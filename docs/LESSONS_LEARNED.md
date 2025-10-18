# 🧠 Lessons Learned – Luna IEMS Setup

## 1. Docker & Compose
- ❌ Fehler: `no such service: luna-api`  
  ✅ Ursache: falsches Verzeichnis (`api/` statt Projektroot).  
  💡 Lösung: Immer im Projekt-Root `~/iems-luna` arbeiten.

- ❌ Fehler: Container unhealthy (`qdrant`, `tika`, `ollama`)  
  ✅ Ursache: falsche Healthcheck-URLs.  
  💡 Lösung: Healthchecks auf Ports (`nc -z`) statt HTTP-Endpunkte.

- ❌ Fehler: Worker startet nicht (`FileNotFoundError`)  
  ✅ Ursache: Pfadbruch nach Verschieben in `api/worker/`.  
  💡 Lösung: Pfade mit `Path(__file__).resolve().parent` dynamisch machen.

## 2. Python & Worker
- ❌ Fehler: `launch_simulations.py` fand Simulationsskripte nicht  
  ✅ Ursache: relative Pfade.  
  💡 Lösung: absolute Pfade im Code verwenden.

- 💡 Worker-Logs regelmäßig prüfen: `docker logs -f luna-worker`

## 3. Datenbank
- ❌ Fehler: `relation "readings" does not exist`  
  ✅ Ursache: Tabelle heißt `smart_meter_readings` und `market_prices`.  
  💡 Lösung: Tabellen prüfen mit `\dt` im psql.

## 4. Git & Struktur
- 📁 Struktur jetzt:
iems-luna/
├── api/
│ └── worker/
│ ├── launch_simulations.py
│ ├── sim_smartmeter.py
│ ├── sim_market.py
├── docker-compose.dev.yml
├── Dockerfile.dev
└── LESSONS_LEARNED.md


## 5. Next Steps
- 🔄 Automatisiertes Startskript (`start.sh`)
- 📈 Monitoring via Grafana / pgAdmin
- 📦 Deployment auf Remote (z. B. EC2 oder Hetzner VM)
