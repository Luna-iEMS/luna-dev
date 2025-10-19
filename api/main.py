from fastapi import FastAPI
from datetime import datetime
import os
import sys
from pathlib import Path

# --- 🔧 Pfadfix für Docker ---
sys.path.append(str(Path(__file__).resolve().parent))

app = FastAPI(
    title="Luna IEMS API",
    version="0.4.0",
    description="Luna Intelligent Energy Management System – Backend API (M4: Empfehlungssystem)",
)

app.router.redirect_slashes = False

# ------------------------------------------------------------------------------
# 🔗 Router-Importe
# ------------------------------------------------------------------------------
from routers import (
    data_smartmeter,
    data_market,
    ingest,
    rag_api,
    recommend,
)

# ------------------------------------------------------------------------------
# 🧩 System Info Endpoint
# ------------------------------------------------------------------------------
@app.get("/api/v1/system/info")
def system_info():
    return {
        "status": "ok",
        "service": "luna-api",
        "timestamp": datetime.utcnow().isoformat(),
        "versions": {
            "api": "0.4.0",
            "python": os.sys.version.split()[0],
        },
        "ports": {
            "api": os.getenv("API_PORT", "8000"),
            "db": os.getenv("DB_PORT", "5432"),
            "qdrant": os.getenv("QDRANT_HTTP", "6333"),
            "minio": os.getenv("MINIO_API", "9000"),
            "tika": os.getenv("TIKA_PORT", "9998"),
            "ollama": os.getenv("OLLAMA_PORT", "11434"),
        },
    }

# ------------------------------------------------------------------------------
# 🏁 Root Endpoint
# ------------------------------------------------------------------------------
@app.get("/")
def root():
    return {
        "message": "🌙 Luna IEMS API läuft.",
        "docs": "/docs",
        "info": "/api/v1/system/info",
    }

# ------------------------------------------------------------------------------
# 🔌 Router-Registrierungen
# ------------------------------------------------------------------------------
app.include_router(data_smartmeter.router)
app.include_router(data_market.router)
app.include_router(ingest.router)
app.include_router(rag_api.router)
app.include_router(recommend.router)

# ------------------------------------------------------------------------------
# ✅ Startup Event
# ------------------------------------------------------------------------------
@app.on_event("startup")
def startup_event():
    print("[Luna IEMS] API-Server gestartet – alle Router aktiv.", flush=True)
