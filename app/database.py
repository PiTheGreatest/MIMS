import os
import logging
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv

# Load the "Statutory Environment"
load_dotenv()

# 1. Credential Mapping (Synchronized with your .env)
# We use the POSTGRES_ keys to match Docker's internal registry requirements
# Use None as a default to force the system to crash if .env is missing.
# This is a "Safety Interlock" for your protection.
DB_USER = os.getenv("POSTGRES_USER")
DB_PASS = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB")
DB_HOST = os.getenv("DB_HOST", "db") 
DB_PORT = os.getenv('DB_PORT', "5432")

if not all([DB_USER, DB_PASS, DB_NAME, DB_PORT]):
    raise ImportError("CRITICAL: MIMS Statutory Environment Variables are missing!")

# 2. Build the "Statutory Connection String"
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 3. The Engine (Evidence Act §84 Reliability Protocol)
# pool_pre_ping=True: Validates the "Witness" before taking "Evidence"
engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True,
    echo=False  # Set to True if you need to see raw SQL "Transcripts"
)

# 4. The Session (The Court Clerk handling daily records)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 5. The Base (The Digital Constitution)
# Using the modern SQLAlchemy 2.0 DeclarativeBase
class Base(DeclarativeBase):
    pass

# 6. The Enactment Clause (Table Creation)
def init_db():
    """
    Formally enacts the database schema.
    This creates all tables defined in models.py.
    """
    try:
        # Local import to prevent Circular Import Disputes
        from app import models
        Base.metadata.create_all(bind=engine)
        logging.info("MIMS: Database Registry successfully enacted.")
    except Exception as e:
        logging.error(f"MIMS: Statutory Enactment Failed: {e}")
        raise e

# 7. The Public Notary (FastAPI Dependency)
def get_db() -> Generator:
    """
    Yields a database session for a single 'Clinical Encounter' (Request).
    Ensures the session is closed afterward (NDPA Compliance).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()