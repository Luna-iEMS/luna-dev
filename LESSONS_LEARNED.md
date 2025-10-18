# 🧠 Lessons Learned – Luna IEMS Setup & Debugging

## 🧭 Überblick

Dieses Dokument fasst die wichtigsten Erkenntnisse und Problembehebungen beim Aufbau und Debugging der **Luna-IEMS Entwicklungsumgebung** zusammen.  
Ziel ist es, den Projektaufbau reproduzierbar und transparent zu halten.

---

## ⚙️ Docker & Compose

### Problem 1 – `no such service: luna-api` / `luna-worker`
**Ursache:** Befehl wurde im falschen Verzeichnis ausgeführt (`api/` statt Projekt-Root).  
**Lösung:**  
```bash
cd ~/iems-luna
docker compose -f docker-compose.dev.yml up -d
Problem 2 – Container unhealthy

Ursache: Healthchecks verwendeten falsche Endpunkte (/healthz, /version).
Lösung:

Healthchecks vereinfacht auf Port-Prüfungen (nc -z localhost <port>).

Längere Startperioden für Qdrant, Tika und Ollama (start_period: 60–120s).

Problem 3 – Dienste starten zu früh

Ursache: Abhängigkeiten waren nicht als condition: service_healthy definiert.
Lösung:
depends_on für API und Worker erweitert, damit DB, Qdrant, Tika, Ollama, MinIO erst „healthy“ sind.

🧩 Worker & Pfadprobleme
Problem 4 – Worker startet nicht (No such file or directory)

Ursache: launch_simulations.py suchte Skripte unter /app/worker/…,
nach Verschieben lagen sie aber in api/worker/.
Lösung:

Pfade mit Path(__file__).resolve().parent dynamisch gemacht.

Aktuelles Arbeitsverzeichnis mit os.chdir(BASE_DIR) gesetzt.

Problem 5 – Market- & SmartMeter-Skripte nicht gefunden

Ursache: relative Pfade im Launcher.
Lösung: absolute Pfade im Code:

BASE_DIR = Path(__file__).resolve().parent
TARGETS = [
    ("SmartMeter", ["python", "-u", str(BASE_DIR / "sim_smartmeter.py")]),
    ("Market", ["python", "-u", str(BASE_DIR / "sim_market.py")]),
]

🗄️ Datenbank & Tabellen
Problem 6 – relation "readings" does not exist

Ursache: Tabellen heißen anders (smart_meter_readings, market_prices).
Lösung: Tabellen mit \dt prüfen, anschließend:

SELECT * FROM smart_meter_readings LIMIT 10;
SELECT * FROM market_prices LIMIT 10;

Problem 7 – Keine Daten sichtbar

Ursache: Worker war im Restart-Loop.
Lösung: Pfade gefixt → Worker startet korrekt → Daten fließen kontinuierlich in DB.

🧰 Infrastruktur & Organisation
Problem 8 – Extra worker/Dockerfile

Ursache: alter Dockerfile im worker/-Ordner war verwirrend.
Lösung: nur Dockerfile.dev verwenden, alter Dockerfile kann gelöscht werden.

Problem 9 – Compose Build-Reihenfolge

Lösung: alle Services bauen mit:

docker compose -f docker-compose.dev.yml build --no-cache
docker compose -f docker-compose.dev.yml up -d

🧾 Struktur & Versionierung
Projektstruktur (Stand Oktober 2025)
iems-luna/
├── api/
│   ├── main.py
│   └── worker/
│       ├── launch_simulations.py
│       ├── sim_smartmeter.py
│       ├── sim_market.py
│       └── config.py
├── docker-compose.dev.yml
├── Dockerfile.dev
├── LESSONS_LEARNED.md
├── README.md
└── requirements.txt

Best Practices

Immer im Projekt-Root arbeiten (~/iems-luna)

Logs gezielt prüfen:

docker logs -f luna-api
docker logs -f luna-worker


Tabellen prüfen:

docker exec -it luna-db psql -U postgres -d luna
\dt

🧩 Zukünftige Verbesserungen

Automatisches Health-Wait-Skript (start.sh)

Integration eines Monitoring-Dashboards (Grafana)

Erweiterte Tests für Worker-Resilience (Restart & Recovery)

Release-Automatisierung (GitHub Actions Tagging)