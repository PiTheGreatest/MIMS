from datetime import date
from typing import Dict, Any

def verify_nhia_coverage(patient: Any) -> Dict[str, Any]:
    """
    Adjudicates coverage based on the NHIA Act 2022 Vulnerable Group Fund (VGF).
    Sections 25 & 26: Equity for the vulnerable.
    """
    today = date.today()
    # Calculate Age
    age = today.year - patient.date_of_birth.year - (
        (today.month, today.day) < (patient.date_of_birth.month, patient.date_of_birth.day)
    )

    # 1. THE GOLD TIER (0% Copay - Statutory Exemptions)
    if age < 5:
        return {"status": "ACTIVE", "tier": "Vulnerable (Child)", "copay_rate": 0.0}
    
    if age >= 70:
        return {"status": "ACTIVE", "tier": "Vulnerable (Elderly)", "copay_rate": 0.0}
    
    if patient.is_pregnant:
        return {"status": "ACTIVE", "tier": "Vulnerable (Maternal)", "copay_rate": 0.0}
    
    if patient.is_indigent:
        return {"status": "ACTIVE", "tier": "Vulnerable (Indigent)", "copay_rate": 0.0}

    # 2. THE STANDARD TIER (10% Copay - Formal Sector)
    return {"status": "ACTIVE", "tier": "Formal Sector", "copay_rate": 0.10}

def apply_insurance_to_bill(base_fee: float, coverage_data: Dict[str, Any]) -> Dict[str, float]:
    copay_rate = coverage_data.get("copay_rate", 0.10)
    patient_portion = base_fee * copay_rate
    
    return {
        "total_bill": base_fee,
        "patient_portion": round(patient_portion, 2),
        "insurance_portion": round(base_fee - patient_portion, 2),
        "benefit_tier": coverage_data["tier"]
    }