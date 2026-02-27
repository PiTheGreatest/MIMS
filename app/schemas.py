from __future__ import annotations
from datetime import date, datetime
from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict
from typing import Optional, List, Dict, Any

# --- 1. HOSPITAL & ADMIN SCHEMAS (NTA 2025 Corporate Compliance) ---

class AdminCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str = Field(..., min_length=8) 
    role: str = "admin"
    nin: str = Field(..., pattern=r"^\d{11}$")

class HospitalCreate(BaseModel):
    hospital_name: str
    cac_registration_number: str = Field(..., pattern=r"^(RC|BN)\d+$")
    tin: str = Field(..., description="NTA 2025: Mandatory for NRS E-Invoicing integration")
    address: str
    specialization: str
    # ⚖️ NTA 2025: Companies with turnover > ₦100m are 'Medium/Large' 
    # and subject to the 4% Development Levy.
    company_size: str = Field("Small", pattern="^(Small|Medium|Large)$")
    admin_details: AdminCreate 

# --- 2. DOCTOR SCHEMAS (Professional Accountability) ---

class DoctorCreate(BaseModel):
    full_name: str
    license_number: str = Field(..., description="MDCN License - Required for Clinical Admissibility")
    hospital_id: int
    email: EmailStr
    password: str = Field(..., min_length=8)

# --- 3. PATIENT SCHEMAS (NDPA 2023 & NHIA 2022 VGF Logic) ---

class PatientCreate(BaseModel):
    nin: str = Field(..., pattern=r"^\d{11}$")
    name: str = Field(..., min_length=3)
    phone_number: str = Field(..., pattern=r"^\+234\d{10}$")
    blood_group: str = Field(..., pattern="^(A|B|AB|O)[+-]$")
    nhia_id: Optional[str] = None 
    date_of_birth: date
    is_pregnant: bool = False
    is_indigent: bool = False
    
    # ⚖️ NDPA 2023 §26: Explicit Consent is a 'Condition Precedent' to processing
    data_processing_consent: bool = Field(default=False)
    consent_version: str = "v2026.1"

    @field_validator('data_processing_consent')
    @classmethod
    def must_be_true(cls, v: bool) -> bool:
        if v is False:
            raise ValueError("NDPA 2023: Processing sensitive health data requires explicit consent.")
        return v

# --- 4. CLINICAL & FISCAL SCHEMAS (NRS 2026 E-Invoicing) ---

class BillingBreakdown(BaseModel):
    total_bill: float
    patient_portion: float
    insurance_portion: float
    # 💰 NTA 2025: Medical services are Zero-Rated (0% VAT)
    vat_amount: float = 0.0 
    tax_status: str = Field("ZERO-RATED (NTA 2025 Sch. 1)")
    
    # 🏛️ NRS E-Invoicing metadata
    nrs_irn: Optional[str] = Field(None, description="Invoice Reference Number from NRS MBS")
    flutterwave_ref: Optional[str] = None

class RecordCreate(BaseModel):
    patient_nin: str = Field(..., pattern=r"^\d{11}$")
    doctor_id: int
    diagnosis: str
    base_fee: float = Field(..., gt=0)
    # Categorization for tax deduction eligibility under NTA 2025
    service_type: str = Field(default="medical", pattern="^(medical|pharmaceutical|administrative)$")

class MedicalRecordResponse(BaseModel):
    id: int
    status: str = "Validated & Fiscalized"
    is_paid: bool = False
    billing: BillingBreakdown
    # Cryptographic Stamp Identifier (CSID) required for 2026 compliance
    fiscal_stamp: str = Field(..., description="NRS Cryptographic Stamp")
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)

# --- 5. PAYMENT & WEBHOOK SCHEMAS (Flutterwave Verification) ---

class FlutterwaveWebhook(BaseModel):
    """Schema to handle the 'verif-hash' logic we discussed."""
    event: str
    data: Dict[str, Any]
    # We verify this against settings.FLW_SECRET_HASH

# --- 6. RESPONSE SCHEMAS (The 'Certified True Copies' of Records) ---

class AdminResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str
    model_config = ConfigDict(from_attributes=True)

class HospitalResponse(BaseModel):
    """
    ⚖️ Fixing the AttributeError: This schema provides the 
    official response format for hospital queries.
    """
    id: int
    hospital_name: str
    cac_registration_number: str
    tin: str
    address: str
    specialization: str
    company_size: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class DoctorResponse(BaseModel):
    id: int
    full_name: str
    license_number: str
    hospital_id: int
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)

class PatientResponse(BaseModel):
    id: int
    nin: str
    name: str
    blood_group: str
    is_pregnant: bool
    is_indigent: bool
    # ⚖️ Sensitive data - hidden in basic response per NDPA 2023
    model_config = ConfigDict(from_attributes=True)