# --- STAGE 1: Builder (The Legislative Assembly) ---
FROM python:3.12-slim AS builder

WORKDIR /build

# Install compilers and headers (Required for pgvector, psycopg2, and forensic tools)
# ⚖️ Added g++ and python3-dev for C-extension compilation integrity
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    g++ \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# ⚖️ We install to a specific prefix to make the 'Transfer of Assets' clean
# This stage now handles reportlab, httpx, and pgvector compilation
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# --- STAGE 2: Final (The Secure Hospital Ward) ---
FROM python:3.12-slim

# ⚖️ Statutory Env Vars (Evidence Act §84 & Forensic Integrity)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Optimized pathing for the 'Transfer of Assets'
ENV PATH="/usr/local/bin:${PATH}"

WORKDIR /code

# Install ONLY the runtime library for Postgres (The 'Execution' library)
RUN apt-get update && apt-get install -y libpq5 && rm -rf /var/lib/apt/lists/*

# ⚖️ 1. Create the non-privileged 'Accountable Officer' (NDPA 2023 Standard)
RUN adduser --disabled-password --gecos "" mimsuser

# ⚖️ 2. Transfer Assets (Copy the installed packages from builder)
# We copy the entire installation tree to /usr/local for maximum compatibility
COPY --from=builder /install /usr/local

# ⚖️ 3. Copy source code
COPY . /code/

# ⚖️ 4. Grant Statutory Authority (Permissions)
# Ensures mimsuser can generate PDFs (reportlab) and logs in the /code directory
RUN chown -R mimsuser:mimsuser /code

# ⚖️ 5. Switch to the Restricted User
USER mimsuser

EXPOSE 8000

# ⚖️ 6. The Enactment: Use the module flag to ensure uvicorn is found
# This ensures the 'Statutory Registry' starts in a clean, predictable state
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]