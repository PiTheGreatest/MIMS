import hmac
import hashlib
from fastapi import APIRouter, Request, Header, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.config import settings
from app.database import get_db
from app.models import MedicalRecord, AuditLog
# Import our 2026 Fiscal Utilities
from app.utils.fiscal import generate_nrs_irn, generate_fiscal_stamp

router = APIRouter()

@router.post("/flutterwave-webhook")
async def handle_flutterwave_webhook(
    request: Request,
    verif_hash: str = Header(None, alias="verif-hash"),
    db: Session = Depends(get_db)
):
    # ⚖️ 1. Statutory Security Check (Nigeria Cybercrimes Act compliance)
    if not verif_hash or verif_hash != settings.FLW_SECRET_HASH:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid Hash")

    payload = await request.json()
    data = payload.get("data", {})
    flw_id = str(data.get("id"))
    tx_ref = data.get("tx_ref")

    # ⚖️ 2. IDEMPOTENCY CHECK (Evidence Act §84 Data Integrity)
    already_processed = db.query(MedicalRecord).filter(
        MedicalRecord.flutterwave_ref == flw_id
    ).first()

    if already_processed:
        return {"status": "already_processed", "message": "Statutory record already exists"}

    # 3. Process Validated Payment Event
    if payload.get("event") == "charge.completed" and data.get("status") == "successful":
        # We fetch the record using tx_ref (which should be the MedicalRecord.id)
        record = db.query(MedicalRecord).filter(MedicalRecord.id == tx_ref).first()
        
        if record:
            # A. Update Payment Status
            record.is_paid = True
            record.flutterwave_ref = flw_id
            
            # 🏛️ B. 2026 FISCALIZATION (NRS Act 2025 Compliance)
            # We generate the IRN and the Cryptographic Stamp Identifier (CSID)
            irn = generate_nrs_irn(record.id)
            record.fiscal_stamp = generate_fiscal_stamp(
                irn=irn,
                amount=record.base_fee,
                secret_key=settings.PRIMARY_SECRET_KEY
            )
            
            # ⚖️ C. Forensic Logging (NDPA 2023 Accountability)
            new_audit = AuditLog(
                actor_id=0, # System Actor
                action=f"PAYMENT_SUCCESS_FISCALIZED_{flw_id}",
                target_nin=record.patient_nin,
                ip_address=request.client.host
            )
            
            db.add(new_audit)
            db.commit() # Atomic Commit: Payment + Stamp + Audit in one 'Legal Breath'
            
    return {"status": "success"}