#!/bin/sh
# Simple healthcheck for Ollama service

set -e

URL="http://localhost:11434/api/tags"

# Prüfen, ob API erreichbar ist
if ! curl -fs "$URL" >/dev/null 2>&1; then
  echo "❌ Ollama API nicht erreichbar"
  exit 1
fi

# Optional: prüfen, ob Modelle registriert sind
MODELS=$(curl -fs "$URL" | grep -Eo '"name":"[^"]+"' || true)

case "$MODELS" in
  *llama3.1*|*nomic-embed-text*)
    echo "✅ Ollama healthy — Modelle gefunden: $MODELS"
    exit 0
    ;;
  *)
    echo "⚠️  Ollama läuft, aber keine Modelle geladen."
    exit 1
    ;;
esac
