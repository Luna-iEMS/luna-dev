# Luna‑IEMS – Technischer Masterplan (Closed Gaps v1)

**Ziel:** Alle offenen Punkte schließen, damit das Dev‑Team ohne Rückfragen implementieren kann. Enthält präzise API‑Specs, DB‑Schema‑Details, Simulation, Luna‑KI‑Konfiguration, UI‑Datenverträge, Infra/DevOps, Tests & DX.

---

## 0) Systemübersicht

- **Services:** API (FastAPI), Worker (Jobs/ETL), Postgres (Timescale), Qdrant, Ollama, MinIO (Objektspeicher), Tika (Textisierung), Redpanda/Kafka (optional), Customer‑Dashboard (Web), Admin‑Dashboard (Web)
- **Netz:** internes Docker‑Netz `luna-net`. Exponierte Ports zentral konfigurierbar über `.env`.
- **Datenflüsse:** Upload → Tika → Chunks → Embedding (Ollama) → Qdrant → Metadaten in Postgres → RAG/Recommend via API → Dashboards.

---

## 1) API – Spezifikation (v1)

**Base:** `/api/v1`  
**Auth:**
- **Customer‑Dashboard:** JWT (Bearer). Für MVP dev‑only: `X-Dev-User: <uuid>`.
- **Admin‑Dashboard:** API‑Key Header `X-Admin-Key`. Key in `.env` (`ADMIN_API_KEY`).

**Common Response**
```json
{ "status": "ok|error", "message": "...", "data": { ... }, "trace_id": "uuid" }
```

### 1.1 Ingest
- `POST /api/v1/ingest/doc` (multipart)
  - form: `file: UploadFile`, `kind: document|regulation|note` (default `document`), `source: upload|crawler|api` (default `upload`), `tags?: string[]`
  - return: `{ item_id, chunks, sha256 }`
- `POST /api/v1/ingest/url`
  - body: `{ url: string, kind?: string, tags?: string[] }`
  - server lädt Dokument (HTTP GET), leitet an `tika`, gleicher Pfad wie `doc`.

### 1.2 RAG
- `POST /api/v1/rag/ask`
  - body: `{ question: string, top_k?: number=6, filters?: { [key:string]: string|number|boolean }, stream?: boolean=false }`
  - return: `{ answer: string, chunks_used: string[], citations: [{chunk_id, score, payload}] }`

### 1.3 Recommendation (MVP)
- `POST /api/v1/recommend`
  - body: `{ user_id?: string, top_k?: number=10 }`
  - return: `{ items: [{ chunk_id, score, payload }] }`

### 1.4 Events/Feedback
- `POST /api/v1/events`
  - body: `{ user_id: string, type: "view|click|like|solve|ask|feedback", ts?: ISODate, item_id?: string, chunk_id?: string, meta?: object }`
  - return: `{ saved: true }`
- `POST /api/v1/feedback/rag`
  - body: `{ user_id?: string, question: string, answer: string, useful: boolean, notes?: string, chunks_used?: string[] }`
  - return: `{ saved: true }`

### 1.5 Admin
- `POST /api/v1/admin/reindex`  (Rebuild Embeddings für Items/Filter)
  - body: `{ item_ids?: string[], filter?: object }`
- `POST /api/v1/admin/snapshots`
  - body: `{ qdrant?: boolean, pg_dump?: boolean }`
- `GET  /api/v1/admin/health`
  - return: `{ services: {api, db, qdrant, ollama, tika, minio}, versions: {...} }`

### 1.6 System
- `GET /api/v1/system/info` → build, git sha, model versions.
- `GET /api/v1/docs` → Swagger (FastAPI).

**Fehlercodes:**
- 400: Validation
- 401/403: Auth
- 404: Not Found
- 409: Conflict (Duplicate `sha256`)
- 500: Internal

---

## 2) Datenbank – Schema & Indizes (Postgres/Timescale)

