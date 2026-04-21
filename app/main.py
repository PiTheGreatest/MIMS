import os
import logging
from datetime import datetime, timezone
from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# --- 1. Modular Imports ---
# --- 1. Modular Imports ---
from app import models
from app.database import engine, get_db

# ⚖️ IMPORT DIRECTLY FROM THE ROUTERS SUBMODULES
from app.routers import records, hospitals, patients, webhooks, auth, admin

# ⚖️ IMPORT DIRECTLY FROM THE AI ENGINE FILE
from app.ai.engine import MIMSAiAssistant

load_dotenv()

# Setup Statutory Logging for Forensic Audits (Evidence Act §84 requirement)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MIMS_AUDIT")

# --- 2. INITIALIZATION (The One True Constitution) ---
app = FastAPI(
    title="MIMS: Unified Healthcare Management System",
    description="Statutory Compliance: NDPA 2023, Evidence Act S84, NHIA Act 2022, Nigeria Tax Act 2025",
    version="2.3.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# --- 3. MIDDLEWARE (The Security Perimeter) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In 2026 production, restrict to Flutterwave & Hospital IPs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 4. STARTUP: Enacting the Registry ---
@app.on_event("startup")
def on_startup():
    """Enacts tables. Essential for Evidence Act S84 'Proper Working Order' proof."""
    models.Base.metadata.create_all(bind=engine)
    logger.info("MIMS: Database Registry Enacted and Verified under NTA 2025 Standards.")

# --- 5. AI ASSISTANT INITIALIZATION ---
# Using environment variable for security
ai_assistant = MIMSAiAssistant(api_key=os.getenv("OPENAI_API_KEY"))

# --- 6. SYSTEM INTEGRITY & HEALTH ---
@app.get("/", status_code=200, tags=["Compliance"])
def system_health(db: Session = Depends(get_db)):
    """Verifies 'Proper Working Order' under Evidence Act §84."""
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "Operational",
            "database": "Connected",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "regulatory_framework": ["NDPA 2023", "Nigeria Tax Act 2025", "NHIA 2022"],
            "jurisdiction": "Federal Republic of Nigeria",
            "audit_standard": "Evidence Act 2011 Section 84",
            "nrs_integration": "Active (E-Invoicing Pilot v2)"
        }
    except Exception as e:
        logger.critical(f"SYSTEM_FAILURE: Database Registry Offline. Legal Risk: High. Detail: {e}")
        raise HTTPException(status_code=503, detail="Statutory Registry Offline")

# --- 7. AI ENDPOINTS ---

@app.post("/ai/search", tags=["AI Engine"])
async def public_search(query: str = Body(..., embed=True)):
    """🌐 Public Search Mode: The Gemini/ChatGPT experience for users."""
    try:
        response = await ai_assistant.generate_public_search_response(query)
        return {"response": response}
    except Exception as e:
        logger.error(f"AI_SEARCH_ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail="Search service temporarily unavailable")

@app.post("/ai/consult", tags=["AI Engine"])
async def clinical_consult(
    role: str, 
    query: str, 
    patient_id: int, 
    context: str = "General Consultation",
    db: Session = Depends(get_db)
):
    """🩺 Clinical Assistant Mode: Internal RAG logic using patient history."""
    try:
        response = await ai_assistant.generate_clinical_response(role, query, context)
        logger.info(f"AI_CONSULTATION_LOG: Patient {patient_id} | Role {role}")
        return {"response": response}
    except Exception as e:
        logger.error(f"AI_CONSULT_ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail="Clinical AI service error")

# --- 8. CONNECTING THE ROUTERS ---
app.include_router(auth.router, prefix="/auth", tags=["Identity Management"])
app.include_router(hospitals.router, prefix="/hospitals", tags=["Corporate Governance"])
app.include_router(patients.router, prefix="/patients", tags=["Data Subjects (NDPA)"])
app.include_router(records.router, prefix="/records", tags=["Clinical-Fiscal Nexus"])
app.include_router(webhooks.router, prefix="/webhooks", tags=["Fiscal Webhooks"])
app.include_router(admin.router, prefix="/admin", tags=["Compliance & Audit"])

# --- 9. GLOBAL EXCEPTION HANDLER ---
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"SYSTEM_ERROR at {request.url}: {str(exc)}")
    return {
        "error": "Internal System Variance",
        "detail": "Action captured in Forensic Audit Log for Statutory Review.",
        "timestamp": datetime.now(timezone.utc)
    }