from sqlalchemy import text
from sqlalchemy.orm import Session
from ..models import ClinicalLedger, MedicalRecord

class ClaimsCortex:
    """
    🧠 Advanced Semantic Auditor: 
    Uses pgvector to detect duplicate medical narratives that look different but mean the same.
    """

    @staticmethod
    def detect_semantic_duplicates(db: Session, new_embedding: list, threshold: float = 0.92):
        """
        ⚖️ Forensic Audit: Searches for similar clinical encounters using Cosine Similarity.
        Threshold 0.92 is standard for 'highly probable' duplicates.
        """
        # We use the <-> operator for Euclidean distance or <=> for Cosine distance in pgvector
        query = text("""
            SELECT record_id, note_content, 1 - (embedding <=> :emb) AS similarity
            FROM clinical_ledger
            WHERE 1 - (embedding <=> :emb) > :threshold
            ORDER BY similarity DESC
            LIMIT 5
        """)
        
        results = db.execute(query, {"emb": str(new_embedding), "threshold": threshold}).fetchall()
        return results

    @staticmethod
    def validate_claim_uniqueness(db: Session, record_id: int, new_note: str, embedding: list):
        """
        ⚖️ Compliance Check: Ensures the hospital isn't 'double-dipping' on a single patient.
        """
        potential_dupes = ClaimsCortex.detect_semantic_duplicates(db, embedding)
        
        if potential_dupes:
            for dupe in potential_dupes:
                # If a similar note exists for the same patient within a short timeframe
                # logic to flag as 'POTENTIAL_FRAUD' or 'REDUNDANT_CLAIM'
                print(f"⚠️ Audit Alert: Potential duplicate found. Similarity: {dupe.similarity}")
                return False
        return True