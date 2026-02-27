# --- STAGE 1: Builder (The Legislative Assembly) ---
FROM python:3.12-slim AS builder

WORKDIR /build

# Install compilers (Required for psycopg2 and other forensic tools)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# ⚖️ We install to a specific prefix to make the 'Transfer of Assets' clean
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# --- STAGE 2: Final (The Secure Hospital Ward) ---
FROM python:3.12-slim

# ⚖️ Statutory Env Vars (Evidence Act §84 & Forensic Integrity)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Ensure Python looks in the new 'install' directory for packages
ENV PYTHONPATH=/usr/local/lib/python3.12/site-packages
ENV PATH="/usr/local/bin:${PATH}"

WORKDIR /code

# Install ONLY the runtime library for Postgres (The 'Execution' library)
RUN apt-get update && apt-get install -y libpq5 && rm -rf /var/lib/apt/lists/*

# ⚖️ 1. Create the non-privileged 'Accountable Officer'
RUN adduser --disabled-password --gecos "" mimsuser

# ⚖️ 2. Transfer Assets (Copy the installed packages from builder)
# We copy from /install in builder to /usr/local in final
COPY --from=builder /install /usr/local

# ⚖️ 3. Copy source code
COPY . /code/

# ⚖️ 4. Grant Statutory Authority (Permissions)
RUN chown -R mimsuser:mimsuser /code

# ⚖️ 5. Switch to the Restricted User (NDPA 2023 Security Standard)
USER mimsuser

EXPOSE 8000

# ⚖️ 6. The Enactment: Use the module flag to ensure uvicorn is found
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]