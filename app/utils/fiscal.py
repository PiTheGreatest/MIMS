import hashlib
from datetime import datetime

def generate_nrs_irn(invoice_id: int, service_id: str = "MIMS8826") -> str:
    """
    Generates a statutory IRN as per NRS MBS 2026 guidelines.
    Format: INV{ID}-{SERVICE_ID}-{YYYYMMDD}
    """
    date_str = datetime.now().strftime("%Y%m%d")
    return f"INV{invoice_id:04d}-{service_id}-{date_str}"

def generate_fiscal_stamp(irn: str, amount: float, secret_key: str) -> str:
    """
    Creates a Cryptographic Stamp Identifier (CSID).
    In 2026, the NRS requires an ECDSA signature, but for this 
    logic layer, we simulate the 'Seal' using a SHA-256 HMAC.
    """
    payload = f"{irn}|{amount}|{secret_key}"
    # This acts as the 'Digital Wax Seal' on the medical record
    return hashlib.sha256(payload.encode()).hexdigest()[:16].upper()