from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Dict, Any
from sqlalchemy.orm import Session
from ..models import Patient, MedicalRecord, AuditLog

class InsuranceAdjudicator:
    """
    Expert System for Nigerian Insurance Law Compliance (2026 Update).
    Aligned with NHIA Act 2022 and Nigeria Tax Act 2025 (0% VAT).
    """

    @staticmethod
    def calculate_age(dob: date) -> int:
        today = date.today()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    @staticmethod
    def adjudicate(patient: Patient, base_fee: float) -> Dict[str, Any]:
        age = InsuranceAdjudicator.calculate_age(patient.date_of_birth)
        base = Decimal(str(base_fee))

        # ⚖️ NTA 2025: All medical services are 0% VAT
        tax_info = {"vat_rate": 0.0, "status": "Zero-Rated (NTA 2025 S.187)"}

        # 1. Private HMO Logic (e.g., Mansard)
        if patient.hmo_id:
            return {
                "tier": f"Private HMO ({patient.hmo_provider_name})",
                "patient_portion": Decimal("0.00"),
                "insurance_portion": base,
                "action": "EXTERNAL_HMO_CLAIM",
                "is_paid": False,
                "tax": tax_info
            }

        # 2. VGF Logic (Statutory 100% Free - NHIA Sec 25)
        # 2026 update: Includes refugees and trafficking survivors via NSR_ID
        is_vulnerable = (
            age < 5 or 
            age >= 65 or 
            patient.is_pregnant or 
            patient.is_indigent or 
            patient.nsr_id is not None
        )

        if is_vulnerable:
            return {
                "tier": "VGF (Vulnerable Group Fund)",
                "patient_portion": Decimal("0.00"),
                "insurance_portion": base,
                "action": "VGF_STATUTORY_CLAIM",
                "is_paid": True,
                "tax": tax_info
            }

        # 3. Formal/Equity Sector Logic (90/10 Split)
        # Note: 10% is the 'Statutory Commitment Fee'
        patient_pays = base * Decimal("0.10")
        insurance_pays = base - patient_pays

        return {
            "tier": "Formal/Equity Sector",
            "patient_portion": patient_pays,
            "insurance_portion": insurance_pays,
            "action": "FLUTTERWAVE_COLLECTION",
            "is_paid": False,
            "tax": tax_info
        }

def finalize_medical_record(db: Session, record: MedicalRecord, patient: Patient):
    """
    Applies adjudication and enforces 'Legal Hold' protocols.
    """
    # ⚖️ SAFETY CHECK: Is this record flagged for fraud?
    if record.meta_data.get("status") == "LEGAL_HOLD":
        print(f"🛑 REJECTED: Record {record.id} is under Legal Hold. Cannot finalize billing.")
        return None

    billing = InsuranceAdjudicator.adjudicate(patient, record.base_fee)
    
    record.patient_portion = float(billing["patient_portion"])
    record.insurance_portion = float(billing["insurance_portion"])
    record.is_paid = billing["is_paid"]
    
    # Update meta_data with tax status for FIRS/NRS audits
    new_meta = dict(record.meta_data)
    new_meta["billing_tier"] = billing["tier"]
    new_meta["tax_status"] = billing["tax"]["status"]
    record.meta_data = new_meta
    
    db.commit()
    print(f"⚖️ Finalized: {billing['tier']} (Portion: ₦{record.patient_portion})")
    
    return billing