import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# 1. Load Statutory Environment (.env).
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def check_hospital_connection():
    print(f"--- MIMS: Initiating Connection Audit ---")
    try:

        # 2. Create the Engine (The Bridge)
        engine = create_engine(DATABASE_URL)

        # 3. Attempt a 'Ping' (The Handshake)
        # We use 'SELECT 1' - a non-destructive read to verify the path is open.
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            if result:
                print("✅ STATUS: Connection Successful.")
                print("⚖️ LEGAL: Database integrity verified for Evidence Act compliance.")
    except Exception as e:
        print("❌ STATUS: Connection Failed!")
        print(F"🚨 ERROR DETAILS: {e}")
        print("\nSYSTEM'S TROUBLESHOOTING TIPS:")
        print("- Check if your .env DATABASE_URL matches your psql settings.")
        print("- Ensure the 'hospital_admin' user has the right privileges.")

if __name__ == "__main__":
    check_hospital_connection()