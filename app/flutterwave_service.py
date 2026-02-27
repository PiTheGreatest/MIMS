import os
import httpx
from fastapi import HTTPException

# ⚖️ NTA 2025: All financial transactions must have a unique reference
FLW_SECRET_KEY = os.getenv("FLW_SECRET_KEY")
FLW_BASE_URL = "https://api.flutterwave.com/v3"

async def initialize_payment(amount: float, email: str, tx_ref: str):
    """
    ⚖️ Initiates a 'Writ of Payment' via Flutterwave.
    """
    headers = {
        "Authorization": f"Bearer {FLW_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "tx_ref": tx_ref,
        "amount": str(amount),
        "currency": "NGN",
        "redirect_url": "https://your-mims-app.com/api/v1/payments/callback",
        "customer": {
            "email": email
        },
        "customizations": {
            "title": "MIMS Medical Billing",
            "description": "Zero-Rated Medical Service (NTA 2025)"
        }
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{FLW_BASE_URL}/payments", json=payload, headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Flutterwave Gateway Error")
        
        data = response.json()
        return data["data"]["link"] # The URL where the patient pays