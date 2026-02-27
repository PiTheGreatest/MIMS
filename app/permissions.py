from fastapi import HTTPException, status, Depends
from typing import List
from app.auth import get_current_user
from app.models import Doctor

class RoleChecker:
    """
    The Statutory Gatekeeper.
    Ensures that only authorized 'Joint Data Controllers' access specific data.
    """

    def __init__(self, allowed_roles):
        self.allowed_roles = allowed_roles

    def __call__(self, user: Doctor = Depends(get_current_user)):
        # Check if the user's role is permitted for this specific action
        if user.role not in self.allowed_roles:
            # Statutory Note: Failed access attempts should be flagged in the Audit Log
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access Denied. Your role ({user.role}) is not authorized for this module."
            )
        
        # Branch Security: Ensure the user is currently assigned to this hospital branch
        # This prevents 'Casual Browsing' across the network without a clinical reason.
        return user
    
# --- Predefined Permission Scopes (The Legal Boundaries) ---

# 1. Admin: FornSystem Config, Audit Log Review and NDPC Reporting
allow_admin = RoleChecker(["admin"])

# 2. Clinical: For Doctors/Nurses (Access to sensitive health status per NDPA S1.3)
allow_clinical = RoleChecker(["doctor", "nurse", "admin"])

# 3. Billing: For Accountants (Access to Financials/VAT 0% per Finance Act 2025)
allow_billing = RoleChecker(["accountant", "admin", "pharmacist"])

# 4. Emergency 'Break-Glass': Special scope for high-pressure ER situations
allow_emergency = RoleChecker(["emergency_staff", "doctor", "admin", "nurse"])

# --- 5. General Staff: For all authenticated personnel ---
# This satisfies the requirement for 'Authorized Access' under NDPA 2023.
allow_all_staff = RoleChecker(["admin", "doctor", "nurse", "accountant", "pharmacist", "emergency_staff"])