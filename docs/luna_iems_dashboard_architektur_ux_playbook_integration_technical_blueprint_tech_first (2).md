# Luna-IEMS – Technischer Gesamtplan & Entwicklungsphasen

## Überblick
Luna-IEMS ist eine modulare, containerisierte Plattform für KI-basierte Energie- und Informationssysteme. Ziel ist die Kombination von Echtzeitdaten, Wissensmanagement (Dokumente, Playbook), RAG-gestützter Analyse, Simulation und Entscheidungsunterstützung – vollständig lokal lauffähig oder hybrid skalierbar.

Die Architektur ist auf **Isolation pro Kunde**, **optionales anonymisiertes Meta-Learning**, sowie **robuste, resiliente Datenhaltung** ausgelegt. Luna selbst fungiert als interaktiver, lernender Assistent innerhalb des Kundendashboards.

---

## Phasenübersicht & Hauptaufgaben

### **Phase 1 – Core Setup & Container-Infrastruktur**
**Ziele:** Grundlegende Systemarchitektur und Services aufsetzen.
- Docker-Setup mit Compose (Postgres/Timescale, Qdrant, Ollama, Redis, MinIO)
- Netzwerkdefinition und Portmanagement (keine Konflikte, dynamische Zuweisung)
- Healthchecks, persistente Volumes, Backups
- Logging & Fluent-Bit Integration
- Basis `.env` Struktur (lokal/dev/prod)

### **Phase 2 – API Layer & Embeddings-Pipeline**
**Ziele:** Zentrale REST-API (FastAPI) für Dokumenten- und Wissensmanagement.
- Endpunkte: `/ingest/doc`, `/rag/ask`, `/recommend`, `/system/status`
- Ingest & Chunking via Apache Tika + PyMuPDF + python-docx
- Embedding-Erzeugung über Ollama (`nomic-embed-text`)
- Speicherung in Qdrant + relationaler Meta-DB
- Vollständige Testabdeckung für Upsert, Query, Search

### **Phase 3 – Data Layer (Smart Meter & Marktpreise)**
**Ziele:** Zeitreihen-Simulation und spätere Integration realer Schnittstellen.
- Tabellen: `smart_meter_readings`, `market_prices`, `events`
- Batch-Skripte für simulierte Datenfeeds (CSV/JSON-Input)
- Zeitreihenaggregationen in Timescale (1-min/15-min Window)
- Anbindung an API `/data/stream` und `/data/summary`
- Vorbereitung externer Konnektoren (API-Endpoints, MQTT, OPC-UA)

### **Phase 4 – Luna Intelligence & RAG Layer**
**Ziele:** Aufbau des zentralen Luna-Assistenzmoduls (RAG + Memory + Context).
- Interne Wissensbasis (Playbook, Dokumente, Anweisungen)
- Vektorbasierte Retrieval-Engine (Qdrant)
- Prompt-Engine + Persona (leicht sarkastisch, britischer Humor, empathisch)
- Adaptive Prompt Templates basierend auf Kontext (Admin vs. Kunde)
- Selbstüberwachung (Memory, Source Logging, „Warum antworte ich so“)

### **Phase 5 – Monitoring, Admin & Observability**
**Ziele:** Transparente Überwachung und Administrationsfunktionen.
- Admin Dashboard (Monitoring, Uploads, Kontrolle, KI-Feeding)
- Kundendashboard (Insights, RAG-Ergebnisse, Simulationen)
- Systemstatusanzeige (API/DB/Qdrant/Ollama/Cache)
- Metrics via Grafana/Prometheus
- Audit Logs + KI-Nutzungsprotokollierung

### **Phase 6 – Frontend (Kundendashboard & UX)**
**Ziele:** UI/UX auf Enterprise-Niveau mit klarer Informationsarchitektur.
- Technologie: React + Tailwind + shadcn/ui + Recharts
- Layout: Dark/Light Mode (Dark default)
- Hauptbereiche:
  1. **Luna Insight Panel** – Konversation & Analyse
  2. **Playbook View** – strukturierte Darstellung der Knowledge Base
  3. **Data Insights** – Zeitreihen, Marktpreise, Trends
  4. **Support & Hilfe** – generiert durch Luna, kontextsensitiv
  5. **Profil & Einstellungen** – Nutzer, Sprache, Layout, AI-Modus
- Footer: Version, Datenschutz, Impressum, API-Status

### **Phase 7 – Simulation & Recommendation Engine**
**Ziele:** Entscheidungsunterstützung durch simulierte oder reale Daten.
- Implementierung von Simulationen (CO₂, Netzlast, Preisentwicklung)
- Online Learning (Bandit-Recommender, LinUCB, Thompson Sampling)
- Integration mit Event-Datenbank
- Ausgabe über Dashboard + RAG-Erklärung

### **Phase 8 – Security, Deployment & Skalierung**
**Ziele:** Produktionsreife Architektur mit modularer Skalierbarkeit.
- Authentifizierung via OAuth2 + JWT
- Rollenmodell: Admin / Kunde / Service
- TLS/SSL Setup, Reverse Proxy (Caddy/Nginx)
- Snapshots & Backup-Scheduling
- Optional: Anonymisiertes Meta-Learning (Shared Knowledge)

---

## Technische Architektur – Zusammenfassung

**Core Services:**
- Postgres/TimescaleDB → strukturierte & Zeitreihendaten
- Qdrant → semantische Suche, Embeddings
- Redis → Cache & Sessionmanagement
- MinIO → Objektspeicher für Dokumente
- Ollama → lokale LLM/Embedding Engine

**API (Python/FastAPI):**
- REST-basierte Schnittstellen für Daten, Ingest & Abfragen
- Interner Zugriff auf Qdrant, Ollama, Postgres
- Asynchrone Verarbeitung via asyncio & HTTPx

**Frontend:**
- React-basiertes Dashboard mit Realtime-Kommunikation (WebSocket/EventStream)
- Dynamische Darstellung von Luna-Antworten & Systemstatus

**Observability:**
- Fluent Bit → Log Forwarding
- Prometheus/Grafana → Metriken, Alerts
- Qdrant/DB Health Checks

---

## Luna – Technische & sprachliche Definition

**Persona:**
- Tonalität: empathisch, charmant, leicht sarkastisch, britischer Humor
- Stil: präzise, kontextsensitiv, situationsbewusst
- Verhalten: reagiert adaptiv auf Nutzerrolle (Admin/Kunde)
- Lernverhalten: kombiniert lokales Kontextlernen mit anonymisiertem Metawissen

**Technische Umsetzung:**
- Prompt Engine mit dynamischen Persona-Templates
- Knowledge Injection (internes Playbook + Kundendaten)
- Memory Layer (User-Kontext, Historie, Korrekturen)

---

## Nächste Schritte (Sprint 0 → Sprint 1)

1. Repositories & CI/CD Setup
2. Lokale Dev-Umgebung (Docker Compose Dev)
3. Datenbankmigrationen & Seed Scripts
4. API Grundgerüst + Test-Routen
5. Luna Persona Engine (Template, PromptHandler)
6. Kundendashboard Grundlayout (Dark Mode + Panel-Struktur)
7. Admin-Interface Mock

---

**Ziel:** Ein modulares, sich selbst erklärendes System, bei dem Luna die Schnittstelle zwischen Mensch, Daten und KI bildet – technisch robust, emotional ansprechend und architektonisch elegant.

