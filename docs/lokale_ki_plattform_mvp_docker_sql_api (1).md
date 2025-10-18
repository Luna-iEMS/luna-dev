# Lokale KI-Plattform – MVP

Dieses Paket gibt dir einen lauffähigen Startpunkt (lokal/on‑prem) für:

- Dokumenteingang → Textisierung/Chunking → Embeddings → Qdrant (Vektor)
- Zeitreihen (Smart‑Meter, Börsenpreise) in TimescaleDB
- RAG‑API über Ollama (lokales LLM) + SQL‑/Timescale‑Abfragen
- Einfaches Empfehlungsskelett (Bandit‑Style Platzhalter)

---

## 1) `docker-compose.yaml`

```yaml
version: "3.9"
services:
  postgres:
    image: timescale/timescaledb:2.15.2-pg15
    container_name: ki_postgres
    environment:
      POSTGRES_USER: ki
      POSTGRES_PASSWORD: ki
      POSTGRES_DB: ki
    ports: ["5432:5432"]
    volumes:
      - pgdata:/var/lib/postgresql/data

  qdrant:
    image: qdrant/qdrant:latest
    container_name: ki_qdrant
    ports: ["6333:6333", "6334:6334"]
    volumes:
      - qdrant:/qdrant/storage

  minio:
    image: quay.io/minio/minio:latest
    container_name: ki_minio
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minio
      MINIO_ROOT_PASSWORD: minio12345
    ports: ["9000:9000", "9001:9001"]
    volumes:
      - minio:/data

  redpanda:
    image: redpandadata/redpanda:latest
    container_name: ki_redpanda
    command: >-
      redpanda start --overprovisioned --smp 4 --memory 4G --reserve-memory 0M
      --node-id 0 --check=false --kafka-addr PLAINTEXT://0.0.0.0:9092
      --advertise-kafka-addr PLAINTEXT://redpanda:9092
    ports: ["9092:9092", "9644:9644"]

  tika:
    image: apache/tika:2.9.0
    container_name: ki_tika
    ports: ["9998:9998"]

  ollama:
    image: ollama/ollama:latest
    container_name: ki_ollama
    environment:
      OLLAMA_KEEP_ALIVE: 24h
    volumes:
      - ollama:/root/.ollama
    ports: ["11434:11434"]

  api:
    build: ./api
    container_name: ki_api
    depends_on: [postgres, qdrant, minio, ollama]
    environment:
      DATABASE_URL: postgresql://ki:ki@postgres:5432/ki
      QDRANT_URL: http://qdrant:6333
      MINIO_ENDPOINT: http://minio:9000
      MINIO_ACCESS_KEY: minio
      MINIO_SECRET_KEY: minio12345
      OLLAMA_URL: http://ollama:11434
      EMBED_MODEL: nomic-embed-text
      GENERATE_MODEL: llama3.1:8b-instruct
    ports: ["8000:8000"]

volumes:
  pgdata:
  qdrant:
  minio:
  ollama:
```

> Nach dem ersten Start bitte im `ollama`-Container die Modelle ziehen, z. B. `ollama pull nomic-embed-text` und `ollama pull llama3.1:8b-instruct`.

---

## 2) SQL – Basisschema (Timescale + relational)

Datei: `migrations/001_init.sql`

