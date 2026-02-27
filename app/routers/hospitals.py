from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models, schemas, auth
from app.database import get_db

router = APIRouter(prefix="/hospitals", tags=["Corporate Governance"])

@router.post("/register", response_model=schemas.HospitalResponse, status_code=status.HTTP_201_CREATED)
def register_hospital(
    hospital_in: schemas.HospitalCreate, 
    db: Session = Depends(get_db)
):
    # 1. 🏛️ Pre-emptive Check (Locus Standi)
    # Check for existing CAC or TIN to prevent duplicate filings
    existing = db.query(models.Hospital).filter(
        (models.Hospital.cac_registration_number == hospital_in.cac_registration_number) |
        (models.Hospital.tin == hospital_in.tin)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Corporate entity (CAC/TIN) already exists in the MIMS Registry."
        )

    # 2. ⚖️ The Transaction Block (Strict Liability)
    try:
        # Create the Hospital Entity
        new_hospital = models.Hospital(
            hospital_name=hospital_in.hospital_name,
            cac_registration_number=hospital_in.cac_registration_number,
            tin=hospital_in.tin,
            address=hospital_in.address,
            specialization=hospital_in.specialization,
            company_size=hospital_in.company_size
        )
        db.add(new_hospital)
        db.flush()  # 💡 Flush gives us the 'new_hospital.id' without committing yet

        # Create the Super Admin (The Accountable Officer)
        # 🔐 NDPA 2023: Passwords MUST be hashed before storage
        hashed_pwd = auth.get_password_hash(hospital_in.admin_details.password)
        
        new_admin = models.Admin(
            full_name=hospital_in.admin_details.full_name,
            email=hospital_in.admin_details.email,
            password=hashed_pwd,
            role="super_admin",
            nin=hospital_in.admin_details.nin,
            hospital_id=new_hospital.id  # Link to the flushed ID
        )
        db.add(new_admin)

        # 3. Final Enactment
        db.commit()
        db.refresh(new_hospital)
        return new_hospital

    except Exception as e:
        db.rollback()  # ⚖️ Revert all changes if any part fails
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registry failure: {str(e)}"
        )

@router.get("/me", response_model=schemas.HospitalResponse)
def get_my_hospital_profile(
    current_user = Depends(auth.get_current_user), 
    db: Session = Depends(get_db)
):
    # 🏥 Cross-Referencing the User to their 'Locus Standi'
    # Whether Admin or Doctor, they must belong to a Hospital
    hospital = db.query(models.Hospital).filter(models.Hospital.id == current_user.hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Associated Hospital entity not found")
    return hospital