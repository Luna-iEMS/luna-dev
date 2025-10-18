# Luna‑IEMS – Technischer Gesamtplan (Greenfield, finalisiert)

> **Scope**: Single‑Tenant pro Kunde (voll isoliert), Deutsch als UI/Content‑Sprache, globale Wissensbasis erlaubt (anonymisiert/hybrid möglich), reines Docker‑Deployment (Compose) mit späterer Cloud‑Option. Fokus: robuste Daten/API‑Schicht, klare Port/Env‑Policy, saubere Observability, Admin‑Only‑Ingestion.

---

## 1) Richtungsentscheidungen (vom PM bestätigt)
- **Sprache**: ausschließlich Deutsch (UI, Texte, Prompts).
- **Dokument‑Metadaten & Versionierung**: von Dev‑Team definiert (siehe §4).
- **Simulationen**: Parameter & Märkte von Dev‑Team definiert (siehe §6).
- **Admin‑Dashboard**: keine Rollenverwaltung (Single Admin). Technologie & Aufbau von Dev‑Team festgelegt (siehe §7).
- **Customer‑Dashboard**: Export (CSV/PDF) **ja**. Luna darf globales Wissen nutzen (siehe §9).
- **Observability/Logging**: vom Dev‑Team entschieden (siehe §10).
- **Deployment**: strikt Docker Compose; Port‑Konflikt‑Strategie enthalten (siehe §12).

---

## 2) Zielbild & Architektur (High‑Level)
**Kernebenen**
1. **Data Layer**: PostgreSQL (TimescaleDB‑Extension) + Qdrant (Vektor) + MinIO (Objekte).  
2. **Compute/AI Layer**: FastAPI (API), Worker (Async‑Jobs), Ollama (LLM/Embeddings).  
3. **Integration Layer**: Ingestion (Upload + künftige Feeds), Simulation (Smart‑Meter/Markets).  
4. **Experience Layer**: Customer Dashboard (Playbook‑Inhalte, Insights), Admin Dashboard (Ingestion, Control, Monitoring).  
5. **Observability**: Prometheus + cAdvisor + Loki + Promtail + Grafana.

**Isolierung**: Pro Kunde ein kompletter Stack (eigene DB/Qdrant/Objektspeicher/LLM/Logs). Optional vorbereitete Felder für Tenant‑IDs bleiben im Schema, werden aber **nicht** cross‑tenant verwendet.

---

## 3) Services (Compose‑Ebene, feste Komponenten)
- **postgres**: TimescaleDB (PG15), persistentes Volume, tägliche Dumps, WAL aktiviert.
- **qdrant**: Vektorsuche, Collection „`chunks`“ (COSINE, dim 768). Snapshots aktiviert.
- **minio**: Objektspeicher für Rohdokumente/Artefakte/Backups.
- **ollama**: LLM/Embeddings (z. B. `nomic-embed-text`, `llama3.1:8b-instruct`).
- **api**: FastAPI (HTTP), synchron/async Mix, OpenAPI aktiv.
- **worker**: Hintergrundjobs (Ingestion‑Pipelines, Chunking, Embeddings, Exporte, Snapshots).
- **simulator**: Generiert Smart‑Meter- & Marktpreis‑Zeitreihen.
- **observability**: Prometheus, cAdvisor, Loki, Promtail, Grafana.

> **Hinweis**: Ports & ENV‑Variablen sind zentral in `.env` definiert, um Kollisionen zu vermeiden (siehe §12).

---

## 4) Datenmodell (relational) – PostgreSQL/Timescale
**Erweiterungen**: `timescaledb`, `pgcrypto`, `uuid-ossp` (optional).

### 4.1 Relationale Tabellen
- **users**  
  `user_id UUID PK`, `external_id TEXT UNIQUE`, `created_at TIMESTAMPTZ`.

- **items** (logischer Head pro Dokument)  
  `item_id UUID PK`, `kind TEXT` (document|regulation|article|note|report), `source TEXT`, `title TEXT`,  
  `tags TEXT[]`, `lang TEXT DEFAULT 'de'`, `confidentiality TEXT` (public|internal|restricted),  
  `sha256 TEXT`, `version INT DEFAULT 1`, `status TEXT` (active|archived|draft),  
  `created_by TEXT`, `ingestion_method TEXT` (upload|api|crawler),  
  `embedding_model TEXT`, `chunking JSONB`, `created_at TIMESTAMPTZ`.

