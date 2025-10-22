#!/bin/bash
set -e

LOG_DIR="/app/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/update.log"

echo "🧩 Starte wöchentlichen Luna-IEMS Update-Check..." | tee -a "$LOG_FILE"
date | tee -a "$LOG_FILE"

# =====================================================
# 🔹 1. Internet-Check
# =====================================================
if ! ping -c1 -W2 8.8.8.8 >/dev/null 2>&1; then
  echo "⚠️ Keine Internetverbindung – überspringe Updates." | tee -a "$LOG_FILE"
  exit 0
fi

# =====================================================
# 🔹 2. Update Ollama-Modelle
# =====================================================
REQUIRED_MODELS="${REQUIRED_MODELS:-llama3.1:8b nomic-embed-text}"

echo "🔍 Prüfe Ollama-Modelle..." | tee -a "$LOG_FILE"
INSTALLED_MODELS=$(ollama list | awk '{print $1}' | tail -n +2)

for MODEL in $REQUIRED_MODELS; do
  if echo "$INSTALLED_MODELS" | grep -q "^${MODEL}$"; then
    echo "🔁 Aktualisiere Modell '$MODEL' ..." | tee -a "$LOG_FILE"
    ollama pull "$MODEL" | tee -a "$LOG_FILE"
  else
    echo "⬇️ Lade neues Modell '$MODEL' ..." | tee -a "$LOG_FILE"
    ollama pull "$MODEL" | tee -a "$LOG_FILE"
  fi
done

# =====================================================
# 🔹 3. Update Docker-Images
# =====================================================
echo "🐳 Prüfe Container-Images auf Updates..." | tee -a "$LOG_FILE"
docker compose pull | tee -a "$LOG_FILE"

# =====================================================
# 🔹 4. Update Python Dependencies (nur wenn API/Worker laufen)
# =====================================================
if [ -f "/app/requirements.txt" ]; then
  echo "📦 Prüfe Python-Dependencies..." | tee -a "$LOG_FILE"
  pip install --upgrade -r /app/requirements.txt | tee -a "$LOG_FILE"
fi

# =====================================================
# 🔹 5. Optional: Qdrant Snapshot
# =====================================================
SNAPSHOT_DIR="/app/data/backups"
mkdir -p "$SNAPSHOT_DIR"
echo "💾 Erstelle Qdrant-Snapshot (optional)..." | tee -a "$LOG_FILE"
curl -s -X POST http://qdrant:6333/snapshots | tee -a "$LOG_FILE" || echo "⚠️ Qdrant Snapshot fehlgeschlagen"

echo "✅ Update abgeschlossen am $(date)" | tee -a "$LOG_FILE"
echo "──────────────────────────────" | tee -a "$LOG_FILE"
