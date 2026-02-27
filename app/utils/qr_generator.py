import qrcode
import io
import base64
from datetime import datetime
from app.core.config import settings

def generate_nrs_qr_payload(irn: str, certificate_snippet: str) -> str:
    """
    NRS MBS 2026 Requirement: 
    Concatenate IRN with a UNIX timestamp and the hospital's digital certificate.
    """
    unix_timestamp = int(datetime.now().timestamp())
    # Format: IRN.TIMESTAMP|CERTIFICATE
    raw_payload = f"{irn}.{unix_timestamp}|{certificate_snippet}"
    
    # In a production 2026 environment, this payload is typically 
    # Base64 encoded or encrypted using the NRS Public Key.
    return base64.b64encode(raw_payload.encode()).decode()

def create_invoice_qr(irn: str, certificate: str = "CERT-MIMS-2026-X"):
    """
    Generates a QR code image as a Base64 string for embedding in PDFs/Web.
    """
    payload = generate_nrs_qr_payload(irn, certificate)
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(payload)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to a buffer to return as base64 (useful for your FastAPI response)
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()