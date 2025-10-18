# Luna‑IEMS – Technische Planung: **Admin‑Dashboard** (Greenfield)

> Ziel: Ein **privates, lokales** Cockpit für dich als alleinige Admin – Wissen einspielen, Systeme überwachen, Modelle steuern. Klare Trennung vom Kundendashboard. Fokus: Stabil, erweiterbar, „portsafe“.

---

## 0) Architekturüberblick

**Stack**
- **Frontend (Admin UI)**: React (Next.js) + shadcn/ui, Dark Mode default
- **Backend (Admin API)**: FastAPI (Python 3.11), async Endpunkte
- **Queue/Worker**: Redis + RQ (oder Celery) für asynchrone Ingest‑Jobs
- **Dok‑Extraktion**: Apache Tika
- **Embeddings/LLM**: Ollama (lokal) – *nomic-embed-text*, *llama3.1:8b* (parametrisierbar)
- **Vektorstore**: Qdrant
- **SQL**: Postgres (Timescale optional)
- **Object Store**: MinIO (für Originaldateien)
- **Monitoring**: interner /health + /metrics; optional Prometheus/Grafana

**Netzwerk/Ports (portsafe)**
- Alle Services intern auf `luna-net`
- Externe Publishes sind in `.env` konfigurierbar; Standard:
  - Admin‑API: `ADMIN_API_PORT=8800`
  - Admin‑UI: `ADMIN_UI_PORT=8801`
  - Postgres: intern
  - Qdrant: intern
  - MinIO Console nur lokal (optional publish)

**Flows**
1) **Upload** → Tika → Chunking → Embedding → Qdrant + Metadaten in Postgres + Datei in MinIO → Jobstatus zurück an UI.
2) **Connectors** (APIs/Feeds) → periodische Sync‑Jobs → gleiche Pipeline wie Upload.
3) **Monitoring** → Admin‑API sammelt Metriken (Docker/Compose, DB, Redis, Qdrant, Ollama) → UI Panels.

---

## 1) Datenmodell (SQL)

**Tabellen**
- `documents`
  - `doc_id UUID PK`, `title TEXT`, `kind TEXT`, `source TEXT`, `sha256 TEXT UNIQUE`, `mime TEXT`, `size_bytes BIGINT`, `created_at TIMESTAMPTZ`, `version INT DEFAULT 1`
- `document_chunks`
  - `chunk_id UUID PK`, `doc_id UUID FK`, `idx INT`, `text TEXT`, `meta JSONB`, `created_at TIMESTAMPTZ`
- `ingest_jobs`
  - `job_id UUID PK`, `trigger TEXT` (upload|connector), `status TEXT` (queued|running|done|error), `progress REAL`, `error TEXT`, `created_at`, `updated_at`
- `connectors`
  - `connector_id UUID PK`, `name TEXT`, `type TEXT` (api|ftp|folder|…), `config JSONB`, `enabled BOOL`, `last_run TIMESTAMPTZ`, `last_status TEXT`
- `admin_audit`
  - `id BIGSERIAL PK`, `actor TEXT`, `action TEXT`, `target TEXT`, `meta JSONB`, `ts TIMESTAMPTZ DEFAULT now()`
- **(optional)** `knowledge_versions` für Snapshots/Versioning

**Indizes**
- `CREATE INDEX ON document_chunks (doc_id, idx);`
- `CREATE UNIQUE INDEX ON documents (sha256);`
- `CREATE INDEX ON connectors ((config->>'type'));`

---

## 2) Qdrant – Collections

- **Collection**: `luna_docs`
  - `vector`: 768 dims (Default, per ENV konfigurierbar)
  - `payload`: `{ doc_id, idx, kind, source, tags[] }`
- Parametrisierung via ENV: `EMBED_DIM=768`, `EMBED_MODEL=nomic-embed-text`

---

## 3) Admin‑API (FastAPI)

**Konfiguration (ENV)**
```
ADMIN_API_PORT=8800
DATABASE_URL=postgresql://luna:luna@postgres:5432/luna
QDRANT_URL=http://qdrant:6333
OLLAMA_URL=http://ollama:11434
EMBED_MODEL=nomic-embed-text
GENERATE_MODEL=llama3.1:8b-instruct
MINIO_ENDPOINT=http://minio:9000
MINIO_ACCESS_KEY=minio
MINIO_SECRET_KEY=minio12345
MAX_UPLOAD_MB=100
```

**Basispfade**
- `GET /health` → OK + abhängige Komponentenstatus
- `GET /metrics` → Lightweight JSON (CPU/RAM, Queue‑Länge, Fehlerquote)

