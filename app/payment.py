from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app import models, schemas, auth
from app.database import get_db
import uuid
from datetime import datetime, timezone

router = APIRouter(prefix="/payments", tags=["Fiscal & Tax Registry"])

# --- ⚖️ THE STATUTORY CALCULATOR ---
def calculate_tax_compliance(amount: float, service_type: str = "medical"):
    """
    Implements VAT logic based on the Finance Act 2025.
    Medical services = 0% VAT (Zero-Rated/Exempt)
    Non-medical items = 7.5% VAT (Standard Rate)
    """
    service_type = service_type.lower()
    
    if service_type == "medical":
        return {
            "base_amount": amount,
            "vat_rate": 0.0,
            "vat_amount": 0.0,
            "total_with_tax": amount,
            "tax_status": "ZERO-RATED (Finance Act 2025 Sch. 1)"
        }
    
    # 🛑 Standard VAT for retail/luxury items (e.g., Hospital Boutique or VIP Suite upgrades)
    vat_rate = 0.075  # 7.5%
    vat_amount = amount * vat_rate
    
    return {
        "base_amount": amount,
        "vat_rate": vat_rate,
        "vat_amount": round(vat_amount, 2),
        "total_with_tax": round(amount + vat_amount, 2),
        "tax_status": "TAXABLE (Standard VAT Applied)"
    }

@router.post("/process/{record_id}")
async def pay_bill(
    record_id: int,
    request: Request, # 🕵️ Used to capture IP for Evidence Act compliance
    service_type: str = "medical", 
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_user)
):
    # 1. Fetch the Record (The Writ of Debt)
    record = db.query(models.MedicalRecord).filter(models.MedicalRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Medical Record not found in Registry")

    # 2. Apply Finance Act 2025 Tax Logic
    tax_calculation = calculate_tax_compliance(record.patient_portion, service_type)
    
    # 3. 💳 Flutterwave Handshake Simulation
    # In production, this is where you'd call flutterwave_service.initialize_payment
    tx_ref = f"FLW-MIMS-{uuid.uuid4().hex[:8].upper()}"
    
    # 4. Update Database Ledger (The discharge of the lien)
    record.is_paid = True
    record.flutterwave_ref = tx_ref
    
    # 5. 📜 Evidence Act §84: Forensic Audit Entry
    # Links the financial discharge to a specific actor and location
    audit_log = models.AuditLog(
        actor_id=current_user.id,
        action=f"PAYMENT_PROCESSED_{service_type.upper()}",
        target_nin=record.patient_nin,
        ip_address=request.client.host # Captures actual source IP
    )
    
    db.add(audit_log)
    db.commit()

    return {
        "transaction_reference": tx_ref,
        "tax_breakdown": tax_calculation,
        "status": "Statutory Discharge Successful",
        "timestamp": datetime.now(timezone.utc)
    }