from datetime import date
from typing import Dict, Any
from .models import Patient # Assuming this is the path to your models.py

def verify_nhia_coverage(patient: Patient) -> Dict[str, Any]:
    """
    Adjudicates coverage based on NHIA Act 2022.
    Determines if the patient belongs to the VGF (0% Copay), 
    Formal Sector (10% Copay), or Private HMO (External).
    """
    today = date.today()
    age = today.year - patient.date_of_birth.year - (
        (today.month, today.day) < (patient.date_of_birth.month, patient.date_of_birth.day)
    )

    # 1. PRIVATE INSURANCE (The "Mansard" Route)
    if patient.hmo_id:
        return {
            "status": "ACTIVE",
            "tier": f"Private HMO ({patient.hmo_provider_name})",
            "copay_rate": 0.0, # Handled externally via provider portal
            "is_external": True,
            "provider_name": patient.hmo_provider_name
        }

    # 2. VULNERABLE GROUP FUND (0% Copay - Statutory Free Care)
    # NHIA Section 57: Children < 5, Aged >= 65, Pregnant, and Indigent.
    if age < 5:
        return {"status": "ACTIVE", "tier": "VGF (Pediatric)", "copay_rate": 0.0, "is_external": False}
    
    if age >= 65:
        return {"status": "ACTIVE", "tier": "VGF (Geriatric)", "copay_rate": 0.0, "is_external": False}
    
    if patient.is_pregnant:
        return {"status": "ACTIVE", "tier": "VGF (Maternal)", "copay_rate": 0.0, "is_external": False}
    
    # Indigent check via NSR or manual flag
    if patient.is_indigent or patient.nsr_id:
        return {"status": "ACTIVE", "tier": "VGF (Indigent)", "copay_rate": 0.0, "is_external": False}

    # 3. FORMAL / EQUITY SECTOR (10% Copay - Standard)
    # Employer/State pays 90%, Patient pays 10% via Flutterwave.
    return {
        "status": "ACTIVE", 
        "tier": "Formal/Equity", 
        "copay_rate": 0.10, 
        "is_external": False
    }

def process_billing_logic(base_fee: float, patient: Patient) -> Dict[str, Any]:
    """
    The 'Fiscal Nexus' function. Bridges the Clinical Diagnosis to the Invoice.
    """
    coverage = verify_nhia_coverage(patient)
    copay_rate = coverage["copay_rate"]
    
    patient_payable = round(base_fee * copay_rate, 2)
    insurance_payable = round(base_fee - patient_payable, 2)

    return {
        "base_fee": base_fee,
        "patient_portion": patient_payable,
        "insurance_portion": insurance_payable,
        "benefit_tier": coverage["tier"],
        "is_external": coverage["is_external"],
        "requires_payment": patient_payable > 0 # Triggers Flutterwave in UI
    }