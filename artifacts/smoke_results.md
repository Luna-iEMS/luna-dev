# 🧪 Luna IEMS Smoke Test Report
**Date:** 2025-10-21T06:55:49.488284+00:00 UTC

| Service | Status | Detail |
|---|---|---|
| FastAPI /health | ✅ OK | 200 → http://localhost:8000/health |
| System Info | ❌ FAIL | 404 → http://localhost:8000/api/v1/system/info |
| Qdrant | ✅ OK | 200 → http://localhost:6333/readyz |
| Tika | ✅ OK | 200 → http://localhost:9998/tika |
| Ollama | ✅ OK | 200 → http://localhost:11434/api/tags |
| RAG /ask | ❌ FAIL | HTTP 200 |

❌ Fehler aufgetreten.
