import requests
import time

BASE_URL = "http://localhost:8000"

def run_seeding():
    print("🚀 Initializing MIMS Statutory Registry...")

    # 1. Enact the Hospital (The Data Controller)
    hospital = {
        "hospital_name": "MIMS Federal Medical Centre",
        "cac_registration_number": "RC998877",
        "tin": "12345678-0001",
        "address": "Abuja, FCT",
        "specialization": "General Medicine",
        "admin_details": {
            "full_name": "Dr. Chief Administrator",
            "email": "admin@mims.gov.ng",
            "password": "secure_password_2026",
            "nin": "11122233344"
        }
    }
    h_res = requests.post(f"{BASE_URL}/hospitals/register", json=hospital)
    print(f"Hospital Enrolled: {h_res.status_code}")

    # 2. Enroll the Data Subject (The Patient)
    patient = {
        "nin": "12345678901",
        "name": "Ezinne Flutterwave",
        "phone_number": "+2348012345678",
        "blood_group": "O+",
        "date_of_birth": "1995-05-20",
        "is_pregnant": True,
        "is_indigent": False
    }
    p_res = requests.post(f"{BASE_URL}/patients/register", json=patient)
    print(f"Patient Enrolled: {p_res.status_code}")

    print("\n✅ System Seeded. You can now create Medical Records.")

if __name__ == "__main__":
    run_seeding()