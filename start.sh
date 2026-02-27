#!/bin/sh

# ⚖️ EXIT ON ERROR
set -e

echo "🔍 MIMS 2026: Checking Registry Connectivity (DB)..."

# ⚖️ WAIT FOR POSTGRES (The "Condition Precedent")
# We use 'python -m' to bypass PATH issues we saw earlier
while ! python -c "import socket; s = socket.socket(); s.connect(('db', 5432))" 2>/dev/null; do
  echo "⏳ Database is still initializing... sleeping."
  sleep 2
done

echo "✅ Database Registry is ONLINE."

# ⚖️ RUN MIGRATIONS (The "Legislative Update")
echo "📜 Applying Statutory Amendments (Migrations)..."
python -m alembic upgrade head

# ⚖️ START THE SERVER (The "Enactment")
echo "🚀 Starting Clinical Interface (FastAPI)..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000