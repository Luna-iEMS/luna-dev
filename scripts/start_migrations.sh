#!/bin/bash
# Startet alle Alembic-Migrationen beim Containerstart

echo "🚀 Wende Alembic Migrationen an..."
alembic upgrade head

# Jetzt den API-Server starten
echo "✅ Starte FastAPI-Service..."
exec uvicorn api.main:app --host 0.0.0.0 --port 8000 --log-level info --reload
