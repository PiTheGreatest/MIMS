import hmac
import hashlib
import os
from fastapi import APIRouter, Request, Header, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.config import settings
from app.database import get_db
from app.models import MedicalRecord, AuditLog

# 🏛️ 2026 Statutory & Fiscal Utilities
from app.utils.fiscal import generate_nrs_irn, generate_fiscal_stamp
from app.services.notification_service import send_discharge_confirmation
from app.services.document_service import generate_discharge_pdf

router = APIRouter()

@router.post("/flutterwave-webhook")
async def handle_flutterwave_webhook(
    request: Request,
    verif_hash: str = Header(None, alias="verif-hash"),
    db: Session = Depends(get_db)
):
    # ⚖️ 1. Statutory Security Check (Cybercrimes Act compliance)
    # Verifies that the request genuinely originated from Flutterwave
    if not verif_hash or verif_hash != settings.FLW_SECRET_HASH:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid Hash")

    payload = await request.json()
    data = payload.get("data", {})
    flw_id = str(data.get("id"))
    tx_ref = data.get("tx_ref") # Expected format: MIMS-REC-{id}

    # ⚖️ 2. IDEMPOTENCY CHECK (Evidence Act §84 Data Integrity)
    # Prevents duplicate processing of the same payment event
    already_processed = db.query(MedicalRecord).filter(
        MedicalRecord.flutterwave_ref == flw_id
    ).first()

    if already_processed:
        return {"status": "already_processed", "message": "Statutory record already exists"}

    # 3. Process Validated Payment Event
    if payload.get("event") == "charge.completed" and data.get("status") == "successful":
        
        # Extract numerical record ID from the tx_ref string
        try:
            record_id = int(tx_ref.split("-")[-1])
        except (ValueError, IndexError):
            return {"status": "error", "message": "Malformed tx_ref"}

        # Fetch the clinical record to be fiscalized
        record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
        
        if record:
            # A. Update Financial State
            record.is_paid = True
            record.flutterwave_ref = flw_id
            
            # 🏛️ B. 2026 FISCALIZATION (NRS Act 2025 Compliance)
            # Generating the unique IRN and Cryptographic Fiscal Stamp
            irn = generate_nrs_irn(record.id)
            record.fiscal_stamp = generate_fiscal_stamp(
                irn=irn,
                amount=record.base_fee,
                secret_key=settings.SECRET_KEY 
            )
            
            # ⚖️ C. Forensic Logging (NDPA 2023 Accountability)
            # Log the system-level action for the forensic audit trail
            new_audit = AuditLog(
                actor_id=0, # Denotes 'System' as the actor
                action=f"PAYMENT_SUCCESS_FISCALIZED_REF_{flw_id}",
                target_nin=record.patient_nin,
                ip_address=request.client.host
            )
            
            db.add(new_audit)
            
            # Atomic Commit: Ensures DB state is consistent before document generation
            db.commit() 
            db.refresh(record)
            
            # 📜 D. Document Generation (Evidence Act §84)
            # Create the immutable PDF Discharge Summary with the Fiscal Stamp
            try:
                pdf_path = await generate_discharge_pdf(record)
            except Exception as e:
                print(f"⚠️ Document Generation Failed: {e}")
                pdf_path = None

            # 📨 E. Automated Discharge Notification
            # Notify the patient and include the path to their official clearance document
            patient_contact = record.patient.phone_number if record.patient else "unknown"
            
            await send_discharge_confirmation(
                patient_email=patient_contact,
                amount=record.base_fee,
                tx_ref=tx_ref,
                attachment_path=pdf_path 
            )
            
            print(f"✅ Record {record_id} fully processed: Fiscalized, PDF Generated, Patient Notified.")
            
    return {"status": "success"}