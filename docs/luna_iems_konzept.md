# Luna-IEMS: Greenfield-Konzept

## Zielsetzung

Luna-IEMS (Intelligent Energy Management System) ist eine lokal oder hybrid betriebene Plattform für industrielle und kommunale Energiesteuerung. Sie kombiniert **KI-basierte Entscheidungslogik**, **zeitreihenbasierte Analytik** und **regelbasierte Steuerung** zu einem autonomen, antifragilen Energiemanagement-System.

Ziele:
- Echtzeit-Steuerung und Optimierung von Energieflüssen (PV, Speicher, Last, Netz)
- Integration von Smart-Metern, Preisdaten, Wettermodellen, IoT-Sensorik
- Wissensspeicher für Domänenwissen, Vorschriften und Entscheidungsmodelle
- Vollständige Offline- und On-Premise-Fähigkeit (Edge-Ready)

---

## Architektur (High-Level)

### Kernmodule
1. **Data Ingest Layer**
   - Smart-Meter, MQTT, CSV/REST-Importe
   - Parsing, Normalisierung, Speicherung in TimescaleDB
   - Dokument-Upload (Regulierungen, Reports, Notizen)

2. **Knowledge Layer**
   - Textisierung (Apache Tika)
   - Embeddings (Ollama / nomic-embed)
   - Vektorindex (Qdrant)
   - Ontologien, Metadaten, Tagging

3. **Decision Layer**
   - RAG-API (Retrieval-Augmented Generation)
   - Regelwerke (z. B. Netzdienlichkeit, Eigenverbrauchsoptimierung)
   - Agentenbasierte Steuerung (LangChain/Custom)
   - Reinforcement & Bandit-Learning für adaptive Steuerlogik

4. **Timeseries Intelligence**
   - TimescaleDB für Smart-Meter, Preise, Sensorik
   - Aggregationen, Anomalieerkennung, Vorhersagen (Prophet/ARIMA)

5. **User & Control Layer**
   - REST + WebSocket API (FastAPI)
   - Dashboard (Next.js / React)
   - Role-Based Access Control (RBAC)
   - Echtzeitüberwachung & Alerts (Prometheus/Grafana)

6. **Integration Layer (optional)**
   - Modbus, OPC-UA, MQTT
   - Externe Märkte (EPEX, ENTSO-E, Redispatch 2.0)

---

## Zieltechnologie-Stack

| Kategorie | Technologie | Begründung |
|------------|--------------|-------------|
| Containerisierung | Docker / Docker Compose | Reproduzierbare, portable Umgebung |
| API / Backend | FastAPI (Python) | Leichtgewichtig, async, KI-freundlich |
| Datenbank | TimescaleDB | Timeseries + SQL-Analytik |
| Vektorspeicher | Qdrant | Hochperformanter lokaler Vektorindex |
| Dokument-Parsing | Apache Tika | Bewährter Standard für Dokumentanalyse |
| Embeddings / LLM | Ollama (lokal) | Datenschutzkonform, on-prem Modelle |
| Caching / Queue | Redis | Schnelle Zwischenspeicherung und Tasks |
| Storage | MinIO | S3-kompatibel, lokal oder hybrid |
| Message Bus | Redpanda / Kafka | Optionale Skalierung / Event-Streaming |

---

## Entwicklungsphasen

### Phase 1 – Core Infrastructure (MVP)
- Docker Compose Umgebung (Postgres/Timescale, Qdrant, Ollama, API)
- Healthchecks, Logs, Volume Mounts
- API-Basis mit `/ingest/doc`, `/rag/ask`, `/recommend`
- Tests mit lokalem `sample.txt`

### Phase 2 – Daten- und Wissensschicht
- Smart-Meter- und Marktdatenimport (CSV, API)
- Volltext-Indizierung von Dokumenten
- Qdrant-Vektorisierung + Metadatenstruktur

### Phase 3 – Decision Layer
- RAG für regulatorische und technische Fragestellungen
- Regelbasierte Entscheidungsengine
- Adaptive Empfehlungen (Thompson/LinUCB Bandit)

### Phase 4 – Integration & Steuerung
- Echtzeitdatenströme (MQTT, Modbus)
- Steueragenten (z. B. Speicher-Ladung, Peak-Shaving)
- Manuelle und automatische Eingriffe über Dashboard

### Phase 5 – KI & Optimierung
- Vorhersagemodelle (Verbrauch, Preis, PV)
- Reinforcement Learning für Betriebsstrategien
- Chaos-Test und Selbstheilungsmechanismen

---

## Entwicklungsprinzipien

- **Local-First:** Vollständige Funktionsfähigkeit offline / Edge
- **Modularität:** Jeder Service isoliert, erweiterbar
- **Security by Design:** Keine Cloud-Abhängigkeit, TLS intern
- **Observability:** Logging, Tracing, Metrics integriert
- **Reproduzierbarkeit:** Infrastructure as Code + Versioned Data

---

## Geplante Artefakte

| Artefakt | Beschreibung |
|-----------|--------------|
| `docker-compose.yml` | Produktionsnahe lokale Umgebung |
| `docker-compose.dev.yml` | Entwicklerumgebung mit Hot-Reload |
| `api/` | FastAPI-Service inkl. Qdrant & PG-Anbindung |
| `migrations/` | SQL-Skripte für Basisschema |
| `docs/` | Architekturdiagramme, Datenfluss, API-Referenz |
| `jobs/` | Batch-Importer für Preisdaten, Smart-Meter etc. |
| `frontend/` | Web-Interface (Dashboard, Control UI) |

---

## Erfolgskriterien

- Lokale Umgebung startbar mit `docker compose up`
- Dokumente, Daten und Zeitreihen ingestierbar
- RAG-API liefert konsistente Antworten
- Basale Steuer- und Empfehlungsschicht lauffähig
- CI-Testpipeline mit Unit-/Integrationstests
- Monitoring-Stack (Prometheus + Grafana) funktionsfähig

---

## Nächste Schritte

1. Bootstrap der Greenfield-Struktur (Ordner + Compose)
2. API-Grundgerüst + Healthchecks
3. Qdrant/PG-Integration testen
4. Dokument-Ingest & Embedding-Pipeline implementieren
5. Smart-Meter-Import & Timescale-Daten prüfen
6. Minimal-Dashboard + Authentifizierung
7. Logging & Metriken aktivieren

