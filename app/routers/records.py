from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid
from app import models, schemas, auth, flutterwave_service # Assuming a Flutterwave utility
from app.database import get_db

router = APIRouter(prefix="/records", tags=["Clinical & Billing Registry"])

@router.post("/create", response_model=schemas.MedicalRecordResponse)
async def create_medical_record(
    record_in: schemas.RecordCreate,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_user),
    role = Depends(auth.allow_clinical) # 🩺 Validates MDCN Standing
):
    # 1. 🔍 Verification of 'Standing' (Patient Check)
    patient = db.query(models.Patient).filter(models.Patient.nin == record_in.patient_nin).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Data Subject not found in Registry.")

    # 2. ⚖️ NHIA Act 2022 §25: Vulnerable Group Fund (VGF) Adjudication
    # Logic: If patient is pregnant/indigent, the bill is shifted to the Statutory Fund.
    base_fee = record_in.base_fee
    is_vulnerable = patient.is_pregnant or patient.is_indigent
    
    patient_portion = 0.0 if is_vulnerable else base_fee
    insurance_portion = base_fee if is_vulnerable else 0.0
    benefit_tier = "VGF-SUBSIDIZED" if is_vulnerable else "PRIVATE-RETAINERSHIP"

    # 3. 🧾 NTA 2025: Fiscalization (Zero-Rated Medical Services)
    # Medical services are 0% VAT (Zero-Rated), allowing input tax credit recovery.
    # The 'Fiscal Stamp' below satisfies the NTAA 2025 requirement for unique IRNs.
    fiscal_stamp = f"NRS-MIMS-{uuid.uuid4().hex[:12].upper()}"

    # 4. 🏥 The Forensic Entry (Evidence Act §84)
    # Linking the record to 'current_user.id' establishes the 'Responsible Person' 
    # required for electronic evidence admissibility.
    new_record = models.MedicalRecord(
        patient_nin=record_in.patient_nin,
        doctor_id=current_user.id,
        diagnosis=record_in.diagnosis,
        base_fee=base_fee,
        patient_portion=patient_portion,
        insurance_portion=insurance_portion,
        benefit_tier=benefit_tier,
        fiscal_stamp=fiscal_stamp,
        is_paid=True if is_vulnerable else False # VGF records are 'Paid' by the State
    )

    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    # 5. 💳 Flutterwave Integration (Payment Initialization)
    # If the patient owes a portion, we prepare a Flutterwave transaction.
    payment_link = None
    if patient_portion > 0:
        payment_link = await flutterwave_service.initialize_payment(
            amount=patient_portion,
            email=patient.email, # Ensure patient has an email field
            tx_ref=fiscal_stamp # Use the Fiscal Stamp as the reference for reconciliation
        )

    return {
        **new_record.__dict__,
        "payment_link": payment_link,
        "tax_status": "ZERO-RATED (NTA 2025 Sch. 1)"
    }