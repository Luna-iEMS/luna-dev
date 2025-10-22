from fastapi import FastAPI
from api.routers import ingest, rag_api, recommend, data_market, data_smartmeter, admin, system
from api.services import qdrant

app = FastAPI(title="🌙 Luna IEMS API", version="1.0")

@app.on_event("startup")
def init_services():
    """Initialisiert notwendige Services beim Start."""
    try:
        qdrant.ensure_collection(dim=384)
        print("✅ Qdrant initialisiert")
    except Exception as e:
        print(f"⚠️ Startup-Warnung: {e}")

@app.get("/health")
def health():
    return {"status": "ok"}

# Router registrieren
app.include_router(ingest.router)
app.include_router(rag_api.router)
app.include_router(recommend.router)
app.include_router(data_market.router)
app.include_router(data_smartmeter.router)
app.include_router(admin.router)
app.include_router(system.router)