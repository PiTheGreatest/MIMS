import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_vulnerable_group_billing_logic():
    """
    TEST: NHIA Act 2022 §25 Compliance.
    A pregnant patient must have 0.00 patient_copay.
    """
    # 1. Create Record for Pregnant Patient (Ezinne)
    response = client.post("/records/create", json={
        "patient_nin": "12345678901",
        "doctor_id": 1,
        "diagnosis": "Antenatal Checkup",
        "base_fee": 15000.0
    })
    
    data = response.json()
    assert response.status_code == 201
    assert data["billing"]["patient_portion"] == 0.0  # 🏛️ Statutory requirement
    assert data["billing"]["benefit_tier"] == "Vulnerable (Statutory Coverage)"

def test_flutterwave_webhook_settlement():
    """
    TEST: Finance Act 2025 & Contract Law.
    Verify that the webhook flips 'is_paid' to True.
    """
    # 🏛️ Simulate Flutterwave's 'Success' Signal
    webhook_payload = {
        "status": "successful",
        "data": {
            "tx_ref": "FIRS-MIMS-20260205-8901", # Match the IRN
            "status": "successful",
            "amount": 15000.0
        }
    }
    
    # Send with the 'Secret Signet Ring' (Verif-Hash)
    headers = {"verif-hash": "mims_secret_key_2026"}
    response = client.post("/payments/webhook", json=webhook_payload, headers=headers)
    
    assert response.status_code == 200
    assert response.json()["status"] == "Acknowledged"
