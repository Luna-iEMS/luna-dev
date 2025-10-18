# Luna-IEMS – Technischer Entwicklungsplan

## Zielsetzung
Luna-IEMS (Intelligent Energy Management System) ist eine lokale, KI-gestützte Plattform zur Verarbeitung, Analyse und Automatisierung von Energiedaten, Dokumenten und Handlungsempfehlungen. Das System kombiniert Vektor-Datenbanken, Zeitreihen, lokale LLMs (Ollama) und modulare APIs zu einer skalierbaren On-Premise-Architektur.

---

## Phase 1 – Architektur & Infrastruktur
### Ziel
Aufbau der Grundinfrastruktur (Container, Netzwerke, Services) für eine saubere, reproduzierbare Entwicklungs- und Produktionsumgebung.

### Kernkomponenten
- **Docker Compose (v3.9)**
  - Postgres/TimescaleDB (relationale & Zeitreihen-Daten)
  - Qdrant (Vektor-Datenbank)
  - Ollama (LLM & Embeddings)
  - MinIO (Dokumenten-Speicher)
  - API (FastAPI)
  - Redpanda (Event-Streaming, später optional)
- **Netzwerk**: Isoliertes Backend-Netz (kein externer Zugriff)
- **Volumes**: Persistenz für Daten, Logs und Modelle

### Ergebnis
Funktionierende Basisumgebung (docker-compose up) mit Healthchecks und Trennung von Entwicklungs- und Produktionsprofilen.

---

## Phase 2 – Data Foundation (SQL, Vektor, Dokumente)
### Ziel
Erstellung des Datenmodells und Aufbau der Kernpersistenz.

### Inhalte
- **SQL (TimescaleDB)**
  - Nutzer, Items, Events, Smart-Meter-Readings, Marktpreise, Labels, Item-Chunks
- **Qdrant**
  - Collection: `chunks`
  - Embeddings-Config: COSINE, dim=768
- **MinIO**
  - Bucket-Struktur: `/docs/raw`, `/docs/processed`

### Ergebnis
Einheitliches Datenfundament mit synchronisierter Metadatenstruktur (SQL ↔ Qdrant ↔ MinIO).

---

## Phase 3 – Data Layer (Simulation Smart Meter & Marktpreise)
### Ziel
Bereitstellung realistischer Simulationsdaten zur Entwicklung, bevor externe Schnittstellen existieren.

### Inhalte
- **Generatoren**:
  - `simulate_smart_meter.py`: zufällige Zeitreihen für Verbrauch/Produktion, Noise, Tagesmuster
  - `simulate_market_prices.py`: einfache Preiszeitreihe mit saisonalen Mustern
- **API-Integration**:
  - Endpunkte `/data/smart_meter` & `/data/market_prices`
  - Spätere Ablösung durch Live-Schnittstellen (REST, MQTT, OPC-UA etc.)

### Ergebnis
Funktionsfähiger Datengenerator für synthetische Testdaten mit realistischen Mustern und einfacher Austauschbarkeit.

---

## Phase 4 – Knowledge & RAG Layer
### Ziel
Implementierung der Kern-Intelligenz: Dokumentenverarbeitung, Vektorisierung und Abfrage (RAG).

### Inhalte
- **Dokumenten-Ingest** (PDF, DOCX, TXT)
  - Tika → Textisierung
  - Chunking → Embeddings → Qdrant
  - Metadaten → SQL
- **RAG-Endpunkt** `/rag/ask`
  - Kontextsuche in Qdrant
  - Kontextverknüpfung mit SQL-Daten
  - Antwortgenerierung über Ollama (lokal, streaming)
- **Embedding Model**: `nomic-embed-text`
- **Generative Model**: `llama3.1:8b-instruct`

### Ergebnis
Vollständig lokaler RAG-Pipeline mit Knowledge Store und semantischer Suche.

---

## Phase 5 – Monitoring, Admin & Observability
### Ziel
Verwaltung, Transparenz und Steuerung der Plattform durch zwei Ebenen:

#### 1️⃣ Kundendashboard (Frontend)
- Darstellung von:
  - Simulierten Schnittstellen (Smart Meter, Marktpreise)
  - Aktuellen RAG-Playbooks (Handlungsempfehlungen, Analysen)
  - Verlauf und Ergebnisse (Charts, KPIs, Trends)
- **UX/UI-Anforderungen**:
  - Enterprise-Design, clean, interaktiv
  - Konsistente Farbwelt (Luna-Tonalität)
  - Kontextbezogene Erklärungen (Tooltips, Hilfekarten)

#### 2️⃣ Admin-Dashboard
- Zugriff nur für Monika (Root)
- Funktionen:
  - Dokumente & Daten hochladen (Ingest)
  - Lernprozesse starten/stoppen
  - Logs, Events, Metriken einsehen
  - Systemstatus & Ressourcenauslastung (via Prometheus + Grafana)

### Ergebnis
Klare Trennung zwischen Benutzer- und Administratoransicht mit strukturierter Datenvisualisierung.

---

## Phase 6 – Adaptive Learning & Feedback System
### Ziel
Luna soll aktiv aus Nutzung und Feedback lernen – sicher, lokal, kontrolliert.

### Architektur
1. **Admin-Lernen (explizit)** – Wissen & Dokumente → KI
2. **Kunden-Lernen (passiv, anonymisiert)** – Nutzung & Events → Statistik

### Datenfluss
- Events (view, click, ask, feedback) → `events`-Tabelle (Timescale)
- Lern-Jobs (Python):
  - Nutzungsanalyse
  - Relevanzgewichtung der Dokumente
  - Embedding-Recalibration in Qdrant
- Feedback-API (👍/👎, Zeitmessung, Topic-Tracking)

### Steuerung über Admin-Dashboard
- Lernzyklen manuell oder automatisch
- Auditing (wer/was wurde gelernt)
- Versionskontrolle für Modelle & Prompts

### Ergebnis
Luna wird „adaptiv“: lernt aus Verhalten und Admin-Wissen, verbessert sich iterativ ohne Cloud.

---

## Phase 7 – Erweiterbarkeit & Skalierung
### Ziel
Langfristige Basis für Edge-, Cloud- oder Hybridbetrieb.

### Optionen
- Multi-Agent-Komponenten (Regelwerke, Optimierer, Prognosen)
- Externe Connectors (SCADA, ENTSO-E API, Redis Streams)
- Federation zwischen mehreren Lunas (Wissensaustausch)
- Optionaler Cloud-Sync für zentralisiertes Monitoring

### Ergebnis
Skalierbare, erweiterbare Architektur mit klaren Schnittstellen und sicherem Deployment-Modell.

---

## Nächste Schritte
1. Implementierung **Phase 1–2 (Infrastruktur + Data Foundation)** lokal.
2. Simulation der **Phase 3 (Smart Meter & Marktpreise)**.
3. Aufbau der **API & Admin-Oberfläche** für Dokument-Ingest & Monitoring.
4. Iterativer Aufbau von **Phase 6 (Adaptive Learning)**.

---

## Dokumentation & DevOps
- Versionsverwaltung: Git + SemVer
- CI/CD: Build, Test, Deploy via GitHub Actions / Jenkins
- Codequalität: Black, Ruff, MyPy
- Tests: Pytest (Unit + Integration)
- Deployment: Docker Compose / Kubernetes (später)

---

> **Luna-IEMS steht für adaptive Intelligenz in sicherer, lokaler Architektur.**  
> Jeder technische Baustein ist auf Erweiterbarkeit, Erklärbarkeit und Vertrauen ausgelegt.

