# Luna‑IEMS – Technische Umsetzung & Architekturvision (Dev Guide)

> Ziel: Eine robuste, lokal/on‑prem lauffähige Plattform mit klar dokumentierter Architektur, reproduzierbaren Umgebungen, stabilen Ports, und einer sauberen Roadmap für Team‑Delivery.

---

## 0. Architektur‑Leitplanken
- **Isolation je Kunde**: eigener Stack (Namespace/Compose‑Projekt, eigene Volumes/DBs, API‑Keys).
- **„Meta‑Learning“ optional**: nur anonymisierte Embeddings/Statistiken werden (später) in einen zentralen Knoten gespiegelt.
- **Infra by Code**: Docker Compose + Makefile + .env (+ Profile/Overlays für dev/test/prod).
- **Observability by default**: Healthchecks, strukturierte Logs, Metriken, Tracing.
- **Fail‑safe**: Idempotente Migrations, Retries/Backoff, Circuit Breaker, Dead‑Letter für Eventing.

---

## 1. Dienste & Technologie‑Auswahl

| Domäne | Tooling | Begründung |
|---|---|---|
| API / Gateway | **FastAPI (Python 3.11)** | schnelles Prototyping, starke Öko, ASGI kompatibel |
| Embeddings & LLM | **Ollama** (lokal), Modelle konfigurierbar | offline, DSGVO‑freundlich |
| Vektorsuche | **Qdrant** | stabil, REST/gRPC, Snapshots |
| Relationale/TimeSeries | **PostgreSQL 15 + TimescaleDB** | SQL + TimeSeries in einem System |
| Files/Objekte | **MinIO** | S3‑kompatibel, lokal betreibbar |
| Streaming/Eventbus | **Redpanda** (Kafka‑API) | leichtgewichtig; optional in MVP |
| Parsing | **Apache Tika** | Extraktion Office/PDF |
| Observability | **Grafana + Prometheus (optional), Loki (Logs)** | Standard‑Stack |
| Admin/Customer UI | **React + Tailwind** (später), vorerst Nginx Platzhalter | schnelle Iteration |

> **Hinweis**: Redpanda & Prometheus können via Compose‑Profile optional zugeschaltet werden (vermeidet unnötige Ports in MVP).

---

## 2. Port‑ & Netzwerk‑Plan (Konfliktfrei)

**Grundsatz**: Alle externen Ports über `.env` steuerbar; Standard‑Range nur als Default. Bei Konflikt: Preflight‑Check blockt `up` und schlägt Alternativen vor.

```ini
# .env (Beispiel, pro Kunde anpassbar)
PROJECT_NAME=luna-iems

# Core
API_PORT=8001
POSTGRES_PORT=8301
REDIS_PORT=8302
QDRANT_HTTP_PORT=6333
QDRANT_GRPC_PORT=6334
MINIO_API_PORT=9000
MINIO_CONSOLE_PORT=9001
OLLAMA_PORT=11434
TIKA_PORT=9998

# Observability (optional)
GRAFANA_PORT=3000
LOKI_PORT=3100
PROMETHEUS_PORT=9090

# Profile Flags
ENABLE_REDPANDA=false
ENABLE_OBSERVABILITY=false
```

**Preflight‑Script (Konzept)**: `scripts/preflight.sh` prüft freie Ports (`ss -ltn`), existierende Volumes/Netze, und bricht mit klarer Fehlermeldung ab.

**Netz**: Ein benanntes Bridge‑Netz `luna-net` (extern), damit bestehende Container (z. B. bereits laufendes Ollama) integrierbar sind.

---

## 3. Compose‑Layout (MVP‑Profile)

- `docker-compose.yml` – Basis (postgres, qdrant, minio, ollama, tika, api)
- `docker-compose.observability.yml` – grafana, loki, promtail
- `docker-compose.redpanda.yml` – redpanda (kafka‑kompatibel)

**Healthchecks**: Jeder Dienst mit pragmatischem Check (HTTP 200 o. CLI `ping`), `depends_on: condition: service_healthy` nur wo sinnvoll.