```sql
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS pgcrypto; -- für UUIDs

-- Nutzer & Items
CREATE TABLE IF NOT EXISTS users (
  user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  external_id TEXT UNIQUE,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS items (
  item_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  kind TEXT NOT NULL,           -- document|regulation|article|note|...
  source TEXT,                  -- origin: url/system/ingest
  title TEXT,
  tags TEXT[],
  url TEXT,
  sha256 TEXT,
  version INT DEFAULT 1,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Events (Interaktionen, Telemetrie) → Hypertable
CREATE TABLE IF NOT EXISTS events (
  event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(user_id),
  ts TIMESTAMPTZ NOT NULL,
  type TEXT NOT NULL,           -- click|view|like|solve|...
  item_id UUID REFERENCES items(item_id),
  meta JSONB DEFAULT '{}'::jsonb
);

SELECT create_hypertable('events', 'ts', if_not_exists => TRUE);

-- Smart-Meter Zeitreihen
CREATE TABLE IF NOT EXISTS smart_meter_readings (
  meter_id TEXT NOT NULL,
  ts TIMESTAMPTZ NOT NULL,
  consumption_kw DOUBLE PRECISION,
  production_kw DOUBLE PRECISION,
  voltage DOUBLE PRECISION,
  quality TEXT,
  PRIMARY KEY (meter_id, ts)
);

SELECT create_hypertable('smart_meter_readings', 'ts', if_not_exists => TRUE);

-- Börsenpreise
CREATE TABLE IF NOT EXISTS market_prices (
  market TEXT NOT NULL,
  product TEXT NOT NULL,
  ts TIMESTAMPTZ NOT NULL,
  price_eur_mwh DOUBLE PRECISION,
  volume DOUBLE PRECISION,
  PRIMARY KEY (market, product, ts)
);

SELECT create_hypertable('market_prices', 'ts', if_not_exists => TRUE);

-- Labels/Rewards für Recommender
CREATE TABLE IF NOT EXISTS labels (
  user_id UUID REFERENCES users(user_id),
  item_id UUID REFERENCES items(item_id),
  ts TIMESTAMPTZ DEFAULT now(),
  reward DOUBLE PRECISION NOT NULL,
  reason TEXT,
  PRIMARY KEY(user_id, item_id, ts)
);

-- Metadaten für Vektor-Chunks (eigentliche Vektoren in Qdrant)
CREATE TABLE IF NOT EXISTS item_chunks (
  chunk_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  item_id UUID REFERENCES items(item_id),
  chunk_idx INT NOT NULL,
  text TEXT NOT NULL,
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Hilfsindizes
CREATE INDEX IF NOT EXISTS idx_items_tags ON items USING GIN (tags);
CREATE INDEX IF NOT EXISTS idx_events_user_ts ON events(user_id, ts DESC);
CREATE INDEX IF NOT EXISTS idx_chunks_item ON item_chunks(item_id);
```

---

## 3) API (FastAPI) – RAG, Ingest, Recommend (Minimalbeispiel)

Verzeichnis: `api/` → `Dockerfile`, `requirements.txt`, `main.py`

``

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

``

```
fastapi==0.115.0
uvicorn[standard]==0.30.6
psycopg[binary]==3.2.3
qdrant-client==1.10.1
httpx==0.27.2
pydantic==2.9.2
python-multipart==0.0.9
```

`` (stark verkürzt; produktiv bitte erweitern: Auth, Fehlerhandling, Retries)

