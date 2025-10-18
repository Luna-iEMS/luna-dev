# Luna-iEMS Masterplan – Technischer Entwicklungsplan

## Ziel
Ein modulares, lokal lauffähiges Energiemanagement-System mit integriertem KI-Stack: RAG, Zeitreihenanalyse, Recommendation Engine und Monitoring. Vollständig containerisiert, offline-fähig und auf industrielle Datenanbindung (Smart Meter, Marktpreise, Regulierungsdokumente) ausgelegt.

---

## Phase 0 – Foundation & Infrastruktur
**Ziel:** Vollständige lokale Entwicklungsumgebung mit persistenter Datenhaltung und Container-Orchestrierung.

### Tasks
- [ ] Docker-Setup (Compose + ENV-Management + Volumes)
- [ ] Netzwerke für API, DB, Cache, Vector, LLM
- [ ] Volume-Struktur (db, logs, vector, cache, data)
- [ ] Healthchecks & Logging (FluentBit / Loki-Schnittstelle)
- [ ] Makefile für lokale Dev-Commands (build, down, clean, reset)

### Erfolgskriterium
`docker compose up -d` startet das komplette System (DB, Qdrant, Ollama, API, Cache) ohne Fehlermeldung.

---

## Phase 1 – Core Backend (API + Datenbanken)
**Ziel:** Aufbau des Datenmodells und einer API-Schnittstelle für Ingest, Query & Verwaltung.

### Tasks
- [ ] Postgres + TimescaleDB Schema: Nutzer, Items, Events, Market Data, Smart Meter
- [ ] FastAPI-Struktur mit modularen Routen (Ingest, Query, Admin)
- [ ] ORM-Anbindung (SQLAlchemy oder psycopg)
- [ ] Qdrant-Anbindung & Basisoperationen (create_collection, upsert, search)
- [ ] MinIO für File Storage (PDFs, DOCX, CSV)

### Erfolgskriterium
API kann Text- oder PDF-Dokumente empfangen, extrahieren und in Qdrant/DB speichern.

---

## Phase 2 – KI-Layer (RAG + Embedding + LLM)
**Ziel:** Ollama-Integration für lokale Embeddings und Textgenerierung.

### Tasks
- [ ] Ollama-Container + API (11434) konfigurieren
- [ ] Modelle: `nomic-embed-text`, `llama3.1:8b-instruct`
- [ ] Embedding-Endpoint (`/embed`) + Vector Upsert in Qdrant
- [ ] RAG-Endpoint (`/rag/ask`) mit Query-Embedding, Vector-Suche und Generierung
- [ ] Kontextaufbau (Chunk-Rekonstruktion + Prompt-Ketten)

### Erfolgskriterium
`POST /rag/ask` gibt sinnvolle, kontextbezogene Antworten aus lokalem Wissensspeicher zurück.

---

## Phase 3 – Data Layer (Smart Meter & Marktpreise)
**Ziel:** Zeitreihendaten laden, speichern und für Vorhersagen/Analysen nutzbar machen.

### Tasks
- [ ] TimescaleDB Hypertables (market_prices, smart_meter_readings)
- [ ] Batch-Ladejobs (CSV/JSON Ingest via Python)
- [ ] API-Endpunkte `/data/load` und `/data/query`
- [ ] Validierung der Daten (Outlier Detection, Format Checks)
- [ ] Integration in RAG-Kontext (z. B. „Erkläre Preisverlauf von EPEX Strom“)

### Erfolgskriterium
Zeitreihen-APIs liefern konsistente Werte aus DB, Queries sind performant (<200ms für 1 Jahr Daten).

---

## Phase 4 – Intelligence Layer (Recommendation + Learning)
**Ziel:** Aufbau einer adaptiven Empfehlungs-Engine (Content-based & Feedback-Learning).

### Tasks
- [ ] User Event Logging (`/events` Endpoint)
- [ ] Content-basierte Empfehlungen via Embeddings (Qdrant Similarity Search)
- [ ] Bandit-Modul (LinUCB/Thompson Sampling)
- [ ] Online-Learning Loop (Feedback -> Reward -> Update)
- [ ] Integration mit RAG (z. B. „Empfohlene Dokumente zu…“)

### Erfolgskriterium
`/recommend` liefert adaptive Empfehlungen basierend auf Benutzerinteraktion und Vektorräumen.

---

## Phase 5 – Monitoring, Admin & Observability
**Ziel:** Systemgesundheit, Datenflüsse und Modellmetriken sichtbar machen.

### Tasks
- [ ] Admin Dashboard (FastAPI + Tailwind/React Frontend optional)
- [ ] Systemmetriken (Prometheus Exporter, Timescale Continuous Aggregates)
- [ ] Log-Collector (FluentBit + MinIO Logs)
- [ ] Alerts & Error Handling (Healthchecks + E-Mail/Webhook)
- [ ] Model Audit Log (Prompt, Antwort, Modell, Chunk-IDs)

### Erfolgskriterium
Dashboard zeigt Status aller Container + Antwortlatenz + Datenvolumen in Echtzeit.

---

## Phase 6 – Sicherheit, Deployment & Skalierung
**Ziel:** Absicherung, Backup-Strategien und optionale Cloud/Edge-Bereitstellung.

### Tasks
- [ ] Authentifizierung (JWT oder API-Key)
- [ ] Rollen & Berechtigungen (Admin, Analyst, User)
- [ ] Backup-Strategie (Postgres WAL, Qdrant Snapshots, MinIO Versioning)
- [ ] CI/CD (GitHub Actions + Tests + Image Builds)
- [ ] Edge-/Clusterfähigkeit (Docker Swarm oder k8s optional)

### Erfolgskriterium
System kann sicher und reproduzierbar auf mehreren Nodes deployt werden.

---

## Arbeitsweise
- **Bigbang:** Foundation bis Phase 2 in einem durchgehenden Sprint (komplettes lokales MVP).  
- **Iterativ:** Ab Phase 3 modulweise Erweiterung mit Tests & Telemetrie.
- **Kommunikation:** Jede Phase enthält Taskliste mit klaren Zielen; nach Abschluss → Integrationstest + Review.
- **Rollen:**
  - Du: Product Lead & Architekt (entscheidest über Features & Prioritäten)
  - Ich: Entwicklerteam (Backend, Infra, DataOps, LLM-Integration)

---

## Nächste Schritte
1. Phase 0 starten: Verzeichnisstruktur + Compose + Makefile
2. Danach Phase 1 vorbereiten: DB-Schema & API-Basis
3. Parallel Teststrategie aufsetzen (pytest, API-Checks)