**Extensions:** `timescaledb`, `pgcrypto`

```sql
-- Nutzer
CREATE TABLE users (
  user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  external_id TEXT UNIQUE,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Inhalte
CREATE TABLE items (
  item_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  kind TEXT NOT NULL,
  source TEXT,
  title TEXT,
  tags TEXT[],
  url TEXT,
  sha256 TEXT UNIQUE,
  version INT DEFAULT 1,
  created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_items_tags ON items USING GIN (tags);
CREATE INDEX idx_items_sha ON items(sha256);

-- Chunks (Text liegt hier; Vektor in Qdrant)
CREATE TABLE item_chunks (
  chunk_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  item_id UUID REFERENCES items(item_id) ON DELETE CASCADE,
  chunk_idx INT NOT NULL,
  text TEXT NOT NULL,
  qdrant_id TEXT, -- optional Mapping
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_chunks_item ON item_chunks(item_id);

-- Events / Telemetrie → Hypertable
CREATE TABLE events (
  event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(user_id),
  ts TIMESTAMPTZ NOT NULL,
  type TEXT NOT NULL,
  item_id UUID REFERENCES items(item_id),
  chunk_id UUID REFERENCES item_chunks(chunk_id),
  meta JSONB DEFAULT '{}'::jsonb
);
SELECT create_hypertable('events','ts', if_not_exists => TRUE);
CREATE INDEX idx_events_user_ts ON events(user_id, ts DESC);

-- Smart‑Meter
CREATE TABLE smart_meter_readings (
  meter_id TEXT NOT NULL,
  ts TIMESTAMPTZ NOT NULL,
  consumption_kw DOUBLE PRECISION,
  production_kw DOUBLE PRECISION,
  voltage DOUBLE PRECISION,
  quality TEXT,
  PRIMARY KEY (meter_id, ts)
);
SELECT create_hypertable('smart_meter_readings','ts', if_not_exists => TRUE);

-- Marktpreise
CREATE TABLE market_prices (
  market TEXT NOT NULL,
  product TEXT NOT NULL,
  ts TIMESTAMPTZ NOT NULL,
  price_eur_mwh DOUBLE PRECISION,
  volume DOUBLE PRECISION,
  PRIMARY KEY (market, product, ts)
);
SELECT create_hypertable('market_prices','ts', if_not_exists => TRUE);

-- Labels/Feedback (RAG‑Qualität)
CREATE TABLE labels (
  user_id UUID REFERENCES users(user_id),
  item_id UUID REFERENCES items(item_id),
  ts TIMESTAMPTZ DEFAULT now(),
  reward DOUBLE PRECISION NOT NULL,
  reason TEXT,
  PRIMARY KEY(user_id, item_id, ts)
);
```

**Materialized Views (für Dashboard‑Performance):**
```sql
CREATE MATERIALIZED VIEW mv_events_daily AS
SELECT date_trunc('day', ts) AS day, type, count(*) AS cnt
FROM events GROUP BY 1,2;
CREATE INDEX ON mv_events_daily(day);
```

**Migrations:** Alembic/SQL‑Files. Seed‑Daten (Mock) via `scripts/seed.sql`.

---

## 3) Simulation Layer (Smart‑Meter & Marktpreise)

**Ziel:** Daten generieren, die später 1:1 durch echte Feeds ersetzbar sind.

- **Konfiguration:** `.env`
  - `SIM_SMARTMETER_INTERVAL_SEC=60`
  - `SIM_MARKET_INTERVAL_SEC=300`
  - `SIM_MARKETS=EEX,APX`
  - `SIM_PRODUCTS=BASE,PEAK`
- **Implementierung:** Service `worker` mit zwei Loops
  - schreibt direkt in Postgres (Timescale)
  - Dateiformat optional CSV‑Drop in MinIO (`s3://sim/…`), der Worker lädt ins DB
- **API (optional):** `POST /api/v1/sim/run` (admin only) → start/stop

