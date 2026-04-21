from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models import MedicalRecord, Patient, Hospital
from datetime import datetime
from ai.auditor import MedicalIntegrityAuditor
from services.payment_service import InsuranceAdjudicator

class ClaimsService:
    """
    ⚖️ Statutory Claims Aggregator: Groups medical encounters for reimbursement.
    Compliant with NHIA Section 26 (VGF) and Section 14 (Private HMOs).
    """

    @staticmethod
    def get_pending_claims_summary(db: Session, hospital_id: int):
        """
        Summarizes what the hospital is owed by various insurance tiers.
        """
        return db.query(
            MedicalRecord.benefit_tier,
            func.sum(MedicalRecord.insurance_portion).label("total_owed"),
            func.count(MedicalRecord.id).label("encounter_count")
        ).filter(
            MedicalRecord.hospital_id == hospital_id,
            MedicalRecord.insurance_portion > 0,
            MedicalRecord.is_paid == True # Ensuring the patient has settled their 10% first
        ).group_by(MedicalRecord.benefit_tier).all()

    @staticmethod
    def generate_nhia_batch_report(db: Session, hospital_id: int, provider_type: str):
        """
        Generates the detailed encounter list for statutory reimbursement.
        """
        query = db.query(MedicalRecord, Patient).join(Patient).filter(
            MedicalRecord.hospital_id == hospital_id,
            MedicalRecord.benefit_tier.ilike(f"%{provider_type}%")
        )
        
        claims = query.all()
        
        # 📝 Legally required fields for NHIA/HMO submission
        report_data = []
        for record, patient in claims:
            report_data.append({
                "Encounter_Date": record.timestamp.strftime("%Y-%m-%d"),
                "Patient_Name": patient.name,
                "NHIA_ID": patient.nhia_id or patient.nsr_id or patient.hmo_id,
                "Diagnosis": record.diagnosis,
                "Treatment_Cost": record.base_fee,
                "Claim_Amount": record.insurance_portion,
                "NIN_Verified": True if patient.nin else False
            })
            
        return report_data
    
def prepare_batch_for_submission(db: Session, records: List[MedicalRecord]):
    for record in records:
        audit_result = MedicalIntegrityAuditor.check_claim_consistency(record, record.patient)
        
        if audit_result["is_suspicious"]:
            # Mark the record for internal review
            record.meta_data["audit_warning"] = audit_result["flags"]
            print(f"🚨 Audit Warning for Record {record.id}: {audit_result['flags']}")