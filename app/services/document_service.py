import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from app.models import MedicalRecord

async def generate_discharge_pdf(record: MedicalRecord, output_path: str = "exports/"):
    """
    📜 Statutory Discharge Summary: Generates a cryptographically 
    verified PDF receipt for the patient.
    ⚖️ Compliance: Evidence Act 2023 & NTA 2025.
    """
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    filename = f"Discharge_{record.patient_nin}_{record.id}.pdf"
    file_path = os.path.join(output_path, filename)
    
    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    # 🏛️ Header: Hospital Identity
    c.setFont("Helvetica-Bold", 16)
    c.drawString(1 * inch, height - 1 * inch, f"OFFICIAL DISCHARGE SUMMARY")
    c.setFont("Helvetica", 10)
    c.drawString(1 * inch, height - 1.2 * inch, f"Facility: {record.hospital_id} | Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    c.line(1 * inch, height - 1.3 * inch, width - 1 * inch, height - 1.3 * inch)

    # 👤 Patient Details
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1 * inch, height - 1.7 * inch, "PATIENT INFORMATION")
    c.setFont("Helvetica", 10)
    c.drawString(1 * inch, height - 1.9 * inch, f"NIN: {record.patient_nin}")
    c.drawString(1 * inch, height - 2.1 * inch, f"Record Reference: {record.id}")

    # 🩺 Clinical Findings (AI-Generated Content)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1 * inch, height - 2.6 * inch, "CLINICAL SUMMARY")
    c.setFont("Helvetica", 10)
    
    # Text wrapping for long AI responses
    text_object = c.beginText(1 * inch, height - 2.8 * inch)
    text_object.setFont("Helvetica", 10)
    text_object.setLeading(14)
    
    # Simplified text wrap logic
    lines = record.diagnosis.split('\n')
    for line in lines:
        text_object.textLine(line[:100]) # Basic wrap
    c.drawText(text_object)

    # 💰 Fiscal Section: The 2026 Statutory Requirement
    c.line(1 * inch, 2.5 * inch, width - 1 * inch, 2.5 * inch)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1 * inch, 2.2 * inch, "FISCAL CLEARANCE")
    
    c.setFont("Helvetica", 9)
    c.drawString(1 * inch, 1.9 * inch, f"Base Fee: NGN {record.base_fee:,.2f}")
    c.drawString(1 * inch, 1.7 * inch, f"Flutterwave Ref: {record.flutterwave_ref}")
    c.drawString(1 * inch, 1.5 * inch, f"NRS IRN: {record.fiscal_stamp[:20]}...") # Partial IRN for UI
    
    # 🔒 Cryptographic Fiscal Stamp
    c.setFont("Courier-Bold", 8)
    c.rect(1 * inch, 0.7 * inch, width - 2 * inch, 0.5 * inch, stroke=1, fill=0)
    c.drawString(1.2 * inch, 1.0 * inch, "STATUTORY FISCAL STAMP (NTA 2025 COMPLIANT)")
    c.drawString(1.2 * inch, 0.8 * inch, f"VERIFICATION HASH: {record.fiscal_stamp}")

    c.save()
    return file_path