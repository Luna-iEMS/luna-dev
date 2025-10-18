# Luna-IEMS Technical Masterplan & Sprint Overview

## Epic 1: Core Infrastructure & Environment Setup
**Ziel:** Stabile lokale & containerisierte Umgebung (Docker Compose), isoliert pro Kunde.

**Tasks:**
- [ ] Docker Compose Multi-Service Setup (API, DB, Qdrant, Ollama, Cache, Worker)
- [ ] Dev/Prod Environment Variables (.env Struktur, Ports standardisieren)
- [ ] Netzwerkisolation pro Tenant (Kundeninstanz)
- [ ] Healthchecks, Logging & Fluentbit Integration
- [ ] Volume-Struktur: persistente Datenhaltung für DB, Cache, Logs, Qdrant
- [ ] Testing Environment (lokal lauffähig mit Dummy Data)

**Labels:** ⚙️ DevOps / Docker / Infrastructure

---

## Epic 2: Data Layer (Simulierte Smart Meter & Marktpreise)
**Ziel:** Zeitreihen + Marktdatenstrukturen bereitstellen, Simulation bis reale Schnittstellen verfügbar sind.

**Tasks:**
- [ ] TimescaleDB Schema (Smart-Meter, Marktpreise, Events, Labels, Users)
- [ ] Python Simulation Scripts (`simulate_smart_meter.py`, `simulate_market_prices.py`)
- [ ] ETL Jobs (Batch-Import, Streaming via Redpanda optional)
- [ ] API Endpoints für Datenabfragen & Aggregationen
- [ ] Hybrid-Adapter: Spätere Integration echter Messsysteme via API / MQTT / OPC-UA

**Labels:** 💾 Data / SQL / Simulation / Timescale

---

## Epic 3: Knowledge Layer (RAG & Dokumenten-Ingest)
**Ziel:** KI-Wissensspeicher mit Embeddings, Textisierung und Qdrant-Vektorsuche.

**Tasks:**
- [ ] Apache Tika Integration (Text Extraction für PDF, DOCX, MD, TXT)
- [ ] Ollama Embedding Pipeline (nomic-embed-text)
- [ ] Qdrant Collection Schema (`luna_knowledge`)
- [ ] Upload Endpoint `/ingest/doc` (File → Text → Chunk → Embed → Upsert)
- [ ] RAG Endpoint `/rag/ask` (LLM + Kontext aus Qdrant & DB)
- [ ] DB-Sync für Items, Chunks, Metadaten
- [ ] Dokumente-Verwaltung (Admin UI: Upload, Reindex, Delete)

**Labels:** 🧠 KI / Qdrant / FastAPI / Ollama

---

## Epic 4: Luna Core Intelligence
**Ziel:** Lunas Kernintelligenz, Verhalten & API-Integration.

**Tasks:**
- [ ] Luna Persona Definition (Ton, Verhalten, Sprachstil)
- [ ] Context Memory Layer (Kundenkontext + Chatkontext speichern)
- [ ] Adaptive Antworten (leicht sarkastisch, britisch-angehaucht, empathisch)
- [ ] KI-Antwortarchitektur (Prompt Templates, Chain-of-Thought Steuerung)
- [ ] Feedback Loop: Kundeninteraktion → Telemetrie → Retraining Signal

**Labels:** 🧠 LLM / Prompt Engineering / Persona Design

---

## Epic 5: Monitoring, Admin & Observability
**Ziel:** System-Monitoring, Admin-Dashboard und KI-Datenpflege.

**Tasks:**
- [ ] Admin Dashboard (Systemstatus, Logs, CPU/Memory, API-Health)
- [ ] KI Management UI (Dokumenten-Uploads, Trainingstatus, Qdrant Collections)
- [ ] Prometheus + Grafana Setup
- [ ] Logging Dashboard (Fluentbit → Loki → Grafana)
- [ ] Audit Logging (wer hat wann was eingespielt / abgerufen)

**Labels:** ⚙️ Observability / Monitoring / Admin Tools

---

## Epic 6: Customer Dashboard (Luna UI/UX)
**Ziel:** Interaktive Kundenoberfläche im Enterprise-Stil (modern, dunkel/hell, reaktiv, intuitiv).

**Tasks:**
- [ ] Layout Design (Dark Mode Default, Light Mode optional)
- [ ] Luna Insight Panel (Personalisierte Willkommensseite mit Systemstatus & Empfehlungen)
- [ ] Dashboard Seitenstruktur:
  - Home: aktuelle KPIs, Systemstatus, Chat-Eingang
  - Marktpreise: Grafische Analyse, Historie, Vergleich
  - Smart Meter: Echtzeit-Daten, Trends, Simulation
  - Playbook: Visuelle Darstellung von Regeln/Strategien, interaktiv
  - Support: Luna Helpdesk mit generierten Hilfetexten
- [ ] Footer mit Systeminfo, Impressum, Datenschutz, Support-Link
- [ ] Reaktives Frontend (React + Tailwind + API)

**Labels:** 🖥️ Frontend / UI / UX / React

---

## Epic 7: Security & Tenant Isolation
**Ziel:** Saubere Mandantentrennung, Auth & Datenhoheit pro Kunde.

**Tasks:**
- [ ] TenantID in allen relevanten Tabellen & API-Aufrufen
- [ ] Auth via JWT (Admin / Customer)
- [ ] Optional: OpenID/OAuth2 Integration
- [ ] Datenverschlüsselung (DB + Volume)
- [ ] Backup & Restore Konzept

**Labels:** 🔒 Security / Auth / Multi-Tenant

---

## Epic 8: Future Expansion & AI-Orchestration
**Ziel:** Vorbereitung auf Hybrid-Learning, globale Wissensbasis & modulare KI-Erweiterungen.

**Tasks:**
- [ ] Zentrale Knowledge Sync Engine (anonymisierte Metadaten)
- [ ] Hybrid Learning Pipeline (lokal + global anonymisiert)
- [ ] Task Orchestrator (Celery + Redis Queue)
- [ ] Model Management Service (Model Versioning & Rollback)
- [ ] Luna Retraining Interface (Admin Only)

**Labels:** 🧠 ML Ops / Hybrid Learning / Scalability

---

## Infrastrukturüberlegungen
- Ports standardisieren (Qdrant 6333–6334, Ollama 11434, API 8000, DB 5432)
- Interne Netzwerke `luna-net` pro Kunde
- Einheitliche Healthchecks mit `curl -f` und Grace Periods
- Volumes mit klarer Struktur (`/data`, `/logs`, `/models`, `/storage`)
- Lokale vs. Cloud Deployments via Compose Profiles (local / prod)

---

## Dev Workflow
1. **Feature Branch** pro Task / Epic
2. **Lokales Testing:** `docker compose -f docker-compose.dev.yml up`
3. **Unit Tests & Integration Checks** (pytest + httpx)
4. **Automatisierte Build Pipeline** (optional später CI/CD)
5. **Sprint Review** = Feature Merge + Demo in lokaler Umgebung

---

## Zusammenfassung
Luna-IEMS wird als modulare, containerisierte Enterprise-AI-Plattform aufgebaut.
- Jede Kund:inneninstanz ist technisch isoliert.
- Die globale Luna-KI lernt anonymisiert und kontinuierlich.
- Fokus liegt auf Stabilität, Transparenz & Interaktivität.
- Designziel: Eine KI, die sich wie eine echte Teamkollegin anfühlt – charmant, pragmatisch, technisch brillant.

