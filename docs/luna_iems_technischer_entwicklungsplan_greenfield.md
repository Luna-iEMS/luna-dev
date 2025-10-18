# Luna‑IEMS – Technischer Entwicklungsplan (Greenfield)

Dieses Dokument definiert die **technische Roadmap** für Luna‑IEMS von Null an. Fokus: **Data & API zuerst (stabil wie ein Fels)**, anschließend UI/UX (Kunden‑ & Admin‑Dashboard). Deployment pro Kunde **single‑tenant** (komplette Isolation); optional **anonymisierte Lern‑Aggregationen** für ein zentrales „Brain“.

---

## A) Architekturentscheidungen

- **Mandantentrennung**: je Kunde ein separater Stack (eigene DB, Qdrant, Ollama, MinIO – optional), eigene Volumes/Netzwerke.
- **Optionales Hybrid‑Learning**: Nur **anonymisierte Kennzahlen & Modellparameter** (keine Rohdaten, keine Dokumente) werden – falls freigegeben – zentral aggregiert.
- **Simulation** bis Live‑Schnittstellen verfügbar: Smart‑Meter & Marktpreise realistisch (Tages-/Wochenprofil, Saison, Ausfälle, Spikes).
- **Admin‑Service separat** (nur intern): Uploads, Freigaben, Schalter (z. B. für Aggregation). Kunden‑Dashboard folgt nach stabilen Daten/API.

---

## B) Datenmodell (TimescaleDB + Relational)

**Kern‑Tabellen**
- `users(user_id uuid, external_id text, created_at timestamptz)`
- `items(item_id uuid, kind text, source text, title text, tags text[], url text, sha256 text, version int, created_at timestamptz)`
- `item_chunks(chunk_id uuid, item_id uuid, chunk_idx int, text text, metadata jsonb, created_at timestamptz)`
- `events(event_id uuid, user_id uuid, ts timestamptz, type text, item_id uuid, meta jsonb)` → **Hypertable**
- `smart_meter_readings(meter_id text, ts timestamptz, consumption_kw double precision, production_kw double precision, voltage double precision, quality text)` → **Hypertable**
- `market_prices(market text, product text, ts timestamptz, price_eur_mwh double precision, volume double precision)` → **Hypertable**

**Privacy / Konfiguration**
- `privacy_config(flag_send_aggregates bool default false, instance_fingerprint text not null)`
- Keine PII; `external_id` optional vom Kunden gehasht.

**Vektor‑Store (Qdrant)**
- Collection `chunks` (COSINE, size=768), Payload: `{item_id, chunk_idx, tags?, source?}`

---

## C) Services & Schnittstellen

**Ingest**
- `POST /ingest/doc` – Datei → Tika → Chunks → DB → Embeddings → Qdrant
- `POST /ingest/telemetry` – anonyme Events (view/click/like/solve…)

**RAG & Empfehlungen**
- `POST /rag/ask` – top‑k Vektor‑Suche, DB‑Kontext, Antwort via Ollama
- `POST /recommend` – MVP content‑based; später Bandit/Re‑Ranking

**Simulation**
- `POST /sim/start` / `POST /sim/stop` – start/stop Scheduler‑Jobs
- `GET /sim/status` – Laufstatus & letzte Writes

**Monitoring / Ops**
- `GET /health` (live/ready), `GET /metrics` (Prometheus), `GET /status/summary` (JSON: Reachability, Counts)

---

## D) Simulation (Phase 3)

**Smart‑Meter**
- Base‑Load + Tages‑Sinus, Wochenend‑Faktor, Saison‑Faktor, Ausfälle (`quality='missing'`), 1–5 s Intervall (konfigurierbar)

**Marktpreise**
- Day‑Ahead‑Wellen, Intraday‑Noise, Wetter‑Spikes, CSV/Parquet‑Seed möglich

**Konfiguration**
- `/config/sim.yml`: Profile, Intervalle, Zufalls‑Seed

---

## E) Zentrales Lernen ohne Datenabfluss (optional)

- **Lokale Aggregation** aus `events`: CTRs, Dwell‑Time‑Stats, Rewards; Bandit‑Parameter (z. B. LinUCB/Thompson)
- **Differential Privacy** optional (Laplace‑Noise)
- **Exportformat** (nur Kennzahlen):
```json
{
  "schema": 1,
  "instance_fingerprint": "hash…",
  "period": "YYYY-MM-DD",
  "metrics": {"ctr": …, "rewards": …},
  "bandit": {"algo":"linucb","theta":[…],"A":[…],"b":[…]}
}
```
- Kein Auto‑Upload; Admin triggert Upload manuell (URL/Token in ENV)