- **item_versions** (Historie, Append‑Only)  
  `version_id UUID PK`, `item_id UUID FK`, `version INT`, `notes TEXT`, `created_at TIMESTAMPTZ`,  
  `diff JSONB` (optional), `file_uri TEXT` (MinIO‑Pfad), `checksum TEXT`.

- **item_chunks**  
  `chunk_id UUID PK`, `item_id UUID FK`, `chunk_idx INT`, `text TEXT`,  
  `metadata JSONB`, `created_at TIMESTAMPTZ`.

- **events** (Hypertable)  
  `event_id UUID PK`, `user_id UUID FK`, `ts TIMESTAMPTZ NOT NULL`, `type TEXT` (view|click|like|solve|export|ask),  
  `item_id UUID FK`, `meta JSONB`.

- **smart_meter_readings** (Hypertable)  
  `meter_id TEXT`, `ts TIMESTAMPTZ`, `consumption_kw DOUBLE PRECISION`,  
  `production_kw DOUBLE PRECISION`, `voltage DOUBLE PRECISION`, `quality TEXT`,  
  **PK** `(meter_id, ts)`.

- **market_prices** (Hypertable)  
  `market TEXT`, `product TEXT`, `ts TIMESTAMPTZ`, `price_eur_mwh DOUBLE PRECISION`, `volume DOUBLE PRECISION`,  
  **PK** `(market, product, ts)`.

- **labels** (Recommender/Feedback)  
  `user_id UUID FK`, `item_id UUID FK`, `ts TIMESTAMPTZ`, `reward DOUBLE PRECISION`, `reason TEXT`,  
  **PK** `(user_id, item_id, ts)`.

- **audit_log**  
  `log_id UUID PK`, `ts TIMESTAMPTZ`, `actor TEXT`, `action TEXT`, `target TEXT`, `meta JSONB`.

**Wichtige Indizes**:  
- `items(tags GIN)`, `events(user_id, ts DESC)`, `item_chunks(item_id)`, Timescale‑Hypertables für `events`, `smart_meter_readings`, `market_prices`.

### 4.2 Objektspeicher (MinIO)
- Bucket `documents` (Rohdateien), `exports` (CSV/PDF), `backups` (DB/Qdrant Snapshots).  
- Versionierung aktiv, Lifecycle‑Policies optional.

### 4.3 Vektorsuche (Qdrant)
- **Collection `chunks`**: `dim=768`, `distance=COSINE`, payload: `item_id`, `chunk_idx`, `lang`, `tags`, `confidentiality`.
- **Collection `feedback`** (optional): semantische Relevanzsignale (künftig für Re‑Ranking).

---

## 5) API – Oberflächen & Verträge
**Base**: `FastAPI` (OpenAPI/Swagger aktiviert in Dev), JSON over HTTP.

### 5.1 Admin‑Endpoints (nur Admin‑Key)
- `POST /admin/ingest/doc` – Upload → Tika → Chunk → Embed → Qdrant + PG.  
- `GET /admin/ingest/status` – Queue/Progress (Worker).  
- `POST /admin/items/{item_id}/version` – neue Version anlegen.  
- `GET /admin/collections` – Qdrant‑Status.  
- `POST /admin/sim/start|stop|config` – Simulator steuern.  
- `GET /admin/health` – Health‑Aggregation.

### 5.2 Customer‑Endpoints
- `POST /rag/ask` – Frage → Embedding → Qdrant → Compose → LLM‑Antwort (+Chunks).  
- `POST /recommend` – Content‑basiert/Bandit‑Seed → Qdrant Search.  
- `POST /events` – Telemetrie (view/click/like/ask/export).  
- `GET /export/{type}` – CSV/PDF (generiert über Worker) – **nur datenbezogen**.  
- `GET /timeseries/meter` – Zeitreihen‑Abfragen (Timescale Continuos Aggregates).  
- `GET /timeseries/market` – Märkte/Produkte.

