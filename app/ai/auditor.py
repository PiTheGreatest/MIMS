from typing import Dict, Any
from sqlalchemy.orm import Session
from ..models import MedicalRecord, Patient, ClinicalLedger

class MedicalIntegrityAuditor:
    """
    🧠 Clinical-Fiscal Validator: 
    Detects discrepancies between clinical notes and billed insurance tiers.
    """

    @staticmethod
    def check_claim_consistency(record: MedicalRecord, patient: Patient) -> Dict[str, Any]:
        """
        Runs statutory rule-checks for NHIA/HMO compliance.
        """
        flags = []
        score = 1.0  # Integrity score: 1.0 is perfect, < 0.5 is a red flag

        # 1. Statutory Age-Treatment Match (NHIA Compliance)
        age = (record.timestamp.date() - patient.date_of_birth).days // 365
        
        # Flag: Pediatric drugs billed for an adult (or vice-versa)
        if age > 18 and "pediatric" in record.diagnosis.lower():
            flags.append("AGE_DIAGNOSIS_MISMATCH: Adult billed for pediatric care.")
            score -= 0.3

        # 2. VGF Eligibility Audit
        # If billed as Maternal VGF but diagnosis doesn't mention pregnancy
        if record.benefit_tier == "VGF (Maternal)" and not patient.is_pregnant:
            flags.append("VGF_FRAUD_RISK: Maternal tier used for non-pregnant patient.")
            score -= 0.5

        # 3. Upcoding Detection (Semantic Check)
        # In a real RAG setup, we'd use the ledger's embeddings here.
        # Simple example: Billed for 'Major Surgery' but notes say 'Consultation'
        if record.base_fee > 50000 and "consultation" in record.diagnosis.lower():
            flags.append("UPCODING_RISK: High fee for basic consultation.")
            score -= 0.4

        return {
            "integrity_score": round(score, 2),
            "is_suspicious": score < 0.7,
            "flags": flags
        }