**Upload & Ingest**
- `POST /upload` (multipart): Datei + Metadaten → `job_id`
- `GET /jobs/{job_id}`: Status/Progress
- `POST /reindex/{doc_id}`: Rebuild Embeddings/Chunks

**Connectors**
- `GET /connectors` / `POST /connectors` / `PATCH /connectors/{id}`
- `POST /connectors/{id}/run`: Sofortiger Sync (enqueue Job)

**Wissensbasis**
- `GET /documents?query=&kind=&source=&limit=&cursor=`
- `GET /documents/{doc_id}`: Metadaten + Chunks + Qdrant‑Payload
- `DELETE /documents/{doc_id}` (soft delete + tombstone)

**Model Control**
- `GET /models` → von Ollama (installiert/verfügbar)
- `POST /models/pull` `{ name }`
- `POST /models/select` `{ embed_model?, generate_model? }`

**System/Monitoring**
- `GET /system/summary` → Aggregat: Postgres, Qdrant, Redis, Ollama, Disk, Volumes, Container Health
- `GET /logs?service=&level=&since=` → Tail aus sammelndem Log‑Agent oder Dateirotation

**Security**
- `POST /auth/login` → JWT (nur lokaler Admin‑User, ENV‑Secret)
- *RBAC vorbereitet*: Rollen `admin`, `auditor` (später)

---

## 4) Admin‑Frontend (Next.js)

**Seiten**
1. **Dashboard** (Overview)
   - Kacheln: Systemstatus, Queue, Letzte Uploads, Fehlerrate
   - Charts: Ingest/Minute, Qdrant Search Latency, DB Größe
2. **Wissensverwaltung**
   - Upload (Drag‑and‑Drop), Fortschritt, Duplikaterkennung (SHA256)
   - Dokumentliste (Filter: kind/source/tags), Detailansicht (Chunks), Reindex‑Button
3. **Connectors**
   - Liste + Status, Manuell ausführen, Logs pro Connector
4. **Model Control**
   - Aktive Modelle, `pull/select`, Modelgröße, Speicher
5. **Monitoring**
   - Services Health, Container Info, Volumes, Disk, Alert Panel
6. **Audit & Logs**
   - Tabelle + Filter, Export CSV/JSON
7. **Einstellungen**
   - ENV‑Spiegel (readonly), API Keys, Sicherheitsoptionen

**UI‑Komponenten**
- Globales **Admin‑Topbar** (Dark default), Breadcrums
- **Toast/Jobs Drawer**: laufende Jobs, Fehler quick actions
- **Insight Panel** (rechts): Inline‑Tipps von Luna (Admin‑Kontext)

---

## 5) Ingest‑Pipeline (Detail)

**Steps**
1. **Store**: Datei → MinIO (`bucket=documents/{doc_id}/{filename}`)
2. **Extract**: Tika (`PUT /tika`), raw → text
3. **Normalize**: Encoding fix, Whitespace, Head/Foot remove
4. **Chunking**: 1200–1600 chars mit 200 overlap (param.)
5. **Embed**: Ollama embeddings, Batchgröße 32
6. **Index**: Qdrant upsert (payload + vector)
7. **Meta**: Postgres `documents`, `document_chunks`
8. **Audit**: `admin_audit` (actor, action="ingest", target=doc_id)

**Fehlerhandling**
- Hard‑fail → `ingest_jobs.status=error`, `error` Feld
- Retries (exponentiell) bei Transienten: Tika Timeout, Qdrant 5xx

---

## 6) Monitoring & Observability

- **Healthchecks**: Admin‑API prüft:
  - `postgres` – einfache Query (SELECT 1)
  - `qdrant` – `GET /collections`
  - `ollama` – `POST /api/tags`
  - `redis` – `PING`
- **Metriken**: JSON‑Endpoint (für UI‑Charts), z. B.:
  - `ingest_rate`, `embed_latency_ms`, `qdrant_search_ms`, `db_size_mb`, `disk_free_gb`
- **Alerts** (optional): Webhook/Email bei thresholds

---

## 7) Security & Isolation

- Admin‑UI/API nur auf `localhost` publishen (Standard). Reverse‑Proxy optional.
- JWT Secret über ENV, Single Admin User (bootstrap), Session Timeout
- Upload‑Validation (MIME/Size), Quarantäneordner bei unbekanntem Typ
- Kein direkter Internetzugang nötig (Offline‑Betrieb möglich; Modelle pre‑pull)

---

## 8) Docker‑Compose (Admin‑Stack, portsafe)

