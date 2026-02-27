from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models, schemas, auth, hospital_auth
from app.database import get_db

router = APIRouter(prefix="/patients", tags=["Patient Management"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_patient(
    patient_in: schemas.PatientCreate,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_user),
    role = Depends(auth.allow_clinical),     # 🩺 MDCN Standing check
    hospital = Depends(hospital_auth.HospitalChecker(required_feature="cross-sync"))
):
    # 1. ⚖️ Evidence Act 2011 §84: Verification of 'Existing Records'
    # We must ensure no duplicate filing to maintain the integrity of the registry.
    db_patient = db.query(models.Patient).filter(models.Patient.nin == patient_in.nin).first()
    if db_patient:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Patient with this NIN already registered in the MIMS Registry."
        )
    
    # 2. 🛡️ NDPA 2023 §26: The 'Consent' Injunction
    # Processing sensitive health data without explicit consent is a 'Strict Liability' offense.
    if not patient_in.data_processing_consent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="NDPA 2023: Explicit digital consent is a condition precedent for health data processing."
        )

    # 3. 📝 Enrollment into the Registry
    new_patient = models.Patient(   
        nin=patient_in.nin,
        name=patient_in.name,
        blood_group=patient_in.blood_group,
        nhia_id=patient_in.nhia_id,
        date_of_birth=patient_in.date_of_birth,
        is_pregnant=patient_in.is_pregnant,
        is_indigent=patient_in.is_indigent,
        # ⚖️ NDPA Audit Trail: Linking the action to the 'Forensic Anchor' (Doctor)
        last_updated_by=current_user.id,
        consent_timestamp=patient_in.consent_version # Track which policy they signed
    )

    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)

    return {
        "status": "Registration Confirmed",
        "patient_id": new_patient.id,
        "nhia_status": "Vulnerable Group Fund Eligible" if (new_patient.is_indigent or new_patient.is_pregnant) else "Standard"
    }