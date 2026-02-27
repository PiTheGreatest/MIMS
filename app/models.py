from __future__ import annotations
import datetime
import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy import (
    Column, String, Integer, DateTime, ForeignKey, Date, 
    Text, Boolean, JSON, Float, CheckConstraint, Index
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func

class Base(DeclarativeBase):
    pass

class Admin(Base):
    """
    ⚖️ Corporate Accountability: The 'Responsible Person' for the Hospital entity.
    Required for CAMA 2020 and NTA 2025 compliance.
    """
    __tablename__ = "admins"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hospital_id: Mapped[int] = mapped_column(ForeignKey("hospitals.id"))
    full_name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(50), default="super_admin")
    nin: Mapped[str] = mapped_column(String(20), unique=True) # Personal accountability

class Hospital(Base):
    """The Corporate Entity: Subject to Nigeria Tax Act 2025."""
    __tablename__ = "hospitals"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    public_id: Mapped[str] = mapped_column(String(36), default=lambda: str(uuid.uuid4()), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    facility_code: Mapped[Optional[str]] = mapped_column(String(50), unique=True, index=True)
    
    # 🏛️ Compliance: Corporate & Tax Identity
    cac_number: Mapped[Optional[str]] = mapped_column(String(50)) 
    tin: Mapped[str] = mapped_column(String(50), nullable=False) # Finance Act/NTA 2025: Mandatory
    hospital_category: Mapped[str] = mapped_column(String(20), default="Small") # For Tax Rate Logic
    address: Mapped[str] = mapped_column(Text)
    
    doctors: Mapped[List["Doctor"]] = relationship("Doctor", back_populates="hospital")

class Patient(Base):
    """The Data Subject: Protected under NDPA 2023."""
    __tablename__ = "patients"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    public_id: Mapped[str] = mapped_column(String(36), default=lambda: str(uuid.uuid4()), unique=True, index=True)
    
    # ⚖️ Identity: Evidence Act & NIN Mandatory Use
    nin: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(250))
    phone_number: Mapped[str] = mapped_column(String(20)) 
    date_of_birth: Mapped[datetime.date] = mapped_column(Date, nullable=False) 
    
    # 🩸 Clinical Basics
    blood_group: Mapped[Optional[str]] = mapped_column(String(5))
    address: Mapped[Optional[str]] = mapped_column(String)
    
    # 🔐 NDPA 2023: Informed Consent Record
    data_processing_consent: Mapped[bool] = mapped_column(Boolean, default=False)
    consent_timestamp: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    
    # 🏛️ NHIA Act 2022: Social Security & Vulnerability Flags
    nhia_id: Mapped[Optional[str]] = mapped_column(String(50))    
    is_pregnant: Mapped[bool] = mapped_column(Boolean, default=False)
    is_indigent: Mapped[bool] = mapped_column(Boolean, default=False)

    meta_data: Mapped[dict] = mapped_column(JSON, default={})
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())

    medical_records: Mapped[List["MedicalRecord"]] = relationship("MedicalRecord", back_populates="patient")

    # ⚖️ Statutory Guardrails
    __table_args__ = (
        CheckConstraint('length(nin) >= 11', name='min_nin_length'),
    )

class Doctor(Base):
    __tablename__ = "doctors"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hospital_id: Mapped[int] = mapped_column(ForeignKey("hospitals.id"))
    
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    specialization: Mapped[str] = mapped_column(String(100), index=True)
    license_number: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="doctor") 
    
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())

    hospital: Mapped["Hospital"] = relationship("Hospital", back_populates="doctors")
    records: Mapped[List["MedicalRecord"]] = relationship(back_populates="doctor")
    audit_logs: Mapped[List["AuditLog"]] = relationship(back_populates="actor")

# ... (Keep your imports and Base class)

class MedicalRecord(Base):
    """The Clinical-Fiscal Nexus: Linking Diagnosis to Flutterwave Payments."""
    __tablename__ = "medical_records"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    patient_nin: Mapped[str] = mapped_column(ForeignKey("patients.nin"))
    hospital_id: Mapped[int] = mapped_column(ForeignKey("hospitals.id"))
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id"))

    diagnosis: Mapped[str] = mapped_column(Text)
    clinical_data: Mapped[Dict[str, Any]] = mapped_column(JSON) 
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now(), index=True)

    # 💰 Fiscal Data: Finance Act 2025 & Flutterwave Integration
    base_fee: Mapped[float] = mapped_column(Float, default=0.0)
    patient_portion: Mapped[float] = mapped_column(Float, default=0.0) # Added for NHIA tracking
    insurance_portion: Mapped[float] = mapped_column(Float, default=0.0) # Added for NHIA tracking
    
    flutterwave_ref: Mapped[Optional[str]] = mapped_column(String(100), unique=True)
    is_paid: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # 🏛️ Statutory Fiscal Stamp (NRS/FIRS E-Invoicing)
    fiscal_stamp: Mapped[Optional[str]] = mapped_column(String(100), unique=True)

    patient: Mapped["Patient"] = relationship(back_populates="medical_records")
    doctor: Mapped["Doctor"] = relationship(back_populates="records")

    # ⚖️ Integrity Guardrail: Enforcing the 'Rule of Payment'
    __table_args__ = (
        CheckConstraint(
            "(is_paid = False) OR (is_paid = True AND (flutterwave_ref IS NOT NULL OR insurance_portion > 0))",
            name="check_payment_or_subsidy_on_paid"
        ),
        Index("idx_nin_timestamp", "patient_nin", "timestamp"), # Forensic search optimization
    )

class AuditLog(Base):
    """Forensic Trail: Mandatory for NDPA 2023 Compliance."""
    __tablename__ = "audit_logs"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    actor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id"))
    action: Mapped[str] = mapped_column(String(255))
    target_nin: Mapped[Optional[str]] = mapped_column(String(20))
    ip_address: Mapped[str] = mapped_column(String(45))
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())

    actor: Mapped["Doctor"] = relationship(back_populates="audit_logs")