**Ressourcen**: `deploy.resources.limits` für Qdrant/Ollama/Postgres (CPU/Memory), damit Dev‑Kisten nicht in Swap laufen.

---

## 4. Datenmodell & Migrationen

### 4.1 Relationale Basistabellen
- `users` (UUID, external_id)
- `items` (Dokument‑Metadaten)
- `item_chunks` (Text‑Chunks, Verknüpfung zu Qdrant Punkt‑IDs)
- `events` (Interaktionen; Hypertable via Timescale)
- `labels` (Feedback/Rewards)
- `smart_meter_readings` (Hypertable)
- `market_prices` (Hypertable)

**Migrations**: `migrations/001_init.sql` (idempotent), ausgeführt via `scripts/apply_migrations.py` beim API‑Start (nur wenn `APPLY_MIGRATIONS=true`).

### 4.2 Vektor‑Collection
- Qdrant‑Collection `chunks` (COSINE, dimension = embedding size)
- Payload: `{ item_id, chunk_idx, ts, tags }`
- Snapshots: regelmäßige Backups in `./backups/qdrant`

---

## 5. API‑Schnittstellen (MVP)

**Ingest**
- `POST /ingest/doc` – File Upload → Tika‑Extraktion → Chunking → Embeddings → Qdrant + Metadaten in Postgres
- `POST /ingest/text` – Plaintext → wie oben

**RAG**
- `POST /rag/ask` – Frage → Embedding → Qdrant → Kontext → LLM → Antwort + genutzte Chunks

**Simulation (Phase 3)**
- `POST /sim/meter/generate` – Smart‑Meter‑Synthese (Parameter: Skalen/Rauschen)
- `POST /sim/market/generate` – Marktpreise‑Synthese

**Admin**
- `GET /health` – Aggregierter Healthcheck
- `GET /metrics` – Prometheus‑Metriken (optional)

> **Kontrakte** werden als OpenAPI exportiert (FastAPI `/docs`) und versioniert (`/openapi.json`).

---

## 6. Daten‑Pipelines (Phase 3)

**Simulatoren**
- Python Jobs erzeugen Messwerte/Preise in konfigurierbaren Frequenzen.
- Schreiben direkt in Timescale oder per Redpanda‑Topic → API‑Consumer persistiert.

**Echtbetrieb**
- Spätere Adapter (REST/MQTT/SFTP) strukturieren Rohdaten in ein **kanonisches Schema** und versionieren.

**Validierung**
- Schema‑Validierung (Pydantic/JSON‑Schema) + Qualitätssignale (z. B. Missing‑Rate, Outlier‑Score) pro Batch.

---

## 7. Observability & Admin (Phase 5)

**Logs**
- Strukturierte JSON‑Logs (loguru) mit Korrelation (request_id, user_id).
- Loki/Promtail optional per Profile.

**Metriken**
- API‑Latenz, Qdrant‑Suchzeit, Embedding‑Dauer, DB‑Write‑Rate, Queue‑Lag.

**Tracing**
- OpenTelemetry hooks in API‑Pfaden (später aktivieren).

**Admin‑Dashboard (für Monika)**
- Dokumente ingestieren, Jobs steuern, Health‑Übersicht, Modell‑Versionen, Audit‑Trail.

**Kundendashboard (Konzept)**
- „Playbook‑Mode“ mit geführten Seiten: *Warum → Was → Wie → Was‑wäre‑wenn*.
- Visual Storytelling: Systemlandkarte (Ziele↔Daten↔Wirkung), KPI‑Zeitwellen, Szenario‑Slider.

---

## 8. Security & Compliance (lokal, später erweiterbar)
- API‑Key pro Kunde, Rollen (admin, analyst, viewer) – JWT/HTTP Header.
- Network Policies: nur notwendige Ports exposen; alles andere im Bridge‑Netz.
- Backups: Postgres (pg_dump + WAL), Qdrant Snapshots, MinIO Versioning.
- Datenschutz: Anonymisierung vor Meta‑Learning; Tenant‑Isolation durch DB‑Schemas & Namespaces.

---

## 9. Delivery‑Prozess

