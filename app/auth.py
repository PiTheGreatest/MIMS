import os
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import Optional, Union
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from app import models, database

load_dotenv()

# --- Configuration & Security Protocols (Finance Act 2025 Standards) ---
PRIMARY_SECRET_KEY = os.getenv("PRIMARY_SECRET_KEY", "fallback_primary_secure_2026")
SECONDARY_SECRET_KEY = os.getenv("SECONDARY_SECRET_KEY") # Optional fallback for rotation
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8  # ⚖️ 8-hour session (Shift-based)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

# --- 1. Password & Token Logic ---

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies evidence (plain password) against the registry (hash)."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """🔐 NDPA 2023 §39: Mandatory encryption of sensitive data."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, PRIMARY_SECRET_KEY, algorithm=ALGORITHM)

# --- 2. The Current User Dependency (The Forensic Anchor) ---

async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(database.get_db)
):
    """
    ⚖️ Implements Graceful Rotation. Fulfills Evidence Act §84 requirement 
    for 'Attribution' by linking every action to a verified identity.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Session invalid or expired.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = None
    try:
        # Try Primary Key first
        try:
            payload = jwt.decode(token, PRIMARY_SECRET_KEY, algorithms=[ALGORITHM])
        except JWTError:
            # 🔄 Fallback to Secondary Key (Rotation Grace Period)
            if SECONDARY_SECRET_KEY:
                payload = jwt.decode(token, SECONDARY_SECRET_KEY, algorithms=[ALGORITHM])
            else:
                raise credentials_exception
    except JWTError:
        raise credentials_exception
            
    # 🕵️ Forensic Check: We use the 'sub' claim (Subject) which should be the Email
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    
    # 🏛️ Multi-Table Registry Lookup (CAMA 2020 Compliance)
    # 1. Check if user is an Admin (Corporate)
    user = db.query(models.Admin).filter(models.Admin.email == email).first()
    
    # 2. If not an Admin, check if they are a Doctor (Clinical)
    if not user:
        user = db.query(models.Doctor).filter(models.Doctor.email == email).first()
        
    if user is None:
        raise credentials_exception
        
    return user

# --- 3. JURISDICTIONAL ACCESS CONTROL ---

def allow_clinical(current_user = Depends(get_current_user)):
    """
    Ensures 'Clinical Standing' under the Medical and Dental Practitioners Act.
    """
    # Check if the user is specifically a Doctor record
    if not isinstance(current_user, models.Doctor):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User lacks MDCN Clinical Standing for this operation."
        )
    return current_user

def allow_admin(current_user = Depends(get_current_user)):
    """
    Enforces Corporate Governance for Administrative tasks.
    """
    # Checks if user has the 'role' attribute (Admin model)
    role = getattr(current_user, "role", None)
    if role not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrative clearance (CAMA/NTA) required."
        )
    return current_user