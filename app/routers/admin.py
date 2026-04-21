from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from ..database import get_db
from ..models import MedicalRecord, AuditLog
from ..ai.auditor import MedicalIntegrityAuditor 

router = APIRouter(
    prefix="/admin",
    tags=["Admin & Compliance"]
)

@router.patch("/hold/{record_id}")
async def place_on_hold(
    record_id: int, 
    reason: str = Body(..., embed=True), 
    db: Session = Depends(get_db)
):
    """
    ⚖️ Statutory Risk Management: 
    Prevents a suspicious claim from being sent to the NHIA Portal.
    """
    # 1. Fetch the record
    record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Medical Record not found")

    # 2. Update status in JSONB meta_data
    current_meta = dict(record.meta_data)
    current_meta["status"] = "LEGAL_HOLD"
    current_meta["hold_reason"] = reason
    current_meta["hold_timestamp"] = datetime.now(timezone.utc).isoformat()
    
    record.meta_data = current_meta
    
    # 3. ⚖️ Forensic Trail: Log the action for Evidence Act Compliance
    new_audit = AuditLog(
        actor_id=1, # In production, replace with the current_user.id from your Auth router
        action="CLAIM_LEGAL_HOLD",
        target_nin=record.patient_nin,
        ip_address="SYSTEM_ADMIN", # Capture real IP in production
        timestamp=datetime.now(timezone.utc)
    )
    db.add(new_audit)
    
    # 4. Commit both the record update and the audit log
    db.commit()
    
    return {
        "message": f"Claim for Record {record_id} held for internal review.",
        "status": "LEGAL_HOLD",
        "audit_ref": new_audit.id
    }