**Sicherheit**: Admin‑Key über `X-Admin-Token`, Customer‑JWT optional (später). Rate‑Limit (reverse proxy) optional.

---

## 6) Simulationen (Phase 3)
**Smart‑Meter**
- Frequenz: 1 min (konfigurierbar: 1–5 min).  
- Parameter (Default): `consumption_kw ~ N(3.5, 0.8)`, `production_kw ~ max(0, PV(t) + ε)`, `voltage ~ N(230, 2)`.  
- Tagesgang über Sinus + Wochenend‑Modifier, Störimpulse (z. B. +25% Spitze).  

**Märkte/Produkte**  
- `ELECTRICITY_DA` (Day‑Ahead), `INTRADAY`, `CO2_EU_ETS`, `GAS_TTF`.  
- Prozess: AR(1) + saisonale Wellen, gelegentliche Schocks.  
- Speicherung: `market_prices` Hypertable; Aggregationen: 15 min/1 h CA.

**Ersetzung durch echte Feeds**: klare Adapterschnittstelle (`simulator.providers.{name}`) – echte Provider implementieren dieselben Interfaces.

---

## 7) Admin‑Dashboard (Single Admin)
**Technologie**: React + TypeScript + Vite + Tailwind + shadcn/ui.  
**Module**:
1. **Ingestion**: Drag&Drop, Typ/Tags/Confidentiality, Fortschritt, Retrys.  
2. **Knowledge**: Collections, Top‑Items, Embedding‑Modellumschaltung, Rebuild.  
3. **Simulation**: Start/Stop, Parameter‑Live‑Edit, Vorschauplot.  
4. **Monitoring**: Health aller Services, Latenzen, Queue‑Länge, Speicher.  
5. **Auditing**: jede Aktion + Export.  
6. **Backups**: manuell anstoßen, Restore‑Preview.  

**Auth**: statischer Admin‑Token (vorerst).

---

## 8) Customer‑Dashboard
**Inhalte** (aus Playbook abgeleitet, technisch priorisiert):
- **Luna Insight Panel**: RAG‑Chat (kontextbewusst), Guided Prompts, Zitat‑Verweise [chunk].  
- **Power‑Flow & Preise**: Zeitreihen‑Panels (Smart‑Meter/Markets) mit Zoom/Export.  
- **Regelwerke & Dokumente**: Filter/Facetten (Tags, Quelle), Vorschau, Download, Zitier‑Anker.  
- **Empfehlungen**: content‑basiert + Feedback‑Buttons (Hilfreich/Irrelevant).  
- **Berichte**: generierte Zusammenfassungen (PDF/CSV Exporte).  
- **Systemstatus/Support**: Mini‑Health, Hilfe‑Center (von Luna generiert), Impressum, Datenschutz.

**Export**: CSV/PDF via Worker, Ablage in MinIO `exports/` (signierte Links, zeitbegrenzt).

---

## 9) Luna – Wissensstrategie & Guardrails
- **Globales Wissen** (freigegeben): anonyme, aggregierte Muster (keine Rohdaten/PII).  
- **Kontextsteuerung**: RAG nur aus Kundenkorpus + optionale globale Wissensbausteine.  
- **Prompt‑Policy**: Deutsch, sachlich, leichte britische Ironie sparsam; Kennzeichnung von Unsicherheit; Quellzitate [chunk].  
- **Feedback‑Loop**: `labels` & `events` schreiben Scores zurück → Re‑Ranking/Bandit.

---

## 10) Observability (Docker‑Only)
- **Metrics**: Prometheus + cAdvisor (Container), PG‑Exporter, Qdrant‑/Ollama‑Probes.  
- **Logs**: Promtail → Loki (Standard‑Docker‑Driver);
- **Dashboards**: Grafana – Standardboards + Luna‑Custom (API Latenz, Qdrant Search‑Time, Embedding‑Queue, Error‑Rate).

**Healthchecks**: container‑native (compose `healthcheck`) + `/health` in API.

---

