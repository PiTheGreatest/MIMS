from typing import List
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import ClinicalLedger, MedicalRecord
from app.database import SessionLocal
from app.services.payment_service import generate_flutterwave_link

def get_relevant_history(query_embedding: List[float], limit: int = 5) -> List[ClinicalLedger]:
    """
    🔍 Semantic Similarity Search: Finds relevant historical notes using pgvector.
    ⚖️ Statutory Goal: Evidence-based clinical support as per NHIA quality guidelines.
    """
    with SessionLocal() as session:
        # Using COSINE_DISTANCE (<=>) to find closest matches in 1536-dim space
        statement = (
            select(ClinicalLedger)
            .order_by(ClinicalLedger.embedding.cosine_distance(query_embedding))
            .limit(limit)
        )
        results = session.execute(statement).scalars().all()
        return results

async def process_clinical_workflow(db: Session, patient_id: int, ai_response: str, hospital_base_fee: float = 5000.0):
    """
    ⚖️ Workflow Orchestrator: Links Clinical AI output to Fiscal Actions.
    Automatically triggers Flutterwave billing if a 'Discharge' is detected.
    """
    final_output = ai_response
    
    # 1. Statutory Trigger: Detecting the clinical intent to discharge
    if "discharge" in ai_response.lower():
        try:
            # 2. Fiscal Execution: Generate Flutterwave Payment Link
            # This ensures compliance with the Nigeria Finance Act regarding e-invoicing
            payment_link = await generate_flutterwave_link(
                patient_id=patient_id, 
                amount=hospital_base_fee
            )
            
            # 3. Append Official Statutory Notice to the AI output
            final_output += (
                f"\n\n--- STATUTORY BILLING NOTICE ---\n"
                f"A clinical discharge has been initiated. To complete the hospital clearance "
                f"and secure your digital records, please use the following secure "
                f"Flutterwave link: {payment_link}"
            )
            
            # 4. Audit Trail: Update the record status if necessary (Optional logic)
            # record = db.query(MedicalRecord).filter(MedicalRecord.id == some_id).first()
            # record.is_paid = False 
            # db.commit()

        except Exception as e:
            # Logging failure to generate link to maintain technical accountability
            final_output += f"\n\n[ERROR] Billing gateway temporarily unavailable. Please visit the accounts department."
            print(f"Payment Link Error: {e}")

    return final_output