#!/bin/bash

# --- SAFETY SETTINGS ---
# Exit immediately if a command exits with a non-zero status
set -e

echo "---------------------------------------------------------"
echo "🚀 MIMS: Starting Integrated Deployment..."
echo "---------------------------------------------------------"

# 1. System Check & Update
echo "⚙️ Updating system packages..."
sudo apt update && sudo apt upgrade -y

# 2. Build the Integrated Containers
# This links main.py, auth.py and database together
echo "📦 Building Docker images from your modular files..."
docker-compose build

# 3. Launch in the Background
echo "🌐 Bringing the echosystem online..."
docker-compose up -d

# 4. Final Legal Foundation (Database Migrations)
# This creates the tables required for Evidence Act compliance
echo "🗄️ Initializing medical & audit tables..."
docker-compose exec web python -c "from app.database import engine, Base; Base.metadata.create_all(bind=engine)"

echo "----------------------------------------------------------"
echo "✅ DEPLOYMENT COMPLETE"
echo "Your Medic Card System is Live"
echo "Legal Framework: NDPA 2023 & NTA 2025 Active"
echo "----------------------------------------------------------"