**CSV‑Schema Beispiele**
```
smart_meter_readings.csv: meter_id,ts,consumption_kw,production_kw,voltage,quality
market_prices.csv: market,product,ts,price_eur_mwh,volume
```

---

## 4) Luna – KI‑Engine (Konfiguration & Learning Loop)

**Modelle (Ollama):**
- `EMBED_MODEL=all-minilm:33m` *(alternativ: `nomic-embed-text`)*
- `GENERATE_MODEL=llama3.1:8b-instruct`

**Prompt‑Templates (Persona/Ton):**
- Datei: `prompts/luna.yml`
```yaml
persona: |
  Du bist „Luna“, eine britisch-höfliche, leicht sarkastische Expertin für Energiewirtschaft und Antifragilität.
  Du antwortest präzise, zitierst Quellen (Chunk‑IDs) und gibst Handlungsempfehlungen.
  Wenn unsicher, sag es offen und biete eine nächste, konkrete Frage an.
style:
  language: de
  register: professionell, freundlich, klar
  sarcasm: leicht, nie verletzend
rag:
  system: |
    Beantworte ausschließlich auf Basis des bereitgestellten Kontexts.
    Zitiere relevante Passagen mit [chunk <ID>]. Gib eine kurze Zusammenfassung + Handlungsvorschlag.
```

**Learning Loop:**
1. User‑Events & RAG‑Feedback → `labels` und `events`
2. Nachtjob (`worker`):
   - Popularität & Qualitätsscores je Chunk/Item berechnen
   - optional Re‑Ranking‑Features materialisieren
3. Recommender: Content‑basiert (Avg‑Embeddings) → optional LinUCB/Thompson als nächster Schritt

**Wissenspflege:**
- Duplicate via `sha256` vermeiden
- Versionierung pro Item (`version`), Reindex bei Update
- Retention: Alte Chunks archivieren (Flag in `metadata`)

---

## 5) Dashboards – Datenverträge (UI ⇄ API)

### 5.1 Customer‑Dashboard
- **Global Insight Panel:**
  - `GET /api/v1/system/info` → Status + Versionsinfo
  - `GET /api/v1/metrics/overview` → counts (items, chunks, events/day)
- **RAG Suche/Q&A:**
  - `POST /api/v1/rag/ask` → Antwort + `chunks_used`
- **Datenbereiche:**
  - Smart‑Meter Charts → `GET /api/v1/data/smartmeter?meter_id=&from=&to=`
  - Marktpreise → `GET /api/v1/data/market?market=&product=&from=&to=`
- **Empfehlungen:** `POST /api/v1/recommend`
- **Hilfe:** `GET /api/v1/help/context?route=` (Luna generiert Text serverseitig)

### 5.2 Admin‑Dashboard
- **Upload/Feeding:** `POST /api/v1/ingest/doc`, `/ingest/url`
- **Korpusverwaltung:** `GET /api/v1/admin/items?query=&tag=`; `DELETE /api/v1/admin/item/:id`
- **Monitoring:** `GET /api/v1/admin/health`, `GET /api/v1/metrics/ingest`
- **JOBS:** `POST /api/v1/admin/reindex`, `POST /api/v1/admin/snapshots`
- **Logs:** Streaming via Fluent‑Bit → Loki/Files; API zeigt Summary KPIs.

**UI‑Komponenten (Empfehlung):** React + shadcn/ui + Recharts, State über React Query.

---

## 6) Infrastruktur & DevOps

**Ports & .env** (Beispiel)
```
API_PORT=8000
DB_PORT=5432
QDRANT_HTTP=6333
QDRANT_GRPC=6334
OLLAMA_PORT=11434
MINIO_API=9000
MINIO_CONSOLE=9001
TIKA_PORT=9998
```

**Compose (dev/prod getrennt)**
- `docker-compose.dev.yml` (bind mounts, reload)
- `docker-compose.yml` (prod‑like, Healthchecks, Ressourcenlimits)

