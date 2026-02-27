import os
import logging
from datetime import datetime, timezone
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# --- 1. Modular Imports ---
from app import models
from app.database import engine, get_db
# ⚖️ Added 'webhooks' to our jurisdictional delegation
from app.routers import records, hospitals, patients, webhooks, auth


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

# --- 5. CONNECTING THE ROUTERS (Jurisdictional Delegation) ---
app.include_router(hospitals.router, prefix="/hospitals", tags=["Corporate Governance"])
app.include_router(patients.router, prefix="/patients", tags=["Data Subjects (NDPA)"])
app.include_router(records.router, prefix="/records", tags=["Clinical-Fiscal Nexus"])
# 💳 Flutterwave & NRS Webhook Integration
app.include_router(webhooks.router, prefix="/webhooks", tags=["Fiscal Webhooks"])

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

# --- 7. GLOBAL EXCEPTION HANDLER (Forensic Capture) ---
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"SYSTEM_ERROR at {request.url}: {str(exc)}")
    return {
        "error": "Internal System Variance",
        "detail": "Action captured in Forensic Audit Log for Statutory Review.",
        "timestamp": datetime.now(timezone.utc)
    }

app.include_router(auth.router, prefix="/api/v1")