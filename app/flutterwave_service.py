import os
import httpx
from fastapi import HTTPException

# ⚖️ NTA 2025: All financial transactions must have a unique reference
FLW_SECRET_KEY = os.getenv("FLW_SECRET_KEY")
FLW_BASE_URL = "https://api.flutterwave.com/v3"

async def initialize_payment(amount: float, email: str, tx_ref: str):
    """
    ⚖️ Initiates a 'Writ of Payment' via Flutterwave.
    Used for the 10% Statutory Co-pay for Formal Sector patients.
    """
    headers = {
        "Authorization": f"Bearer {FLW_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "tx_ref": tx_ref,
        "amount": str(amount),
        "currency": "NGN",
        # Ensure this redirect points to your frontend "Thank You" or "Processing" page
        "redirect_url": "https://your-mims-app.com/payment-confirmation", 
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
            # Better error logging for debugging
            error_data = response.json()
            print(f"❌ FLW Error: {error_data}")
            raise HTTPException(status_code=500, detail="Flutterwave Gateway Error")
        
        data = response.json()
        return data["data"]["link"]

async def verify_transaction(transaction_id: str):
    """
    ⚖️ Secondary Verification: Checks the Flutterwave server directly.
    Necessary for finality in 'Fiscal Audit' reports.
    """
    headers = {
        "Authorization": f"Bearer {FLW_SECRET_KEY}",
    }

    async with httpx.AsyncClient() as client:
        # Note: transaction_id here is the ID returned by FLW, not your tx_ref
        response = await client.get(f"{FLW_BASE_URL}/transactions/{transaction_id}/verify", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        return None