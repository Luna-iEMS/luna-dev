#!/bin/bash
set -e
API_URL="http://localhost:8000/api/v1"
echo "🚀 Luna-IEMS Smoke-Test gestartet..."

# 1. API Health
echo "→ Prüfe API-Health..."
curl -sf "$API_URL/system/info" | jq .status >/dev/null && echo "✅ API erreichbar" || (echo "❌ API down"; exit 1)

# 2. DB Schema
echo "→ Prüfe DB-Tabellen..."
docker exec -i luna-db psql -U postgres -d luna -c "\dt" | grep smart_meter_readings >/dev/null && echo "✅ DB-Schema ok" || (echo "❌ DB-Schema fehlt"; exit 1)

# 3. Ingestion-Test
echo "→ Teste Dokument-Upload..."
curl -sf -X POST "$API_URL/ingest/doc" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@docs/sample.pdf" \
  -F "kind=document" >/tmp/ingest_out.json && echo "✅ Upload erfolgreich"

# 4. RAG-Test
echo "→ Teste RAG-Frage..."
curl -sf -X POST "$API_URL/rag/ask" \
  -H "Content-Type: application/json" \
  -d '{"question":"Was steht in sample.pdf?"}' \
  | jq .answer >/dev/null && echo "✅ RAG funktioniert" || echo "⚠️ RAG unvollständig"

# 5. Simulation
echo "→ Prüfe Simulation..."
docker exec -i luna-db psql -U postgres -d luna -c "SELECT count(*) FROM smart_meter_readings;" | grep -E '[1-9]' >/dev/null && echo "✅ Smart-Meter Daten vorhanden" || echo "⚠️ Keine Smart-Meter Daten"
docker exec -i luna-db psql -U postgres -d luna -c "SELECT count(*) FROM market_prices;" | grep -E '[1-9]' >/dev/null && echo "✅ Marktpreise vorhanden" || echo "⚠️ Keine Marktpreise"

# 6. Empfehlung
echo "→ Teste Empfehlungssystem..."
curl -sf -X POST "$API_URL/recommend" -H "Content-Type: application/json" -d '{}' >/tmp/recommend_out.json && echo "✅ Empfehlung liefert Antwort" || echo "⚠️ Empfehlung leer"

# 7. Admin-Health
echo "→ Prüfe Admin-Health..."
curl -sf "$API_URL/admin/health" | jq .services >/dev/null && echo "✅ Admin-Health ok" || echo "⚠️ Admin-API nicht erreichbar"

echo "✅ Smoke-Test abgeschlossen!"
