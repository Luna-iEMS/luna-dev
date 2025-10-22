#!/bin/sh
set -e

echo "🚀 Starte Ollama Service ..."
ollama serve &

# Gib Ollama kurz Zeit, den Server zu starten
sleep 5

# Liste der benötigten Modelle
REQUIRED_MODELS="${REQUIRED_MODELS:-llama3.1:8b nomic-embed-text}"

echo "🧩 Prüfe installierte Modelle ..."
INSTALLED_MODELS=$(ollama list | awk '{print $1}' | tail -n +2)

for MODEL in $REQUIRED_MODELS; do
  if echo "$INSTALLED_MODELS" | grep -q "^${MODEL}$"; then
    echo "✅ Modell '$MODEL' ist bereits vorhanden."
  else
    echo "⬇️ Lade Modell '$MODEL' ..."
    ollama pull "$MODEL" || {
      echo "⚠️ Fehler beim Laden von '$MODEL'"
      exit 1
    }
  fi
done

echo "✅ Alle Modelle sind bereit. (Cache unter /root/.ollama)"
wait
