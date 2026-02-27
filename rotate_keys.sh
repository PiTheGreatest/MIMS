#!/bin/bash

# --- MIMS Statutory Kay Rotator v1.0 ---
# Purpose: Maintain cryptographic freshness per NDPA 2023 Guidelines.

ENV_FILE=".env"

# 1. Generate a fresh, high-entropy key for the new quarter
NEW_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# 2. Extract the current Primary Key to move it to Secondary
# This ensures existing users aren't logged out immediately (Graceful Logic Rotation)
CURRENT_PRIMARY=$(grep "PRIMARY_SECRET_KEY=" $ENV_FILE | cut -d'=' -f2)

# 3. Update the .env file
# Move Current Primary -> Secondary
sed -i "s|SECONDARY_SECRET_KEY=.*|SECONDARY_SECRET_KEY=$CURRENT_PRIMARY|" $ENV_FILE
# iNJECT nEW kEY -> Primary
sed -i "s|PRIMARY_SECRET_KEY=.*|PRIMARY_SECRET_KEY=$NEW_KEY|" $ENV_FILE

echo "✅ Statutory Key Rotation Complete!"
echo "♻️ Old Primary is now Secondary. New Primary is now active."
echo "🚀 Restart your FASTAPI server to apply changes."