## 11) Security & Compliance (MVP‑angemessen)
- Netzwerktrennung: internes Docker‑Netz; API Ports explizit.  
- Secrets: `.env` (lokal), später Secret‑Manager.  
- MinIO: Access/Secret Keys aus `.env`.  
- Qdrant/PG: nur interner Zugriff; Backups verschlüsselt optional.  
- Audit‑Log vollständig bei Admin‑Aktionen.

---

## 12) Ports & ENV‑Policy (Konfliktfrei)
- **Zentrale `.env`** im Projektroot, *einzige* Quelle für Ports & Host‑Pfad‑Volumes.
- Vorgabe (empfohlen):  
  - `API_PORT=8001`  
  - `PG_PORT=8301`  
  - `QDRANT_HTTP=6333`, `QDRANT_GRPC=6334`  
  - `MINIO_API=9000`, `MINIO_CONSOLE=9001`  
  - `OLLAMA_PORT=11434`  
  - `GRAFANA_PORT=3000`, `PROM_PORT=9090`, `LOKI_PORT=3100`
- **Regel**: Nie „host:container“ Ports doppelt vergeben; bei Konflikt Anpassung **nur** in `.env`.

---

## 13) Migrations, Seeds & Snapshots
- **Alembic** (später) oder SQL‑Migrationsordner (`migrations/*.sql`).  
- **Seed‑Jobs**: Beispiel‑Dokumente + Beispiel‑Zeitreihen + Marktpreise.  
- **Backups**: PG `pg_dump` täglich, Qdrant Snapshots, MinIO Versioning.

---

## 14) Test‑ & Release‑Strategie
- **Unit**: Parser/Chunker/Embeddings/DB‑Repos.  
- **E2E (Docker)**: `docker compose -f docker-compose.dev.yml up --build` Smoke‑Tests → `/health`, `/rag/ask` Dummy, `/timeseries/*`.  
- **Load**: k6/Gatling gegen `/rag/ask` & `/timeseries`.  
- **Canary**: Simulator‑Only‑Run vor Live‑Feeds.

---

## 15) Umsetzung als Tasks/Sprints (Developer‑sicht)
**Sprint A – Foundation**  
A1 .env & Ports, Volumes, Netzwerk;  A2 DB‑Schema + Migrations;  A3 Qdrant Init;  A4 MinIO Buckets;  A5 Health/Dashboards.

**Sprint B – Ingestion & RAG**  
B1 Admin Upload → Tika;  B2 Chunking (naiv + Param);  B3 Embeddings/Upsert;  B4 `/rag/ask` MVP;  B5 Audit/Events.

**Sprint C – Simulation**  
C1 Smart‑Meter Generator;  C2 Markets Generator;  C3 API‑Abfragen & Aggregates;  C4 Beispiel‑Dashboards.

**Sprint D – Dashboards**  
D1 Admin (Ingestion/Knowledge/Monitoring/Backups);  D2 Customer (Insights/Docs/Charts/Exports).

**Sprint E – Observability & Hardening**  
E1 Prometheus/Loki/Grafana;  E2 Retry/RL‑Backoff;  E3 Snapshot/Backup‑Jobs;  E4 Security Pass.

---

## 16) Offene Punkte – jetzt geschlossen
- **Dokument‑Metadaten/Versionierung** → definiert (§4).  
- **Simulation** → Parameter & Märkte fix (§6).  
- **Globales Wissen** → Guardrails definiert (§9).  
- **Logging/Monitoring** → Stack gewählt (§10).  
- **Ports** → zentrale Policy & Defaults (§12).  
- **Admin‑Only‑Ingestion** → Endpunkte/Fluss klar (§5, §7).

---

## 17) Nächste konkrete Schritte (sofort umsetzbar)
1) `.env` gemäß §12 anlegen.  
2) Compose‑Stacks (core + observability) erstellen.  
3) DB‑Migration `001_init.sql` anwenden.  
4) Admin‑API `/admin/ingest/doc` + Worker‑Job implementieren.  
5) `RAG /rag/ask` minimal anbinden (Qdrant+Ollama).  
6) Simulator starten, Timeseries‑Panels prüfen.  
7) Grafana Dashboards importieren.

> Ab diesem Punkt ist das System Ende‑zu‑Ende nutzbar: Upload → Suche/Antwort → Zeitreihen → Exporte → Monitoring.