---

## F) Artefakte & Dateien (Greenfield‑Set)

**Migrations**
- `migrations/001_init.sql` – Schema (oben)
- `migrations/002_privacy.sql` – `privacy_config` + Seed `instance_fingerprint`

**API (FastAPI)**
- `api/Dockerfile`
- `api/requirements.txt` (fastapi, uvicorn, qdrant-client, httpx, psycopg[binary], python-multipart, apscheduler)
- `api/main.py` – Endpunkte: `/ingest/doc`, `/ingest/telemetry`, `/rag/ask`, `/recommend`, `/sim/*`, `/health`, `/metrics`, `/status/summary`

**Compose (Dev)**
- `docker-compose.dev.yml` – Services: postgres (Timescale), qdrant, tika, ollama, api; Healthchecks & Volumes; konfliktfreie Ports

**Konfiguration & Tools**
- `.env.example` – alle URLs/Modelle/Flags (Privacy)
- `Makefile` – `up`, `down`, `logs`, `migrate`, `simulate`, `seed`, `testping`
- `docs/` – Beispiel‑Dateien für Ingest (TXT/PDF)

---

## G) Arbeitsweise & Tasks (Sprint‑ready)

**Sprint 1 – Fundament**
1. Repo‑Gerüst & Migrations erstellen
2. Compose‑Stack (Dev) lauffähig, Healthchecks grün
3. API‑Skeleton + `/health`, `/status/summary`

**Sprint 2 – Ingest & RAG**
1. Tika‑Anbindung, Chunking, Embeddings → Qdrant
2. `POST /ingest/doc` end‑to‑end Smoke‑Test
3. `POST /rag/ask` minimal (ohne Re‑Ranking)

**Sprint 3 – Simulation (Phase 3)**
1. Smart‑Meter‑Job (apscheduler), konfigurabel
2. Marktpreis‑Job, CSV‑Seed & Live‑Sim
3. `/sim/*` Endpunkte + `events`‑Aufzeichnung

**Sprint 4 – Monitoring (Phase 5 Vorarbeit)**
1. `/metrics`, Prometheus‑Exporter (API‑Metriken)
2. `status/summary` mit DB/Qdrant/Ollama‑Reachability
3. Logrotation & strukturierte Logs (jsonl)

**Sprint 5 – Hybrid‑Export (optional)**
1. Aggregation aus `events` + DP‑Option
2. `POST /learn/export` (signiert)
3. Merge‑Strategie (lokale Prior‑Seeds laden)

**Sprint 6 – Admin‑Service (Skeleton)**
1. Auth (local‑only), Upload UI (Docs/Daten), Schalter für Aggregation
2. Job‑Control (Sim an/aus), Runs/Errors sichtbar
3. Audit‑Trail (wer/was/wann)

**Nach Sprint 6**: Kundendashboard (UI/UX) mit hoher Politur, Playbook‑Darstellung, Assistent‑Guidance.

---

## H) Go‑/No‑Go Liste (Abnahmen)

- **Datenbank stabil**: Hypertables vorhanden, Indizes, Migrations idempotent
- **RAG Smoke**: Upload → Chunking → Embedding → Qdrant → Antwort
- **Simulation**: schreibt valide Zeitreihen (Query‑Beispiele liefern Werte)
- **Monitoring**: Health/Metrics erreichbar; Status zeigt korrekte Counters
- **Privacy**: Aggregation standardmäßig **aus**, Export nur manuell

---

## I) Nächste Schritte (für dich)

1) Dieses Dokument abnicken
2) Ich liefere das Greenfield‑Set (Migrations, API, Compose, .env.example, Makefile)
3) Du startest lokal, ziehst Ollama‑Modelle, führst Smoke‑Tests aus
4) Wir härten Metriken/Simulation nach Bedarf und gehen dann ins UI/UX

---

*Hinweis:* Alles ist so ausgelegt, dass spätere Live‑Integrationen (echte Smart‑Meter/Markt‑APIs) **ohne Schema‑Bruch** anbindbar sind; Simulation wird dann nur deaktiviert.