```python
import io, uuid, json, hashlib
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
import httpx, psycopg
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
import os

DB_URL = os.getenv("DATABASE_URL")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
GEN_MODEL = os.getenv("GENERATE_MODEL", "llama3.1:8b-instruct")
COLLECTION = "chunks"

app = FastAPI()

# --- Clients ---
qdrant = QdrantClient(url=QDRANT_URL)

# Sicherstellen, dass die Collection existiert
try:
    qdrant.get_collection(COLLECTION)
except Exception:
    qdrant.recreate_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(size=768, distance=Distance.COSINE),
    )

# --- Hilfsfunktionen ---
async def embed(texts: List[str]):
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(f"{OLLAMA_URL}/api/embeddings", json={"model": EMBED_MODEL, "input": texts})
        r.raise_for_status()
        data = r.json()
        # Ollama gibt entweder {embedding: [...]} oder {embeddings: [{embedding: [...]}]} je nach Version
        if "embeddings" in data:
            return [e["embedding"] for e in data["embeddings"]]
        return [data["embedding"]]

async def generate(prompt: str):
    async with httpx.AsyncClient(timeout=None) as client:
        r = await client.post(f"{OLLAMA_URL}/api/generate", json={"model": GEN_MODEL, "prompt": prompt, "stream": False})
        r.raise_for_status()
        return r.json().get("response", "")

async def tika_extract(file_bytes: bytes, filename: str) -> str:
    async with httpx.AsyncClient(timeout=120) as client:
        headers = {"Content-Disposition": f"attachment; filename={filename}"}
        r = await client.put("http://tika:9998/tika", content=file_bytes, headers=headers)
        r.raise_for_status()
        return r.text

# --- Schemas ---
class AskReq(BaseModel):
    question: str
    top_k: int = 6
    filters: Optional[dict] = None  # z.B. {"source": "co2_reg"}

class RecommendReq(BaseModel):
    user_id: Optional[str] = None
    top_k: int = 10

# --- Endpunkte ---
@app.post("/ingest/doc")
async def ingest_doc(file: UploadFile = File(...), kind: str = Form("document"), source: str = Form("upload")):
    raw = await file.read()
    text = await tika_extract(raw, file.filename)
    sha256 = hashlib.sha256(raw).hexdigest()

    # Split naive (für MVP; produktiv: token-basiert + Overlap)
    CHUNK_SIZE = 1200
    chunks = [text[i:i+CHUNK_SIZE] for i in range(0, len(text), CHUNK_SIZE) if text[i:i+CHUNK_SIZE].strip()]

    # DB: items + item_chunks
    async with psycopg.AsyncConnection.connect(DB_URL) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO items(kind, source, title, sha256)
                VALUES (%s, %s, %s, %s)
                RETURNING item_id
                """,
                (kind, source, file.filename, sha256)
            )
            (item_id,) = await cur.fetchone()
            chunk_ids = []
            for idx, c in enumerate(chunks):
                await cur.execute(
                    """
                    INSERT INTO item_chunks(item_id, chunk_idx, text)
                    VALUES (%s, %s, %s) RETURNING chunk_id
                    """,
                    (item_id, idx, c)
                )
                (chunk_id,) = await cur.fetchone()
                chunk_ids.append((chunk_id, c))
            await conn.commit()

    # Embeddings + Qdrant
    vectors = await embed([c for (_, c) in chunk_ids])
    points = [
        PointStruct(id=str(cid), vector=v, payload={"item_id": str(item_id), "chunk_idx": i})
        for i, ((cid, _), v) in enumerate(zip(chunk_ids, vectors))
    ]
    qdrant.upsert(collection_name=COLLECTION, points=points)
    return {"item_id": str(item_id), "chunks": len(points)}

@app.post("/rag/ask")
async def rag_ask(req: AskReq):
    # Optional Filter
    qfilter = None
    if req.filters:
        conditions = [FieldCondition(key=k, match=MatchValue(value=v)) for k, v in req.filters.items()]
        qfilter = Filter(must=conditions)

    # Query-Embedding
    [qvec] = await embed([req.question])
    hits = qdrant.search(collection_name=COLLECTION, query_vector=qvec, limit=req.top_k, query_filter=qfilter)

    # Kontext zusammensetzen
    ctx = []
    chunk_ids = []
    for h in hits:
        payload = h.payload or {}
        cid = h.id
        chunk_ids.append(cid)
        ctx.append(f"[chunk {cid}] {payload}")

    # eigentlichen Text aus DB holen
    texts = []
    async with psycopg.AsyncConnection.connect(DB_URL) as conn:
        async with conn.cursor() as cur:
            for cid in chunk_ids:
                await cur.execute("SELECT text FROM item_chunks WHERE chunk_id = %s", (uuid.UUID(str(cid)),))
                row = await cur.fetchone()
                if row:
                    texts.append(row[0])

    context = "\n\n".join(texts)
    prompt = (
        "Du bist eine Expertin für Antifragilität in der Energiewirtschaft. "
        "Beantworte auf Deutsch, zitiere relevante Passagen mit [chunk ID]. "
        "Wenn unsicher, sage es explizit.\n\n"
        f"Frage: {req.question}\n\nKontext:\n{context}\n\nAntwort:"
    )
    answer = await generate(prompt)
    return {"answer": answer, "chunks_used": [str(c) for c in chunk_ids]}

@app.post("/recommend")
async def recommend(req: RecommendReq):
    # MVP: content-basiert über zuletzt gesehene Chunks des Nutzers (oder Fallback: populär)
    user_id = req.user_id
    seed_texts = []
    async with psycopg.AsyncConnection.connect(DB_URL) as conn:
        async with conn.cursor() as cur:
            if user_id:
                await cur.execute(
                    """
                    SELECT ic.text
                    FROM events e
                    JOIN item_chunks ic ON ic.item_id = e.item_id
                    WHERE e.user_id = %s AND e.type IN ('view','click')
                    ORDER BY e.ts DESC LIMIT 5
                    """,
                    (uuid.UUID(user_id),)
                )
                for r in await cur.fetchall() or []:
                    seed_texts.append(r[0])
            if not seed_texts:
                await cur.execute("SELECT text FROM item_chunks ORDER BY created_at DESC LIMIT 5")
                for r in await cur.fetchall() or []:
                    seed_texts.append(r[0])

    if not seed_texts:
        return {"items": []}

    # Query-Vektor = Mittelwert der Seed-Embeddings
    vecs = await embed(seed_texts)
    avg = [sum(col)/len(vecs) for col in zip(*vecs)]
    hits = qdrant.search(collection_name=COLLECTION, query_vector=avg, limit=req.top_k)

    # Rückgabe: Item-IDs + Chunk-IDs
    out = []
    for h in hits:
        payload = h.payload or {}
        out.append({"chunk_id": str(h.id), "score": h.score, "payload": payload})
    return {"items": out}
```