**Repo‑Struktur**
```
/ api/            # FastAPI
/ migrations/     # SQL
/ scripts/        # preflight, migrate, seed, backup
/ docker/         # compose files & overrides
/ docs/           # Architektur, ADRs, Playbook‑Mapping
```

**Makefile‑Kommandos (Beispiele)**
```
make preflight     # Port‑Check, Netz/Volume‑Check
make up            # compose up -d
make down          # compose down
make logs          # tail -f aller Services
make migrate       # SQL ausführen
make seed          # Demo‑Daten + Embeddings
```

**CI**
- Lint/Typecheck, Unit‑Tests, Contract‑Tests (OpenAPI), Build Compose, Healthcheck‑Gate.

---

## 10. Umgang mit Port‑Konflikten (Best Practices)
1. **.env als einzige Quelle** für Port‑Werte.
2. **Preflight** vor `up`: prüft Ports und schlägt freie Alternativen vor.
3. **Compose‑Profile**: optionale Dienste standardmäßig aus → weniger belegte Ports.
4. **Keine harten Container‑Namen** außer wo nötig; Netz‑Alias statt Host‑Ports intern verwenden.
5. **Dokumentierte Standardbelegung** (Tabelle oben) und „Fallback‑Range“ (z. B. 18000–18999) pro Kunde.

---

## 11. Roadmap (Implementierungs‑Tasks)

**Phase 1 – Core & Stabilität**
- [ ] `.env` + Preflight‑Script
- [ ] Compose Basis + Healthchecks
- [ ] API‑Skeleton + OpenAPI Export
- [ ] Migrations + Seed (Beispiel‑Dokument + Embedding)

**Phase 2 – RAG & Ingest**
- [ ] Tika‑Anbindung, Chunking, Qdrant Upsert
- [ ] `/rag/ask` mit konfigurierbarem Prompt & Zitat‑IDs
- [ ] Admin: Upload‑Maske + Status

**Phase 3 – Data Layer (Simulation)**
- [ ] Smart‑Meter‑Generator → Timescale
- [ ] Marktpreis‑Generator → Timescale
- [ ] (Optional) Redpanda‑Pfad + Consumer

**Phase 4 – Admin‑Dashboard**
- [ ] Health/Jobs/Uploads/Backups
- [ ] Rollen/Keys Verwaltung

**Phase 5 – Customer‑Dashboard (Playbook‑Mode)**
- [ ] JSON‑Schemas der Playbook‑Module
- [ ] Visual System Map + KPI‑Views
- [ ] Szenarien‑„What‑If“ (Python Engine)

**Phase 6 – Observability & Meta‑Learning**
- [ ] Loki/Prometheus Profile
- [ ] Feedback‑Loop + Audit Trails
- [ ] Anonymisierte Embedding‑Aggregation

---

## 12. Risiken & Gegenmaßnahmen
- **Port‑Flapping / alte Container** → `make down --remove-orphans` + Preflight.
- **Speicherlast durch Modelle** → Modell‑Profile (klein/mittel/groß), Limits in Compose.
- **Embedding‑Dimensionen inkonsistent** → zentrale Config + Collection‑Versionierung.
- **Langsame Tika/Parsing** → Worker‑Queue + Parallelisierung in Batches.

---

## 13. Offene Punkte (für spätere Iterationen)
- AuthN/Z fein granular (Scopes je Endpoint)
- Re‑Ranking (Cross‑Encoder) lokal
- Neo4j/Graph‑Layer für Kausalpfade
- Feature Store (Feast) für Recommender

---

## 14. Definition of Done (MVP)
- `make up` bringt das System **gesund** hoch (alle Healthchecks grün).
- `/ingest/doc` akzeptiert PDF/DOCX/TXT und zeigt die Chunks in DB + Qdrant.
- `/rag/ask` liefert Antwort inkl. Chunk‑Zitate.
- Preflight verhindert Port‑Konflikte oder nennt klare Alternativen.

> **Nächster Schritt**: Preflight‑Script + Basis‑Compose erstellen und in Repo einchecken. Danach: Migrations + API‑Skeleton.

