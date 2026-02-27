from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app import database, models, auth, schemas

router = APIRouter(prefix="/auth", tags=["Registry Access (Login)"])

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(database.get_db)
):
    """
    ⚖️ Unified Entry Point for Admins and Doctors.
    Verifies credentials and issues a 'Statutory Pass' (JWT).
    """
    
    # 1. 🔍 Search the Corporate Registry (Admins)
    user = db.query(models.Admin).filter(models.Admin.email == form_data.username).first()
    
    # 2. 🔍 Search the Clinical Registry (Doctors) if not found in Admins
    if not user:
        user = db.query(models.Doctor).filter(models.Doctor.email == form_data.username).first()

    # 3. ⚖️ Credential Admissibility Check
    if not user or not auth.verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials (Email/Password mismatch).",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 4. 🎫 Issuance of the Access Token
    # We use the Email as the 'sub' (Subject) for consistent identification
    access_token = auth.create_access_token(data={"sub": user.email})

    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "role": getattr(user, "role", "doctor") # Defaults to doctor if no role attribute
    }