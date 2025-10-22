#!/bin/sh
set -e

log() { printf "%s %s\n" "$(date '+%Y-%m-%d %H:%M:%S')" "$*"; }

# === Ensure curl available ===
if ! command -v curl >/dev/null 2>&1; then
  log "curl nicht gefunden – installiere..."
  apt-get update && apt-get install -y curl >/dev/null
fi

log "🚀 Starte Ollama-Service ..."
ollama serve >/var/log/ollama.log 2>&1 &
OLLAMA_PID=$!

# === Wait for API ===
MAX_ATTEMPTS=30
SLEEP_SECS=2
ATTEMPT=1
log "⏳ Warte auf Ollama API unter http://localhost:11434 ..."
until curl -fsS http://localhost:11434/api/tags >/dev/null 2>&1; do
  if [ "$ATTEMPT" -ge "$MAX_ATTEMPTS" ]; then
    log "❌ Ollama API nach ${MAX_ATTEMPTS} Versuchen nicht erreichbar."
    kill "$OLLAMA_PID" 2>/dev/null || true
    exit 1
  fi
  ATTEMPT=$((ATTEMPT + 1))
  sleep "$SLEEP_SECS"
done
log "✅ Ollama API ist erreichbar."

# === Preload models ===
REQUIRED="${REQUIRED_MODELS:-}"
if [ -n "$REQUIRED" ]; then
  log "⬇️ Lade Modelle: $REQUIRED"
  for MODEL in $REQUIRED; do
    log "   -> pull $MODEL"
    curl -fsS -X POST "http://localhost:11434/api/pull" \
      -H "Content-Type: application/json" \
      -d "{\"model\":\"$MODEL\"}" >/dev/null
  done
  log "✅ Modelle geladen."
else
  log "ℹ️ Keine REQUIRED_MODELS gesetzt."
fi

# === Keep container alive ===
log "👀 Warte auf ollama-Prozess (PID $OLLAMA_PID) ..."
wait "$OLLAMA_PID"