**Healthchecks (Beispiele)**
- API: `curl -f http://localhost:${API_PORT}/api/v1/system/info`
- Qdrant: `curl -f http://localhost:${QDRANT_HTTP}/collections`
- Ollama: `curl -f http://localhost:${OLLAMA_PORT}/api/tags`
- Postgres: `pg_isready -U <user>`

**Volumes** getrennt: `pgdata`, `qdrant`, `ollama`, `minio`, `logs`.

**CI (optional):** GitHub Actions → Lint, Unit‑Tests, Build, Compose up (health), Artifacts.

---

## 7) Testing & Qualität

- **Unit:** API‑Handlers, Embedding‑Adapter, Tika‑Wrapper, DB‑Repos
- **Integration:** API ↔ Qdrant ↔ DB (Test‑Compose)
- **E2E (Smoke):** `make smoke` → start Compose, prüfe `/health`, ingest sample.pdf, rag/ask
- **Load (optional):** Locust für `/rag/ask`
- **UI:** React Testing Library + MSW für API‑Mocks

**Testdaten:**
- `docs/sample.pdf`, `docs/sample.docx`, `docs/sample.md`
- Seed‑SQL für Items/Chunks/Events

---

## 8) Developer Experience

- **Repo‑Struktur**
```
api/
  main.py
  routers/ (ingest, rag, recommend, admin, data)
  services/ (tika.py, embed.py, qdrant.py, db.py)
  prompts/luna.yml
worker/
  sim_smartmeter.py
  sim_market.py
  nightly_jobs.py
frontend/ (customer)
admin/ (admin)
scripts/
  seed.sql  make_smoke.sh
migrations/
.env .env.dev .env.prod
docker-compose.yml docker-compose.dev.yml
```
- **Makefile**
```
make dev      # local up (dev compose)
make down
make seed
make smoke    # ingest + rag test
```

---

## 9) Sicherheitsnotizen (MVP geeignet)

- API‑Key für Admin, JWT für Kunden (später OAuth/OIDC)
- Upload‑Validierung: Größe, Typ, Antivirus (ClamAV optional)
- Rate‑Limit auf `/rag/ask` (Reverse‑Proxy oder Starlette middleware)
- Logs ohne PII; Anonymisierung bei globalem Lernen optional aktivierbar

---

## 10) Offene Entscheidungen (jetzt finalisiert)

- Sprache: **Deutsch only** (Luna‑Persona de)
- Roles/RBAC: **nicht notwendig** im MVP (nur Admin‑Key + Customer‑JWT)
- Export: **CSV/JSON** per API, Admin kann Snapshots abziehen
- Logging: Fluent‑Bit → Files/Loki; strukturierte JSON‑Logs
- Deployability: Docker‑first, Ports strikt aus `.env`, Konflikte vermeiden

---

## 11) Akzeptanzkriterien (Go‑Live MVP)

1) `docker compose up` → alle Healthchecks grün  
2) Upload `sample.pdf` → Chunks > 0, Qdrant‑Punkte vorhanden  
3) `/rag/ask` liefert Antwort mit `[chunk …]`‑Zitaten  
4) Simulation erzeugt Daten; Customer‑Dashboard zeigt Live‑Charts  
5) Admin kann Reindex & Snapshots auslösen  
6) Smoke‑Test „grün“ (CI optional)

---

## 12) Nächste Schritte (Dev‑Start)

1) Repo‑Skeleton nach obiger Struktur anlegen  
2) `.env.dev` schreiben + Compose dev/prod erstellen  
3) DB‑Migrations & Seed ausrollen  
4) API‑Router `ingest`, `rag`, `data`, `admin` implementieren  
5) Worker‑Simulation starten  
6) Frontends mit minimalen Views (Insight Panel, Upload, Q&A)  
7) Smoke‑Test und Make‑Targets

