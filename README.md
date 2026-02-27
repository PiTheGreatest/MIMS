MIMS 2026: Medical Information Management System
Clinical, Fiscal, and Forensic Registry Framework
1. EXECUTIVE SUMMARY
MIMS 2026 is a high-integrity healthcare middleware designed to bridge the gap between clinical operations and the 2026 Nigerian Regulatory Landscape. This system moves beyond simple record-keeping to function as a "Legal Ledger," ensuring every medical encounter is compliant with Data Privacy, Tax Law, and the Rules of Evidence.

2. STATUTORY COMPLIANCE MAP (THE LEGAL THEORY)
A. CORPORATE GOVERNANCE (CAMA 2020 & FINANCE ACT 2025)
Requirement: Every hospital must operate as a verified corporate entity.

Implementation: The hospitals.py module enforces mandatory CAC Registration and Tax Identification Number (TIN) validation.

Effect: Prevents the entry of "Shadow Entities" into the national health registry, ensuring all participants have the "Locus Standi" to practice and bill.

B. DATA PRIVACY & PROTECTION (NDPA 2023)
Requirement: Strict protection of "Sensitive Personal Data" (Health records, NIN, Bio-data).

Implementation: 1. Consent Gate: patients.py implements a hard check for data_processing_consent.
2. Access Control: auth.py utilizes JWT with Graceful Rotation to ensure only authorized "Data Controllers" (Admins) and "Data Processors" (Doctors) can access records.

Effect: Minimizes "Strict Liability" for the hospital under the Nigeria Data Protection Commission (NDPC) audit standards.

C. FORENSIC INTEGRITY (EVIDENCE ACT 2011 §84)
Requirement: Computer-generated statements must be admissible in court.

Implementation: Every record and payment is linked to:

Actor Attribution: The specific Doctor/Admin ID.

Chronological Integrity: Server-side UTC Timestamps.

Spatial Validation: Originating IP Address logging in the AuditLog.

Effect: Establishes the "Chain of Custody" required for electronic evidence to be deemed reliable under Section 84 of the Evidence Act.

D. FISCAL REGULARIZATION (NTA 2025 & NRS STANDARDS)
Requirement: Real-time e-invoicing and differentiated tax treatment.

Implementation: The payments.py Statutory Calculator distinguishes between:

Medical Services: Zero-Rated (0% VAT) per NTA 2025 Schedule 1.

Ancillary Items: Standard Rated (7.5% VAT).

Effect: Automates tax compliance, allowing hospitals to reclaim input tax credits while providing transparent billing to the Nigeria Revenue Service (NRS).

3. TECHNICAL ARCHITECTURE
CORE STACK
Backend: FastAPI (Python 3.12+)

Database: PostgreSQL (The Permanent Ledger)

Authentication: JWT (RS256/HS256) with Dual-Key Rotation

Fiscal Gateway: Flutterwave (Integrated via HMAC-SHA256 Webhooks)

DIRECTORY STRUCTURE
/app/models.py: The Statutory Registry (Schema Definitions)

/app/auth.py: The Digital Gatekeeper (Security Protocols)

/app/payments.py: The Fiscal Clearing House (Tax & Billing)

/app/records.py: The Clinical Ledger (Medical & Forensic Records)

4. DEPLOYMENT PROTOCOL
ENVIRONMENT VARIABLES (.env)
PRIMARY_SECRET_KEY: Main JWT Signature

SECONDARY_SECRET_KEY: Rotation Fallback Key

FLW_SECRET_KEY: Flutterwave Authorization

FLW_SECRET_HASH: Webhook Verification (HMAC Seal)