---

## 4) Beispiele: Smart‑Meter & Börsenpreise laden (Batch‑Jobs, Platzhalter)

Datei: `jobs/load_prices.py` (vereinfacht)

```python
import csv, psycopg, sys
DB = "postgresql://ki:ki@localhost:5432/ki"
with psycopg.connect(DB) as conn, conn.cursor() as cur:
    with open(sys.argv[1]) as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            cur.execute(
              """
              INSERT INTO market_prices(market, product, ts, price_eur_mwh, volume)
              VALUES (%s,%s,%s,%s,%s)
              ON CONFLICT (market, product, ts) DO UPDATE
              SET price_eur_mwh=EXCLUDED.price_eur_mwh, volume=EXCLUDED.volume
              """,
              (r["market"], r["product"], r["ts"], float(r["price"]), float(r.get("volume",0) or 0))
            )
        conn.commit()
```

---

## 5) Telemetrie & Online‑Lernen (Skeleton)

- **Events erfassen**: Aus eurer Software bei Klick/Ansicht/„Hilfreich“ POST auf `/events` (Endpunkt analog zu `/ingest/doc` ergänzen).
- **Bandit**: Kleine Tabelle `bandit_state(model TEXT, theta JSONB, updated_at)`; Update job minütlich (Thompson/LinUCB), Ranking-Layer in `/recommend` zwischenschalten.
- **Evaluation**: CTR, Time‑to‑Answer, Abbruchrate als Timeseries in `events` (Grafana‑Dashboard).

---

## 6) Betriebsnotizen

- **Indices**: Timescale Continuous Aggregates für 1‑min/15‑min‑Fenster, Qdrant HNSW‑Params (M, ef) je nach Datengröße.
- **Backups**: Postgres (pg\_dump + WAL), Qdrant Snapshots, MinIO Versioning.
- **Auditing**: Jede RAG‑Antwort speichert `chunks_used`, Prompt, Model‑Version.
- **Security**: Netzwerk nur intern, API hinter Reverse‑Proxy, RBAC in Postgres.

---

## 7) Nächste sinnvolle Ausbaustufen

- Hybrid‑Retrieval (BM25 via OpenSearch/pg\_trgm) und Re‑Ranker (kleiner Cross‑Encoder lokal).
- Regulierungskorpus: Crawler + Normalisierung + Effektivdaten → gezielte Filter im Retriever.
- Feature Store (z. B. Feast) für konsistente Online/Offline‑Features.
- Chaos‑Tests: synthetische Preisschocks und Datenlücken in CI einbauen.

```
```
