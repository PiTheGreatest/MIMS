from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app import models

class HospitalChecker:
    """
    Verifies the Hospital Entity's statutory standing.
    Ensures 'Tenant Isolation' per NDPA 2023 S24.
    """
    def __init__(self, required_feature: str = None):
        self.required_feature = required_feature

    def __call__(self, x_hospital_id: str = Header(...), db: Session = Depends(get_db)):
        # 1. Verify Hospital Existence & License Status
        hospital = db.query(models.HospitalBranch).filter(models.HospitalBranch.id == x_hospital_id, models.HospitalBranch.is_active == True).first()
        if not hospital:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Hospital Entity not recognized or license suspended."
            )
        
        # 2. Check for Specific Federation Features (e.g., 'cross-sync')
        if self.required_feature and self.required_feature not in hospital.enabled_features:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This hospital is not authorized for: {self.required_feature}"
            )
        return hospital
        
