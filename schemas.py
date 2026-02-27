from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# --- PATIENT SCHEMAS ---
class PatientBase(BaseModel):
    fullname: str
    nin: str = Field(..., min_length=11, max_length=11)      # Nigerian NIN must be 11 digits
    phone: str
    email: Optional[EmailStr] = None

class PatientCreate(PatientBase):
    pass    # Used when registering a new patient

class PatientOut(PatientBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True   # Allows compatibility with SQLAlchemy models

# --- CONSENT SCHEMAS ---
class ConsentRequest(BaseModel):
    patient_id: str
    phone: str
    purpose: str = "TREATMENT"

class ConsentVerify(BaseModel):
    patient_id: str
    phone: str
    otp_code: str
    hospital_id: str

# --- FINANCE/PAYMENT SCHEMAS ---
class PaymentInitiate(BaseModel):
    amount: float
    hospital_id: str
    currency: str = "NGN"