```yaml
version: "3.9"
services:
  admin_api:
    build: ./admin/backend
    container_name: luna_admin_api
    env_file: .env
    ports:
      - "${ADMIN_API_PORT:-8800}:8800"
    depends_on: [postgres, qdrant, redis, ollama, minio, tika]
    networks: [luna-net]

  admin_ui:
    build: ./admin/frontend
    container_name: luna_admin_ui
    env_file: .env
    ports:
      - "${ADMIN_UI_PORT:-8801}:3000"
    depends_on: [admin_api]
    networks: [luna-net]

  postgres:
    image: postgres:15
    container_name: luna_postgres
    environment:
      POSTGRES_USER: luna
      POSTGRES_PASSWORD: luna
      POSTGRES_DB: luna
    volumes:
      - pgdata:/var/lib/postgresql/data
    networks: [luna-net]

  qdrant:
    image: qdrant/qdrant:latest
    container_name: luna_qdrant
    networks: [luna-net]

  redis:
    image: redis:alpine
    container_name: luna_redis
    networks: [luna-net]

  minio:
    image: quay.io/minio/minio:latest
    container_name: luna_minio
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minio
      MINIO_ROOT_PASSWORD: minio12345
    volumes:
      - minio:/data
    networks: [luna-net]

  tika:
    image: apache/tika:2.9.0
    container_name: luna_tika
    networks: [luna-net]

  ollama:
    image: ollama/ollama:latest
    container_name: luna_ollama
    volumes:
      - ollama:/root/.ollama
    networks: [luna-net]

networks:
  luna-net:
    name: luna-net

volumes:
  pgdata:
  minio:
  ollama:
```

> Hinweis: Keine öffentlichen Ports für Qdrant/Postgres/Redis/Tika/MinIO nötig. Nur Admin‑API und Admin‑UI publishen – beide per `.env` steuerbar.

---

## 9) API‑Schemas (Auszug)

**Upload**
```http
POST /upload  (multipart)
fields: file, kind=document|policy|note, source=upload, tags[]=...
→ 200 { job_id }
```
**Job Status**
```json
{
  "job_id": "uuid",
  "status": "queued|running|done|error",
  "progress": 0.0,
  "error": null
}
```
**System Summary**
```json
{
  "services": {
    "postgres": "healthy",
    "qdrant": "healthy",
    "redis": "healthy",
    "ollama": "healthy",
    "minio": "healthy",
    "tika": "healthy"
  },
  "metrics": {"ingest_rate": 2.4, "qdrant_search_ms_p95": 18}
}
```

---

## 10) Roadmap (Tasks)

### Sprint A – Foundations
- [ ] Admin‑API Skeleton (FastAPI, JWT, /health, /metrics)
- [ ] DB Migrations (alembic) – Tabellen aus Abschnitt 1
- [ ] Ingest Worker (Redis + RQ), Basis‑Pipeline (Tika → Chunk → Embed → Qdrant)
- [ ] Admin‑UI Grundlayout (Dark, Nav, Toaster, Jobs Drawer)

### Sprint B – Knowledge Ops
- [ ] Upload UI + Progress, Duplikatprüfung (SHA256)
- [ ] Dokumentliste + Detail + Reindex
- [ ] Connectors CRUD + „Run Now“
- [ ] Audit Log Ansicht

### Sprint C – Control & Monitoring
- [ ] Model Control (Ollama list/pull/select)
- [ ] Monitoring Panels (System Summary, Fehler, Queue)
- [ ] Backup/Restore Hooks (PG Dump, Qdrant Snapshot)

### Sprint D – Hardening
- [ ] Error Budget/Retry Policy, Circuit Breaker bei Embeddings
- [ ] Limits (MAX_UPLOAD_MB), MIME allowlist, Antivirus Hook (optional)
- [ ] Load/Chaos Tests (synthetisch)

---

## 11) Erweiterbarkeit & Gaps
- **Policy Layer** (DLP/Klassifizierung) – Gate vor Indexierung
- **Prompt/Config Versioning** – Reproduzierbarkeit für RAG
- **Feature Store** für Recommender (später)
- **Offline‑Betrieb** – Vollständige Air‑Gap Doku (Modelle vorinstalliert)

---

## 12) Akzeptanzkriterien (MVP)
- Upload von PDF/DOCX/TXT bis 100 MB → innerhalb 60s verarbeitet (bei ~100 Seiten)
- Dokument in Postgres + Chunks in Qdrant, durchsuchbar
- Systemstatus zeigt korrekt Health aller Abhängigkeiten
- Modelle switchbar (Embedding/Generate) ohne Neustart
- Alle Ports konfliktfrei durch `.env` steuerbar

---

**Fertig.** Dieses Dokument dient als „Contract“ zwischen PM & Dev‑Team. Von hier aus können wir unmittelbar Tasks erstellen und den Admin‑Stack umsetzen.

