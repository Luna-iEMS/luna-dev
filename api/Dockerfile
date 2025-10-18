FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    bash \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies first (cache-friendly)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy project files (including Alembic + migrations)
COPY . /app

HEALTHCHECK --interval=20s --timeout=5s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/api/v1/system/info || exit 1

CMD bash -c "echo '⏳ Waiting for Postgres to be ready...'; until pg_isready -h \${DB_HOST:-db} -p \${DB_PORT:-5432} -U \${DB_USER:-postgres} > /dev/null 2>&1; do sleep 2; done; echo '✅ Database is ready.'; echo '🚀 Running Alembic migrations...'; alembic -c /app/alembic.ini upgrade head || { echo '❌ Alembic failed'; exit 1; }; echo '✅ Migrations complete. Starting API...'; exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
