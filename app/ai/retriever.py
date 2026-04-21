from pgvector.sqlalchemy import Vector
from sqlalchemy import select, text
from sentence_transformers import SentenceTransformer

from app.models import ClinicalLedger

# Load a lightweight model for local embedding or use OpenAI
model = SentenceTransformer('all-MiniLM-L6-v2')

async def get_relevant_history(db_session, patient_id: int, query: str, limit: int = 3):
    # 1. Convert user query to a vector
    query_embedding = model.encode(query)

    # 2. Semantic search in PostgreSQL
    # We find the top N records closest to the query for THIS patient
    stmt = (
        select(ClinicalLedger.note_content)
        .filter(ClinicalLedger.patient_id == patient_id)
        .order_by(ClinicalLedger.embedding.cosine_distance(query_embedding))
        .limit(limit)
    )
    
    results = await db_session.execute(stmt)
    notes = [row[0] for row in results]
    
    return "\n---\n".join(notes)