from .flutterwave_service import initialize_payment

"""
MIMS: Unified Healthcare Management System
Compliant with NDPA 2023, Evidence Act S84, and NHIA Act 2022.
"""

# 1. Versioning for Audit Trails (Evidence Act §84 requirement)
__version__ = "2.0.0"
__author__ = "Ezinne Priscilla Ngwu"

# 2. Hoisting (Flattening) the API for cleaner imports
# This allows "from app import Patient" instead of "from app.models import Patient"
from .models import (
    Base,
    Doctor,
    Patient,
    MedicalRecord,
    AuditLog
)
from .database import SessionLocal, engine, init_db

# 3. Security: Defining the Public Interface (__all__)
# This strictly limits what is exported, keeping raw credentials hidden.
__all__ = [
    "Base",
    "Doctor",
    "Patient",
    "MedicalRecord",
    "AuditLog",
    "SessionLocal",
    "engine",
    "init_db",
    "__version__"
]

# 4. Global Package Initialization
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MIMS")
logger.info(f"MIMS System v{__version__} initialized with Statutory Security Protocols.")