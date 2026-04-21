from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.ai.engine import MIMSAiAssistant
from app.core.config import settings
from pydantic import BaseModel

router = APIRouter(prefix="/ai", tags=["AI Engine"])

# Initialize Assistant once with your API key
assistant = MIMSAiAssistant(api_key=settings.OPENAI_API_KEY)

# --- SCHEMAS ---
class SearchRequest(BaseModel):
    query: str

class ConsultationRequest(BaseModel):
    patient_id: int
    doctor_id: int
    user_query: str
    context: str = ""

# --- ENDPOINTS ---

@router.post("/search")
async def public_health_search(payload: SearchRequest):
    """
    🌐 PUBLIC SEARCH ENDPOINT
    Acts as the Gemini/ChatGPT search bar for general health inquiries.
    """
    try:
        response = await assistant.generate_public_search_response(payload.query)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search Engine Error: {str(e)}")

@router.post("/consult")
async def clinical_consultation(payload: ConsultationRequest, db: Session = Depends(get_db)):
    """
    🩺 CLINICAL CONSULTATION ENDPOINT
    Reserved for hospital-side use. Connects to the RAG historical ledger.
    """
    try:
        # Note: In a real flow, you'd verify the doctor_id via JWT here.
        response = await assistant.generate_clinical_response(
            role="doctor", 
            user_query=payload.user_query, 
            context=payload.context
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clinical Engine Error: {str(e)}")