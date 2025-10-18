from fastapi import FastAPI
from datetime import datetime
import os

# Import aller Router
from routers import (
    data_smartmeter,
    data_market,
    ingest,
    rag_api,
    recommend
)
# ------------------------------------------------------------------------------
# FastAPI App Definition
# ------------------------------------------------------------------------------
app = FastAPI(
    title="Luna IEMS API",
    version="0.1.0",
    description="Luna Intelligent Energy Management System – API"
)

# ------------------------------------------------------------------------------
# System Info Endpoint
# ------------------------------------------------------------------------------
@app.get("/api/v1/system/info")
def system_info():
    return {
        "status": "ok",
        "service": "luna-api",
        "timestamp": datetime.utcnow().isoformat(),
        "versions": {
            "api": "0.1.0",
            "python": os.sys.version.split()[0],
        },
        "ports": {
            "api": os.getenv("API_PORT"),
            "db": os.getenv("DB_PORT"),
            "qdrant": os.getenv("QDRANT_HTTP"),
            "minio": os.getenv("MINIO_API"),
            "tika": os.getenv("TIKA_PORT"),
        }
    }

# ------------------------------------------------------------------------------
# Root Info
# ------------------------------------------------------------------------------
@app.get("/")
def root():
    return {"message": "Luna IEMS API running. Visit /api/v1/system/info"}

# ------------------------------------------------------------------------------
# Router-Registrierungen
# ------------------------------------------------------------------------------
app.include_router(data_smartmeter.router)
app.include_router(data_market.router)
app.include_router(ingest.router)
app.include_router(rag_api.router)
app.include_router(recommend.router)  # 🆕 Hier wurde dein Recommender aktiviert!

