# Luna-IEMS – Technische Gesamtplanung & Tonalität

## 1. Zielsetzung
Luna-IEMS ist eine modulare, lokal lauffähige KI-Plattform für Energie- und Industriesysteme. Sie kombiniert Datenintegration, Wissensmanagement, Simulation, RAG-basierte Analyse und adaptive Empfehlungen in einem isolierten, sicheren On-Prem- oder Hybrid-Setup.

Ziel ist die vollständige **Autonomie pro Kunde**, gekoppelt an eine zentrale, anonymisierte Lernschicht (Meta-Brain), die globale Muster erkennt, ohne Kundendaten preiszugeben.

---

## 2. Systemarchitektur (Überblick)

### Core Layer
- **Services**: API (FastAPI), Worker (Python Celery/RQ), Qdrant, TimescaleDB, Redis, Ollama, MinIO
- **Orchestrierung**: Docker Compose (lokal & hybrid-ready)
- **Kommunikation**: REST + gRPC
- **Health / Observability**: Prometheus, Loki, Grafana
- **Deployment-Modi**:
  - Single-Node MVP (lokal)
  - Cluster-Modus mit getrennten Daten- & Inferenzdiensten

### Data Layer
- **Relationale Datenbank**: TimescaleDB (Postgres 15) für Zeitreihen & Relationen
- **Vektordatenbank**: Qdrant (semantische Suche)
- **Objektspeicher**: MinIO für Dokumente, Logs, Modelle
- **Simulationsdaten**: Smart-Meter & Marktpreise (synthetisch generiert, später über APIs ersetzbar)

### KI-Layer (Luna Core)
- **Embedding Engine**: Ollama (lokal), Modell: `nomic-embed-text`
- **RAG Engine**: Llama 3.1 oder Mixtral
- **Recommendation Engine**: Bandit-Style Hybrid (Content + Behavior)
- **Knowledge Builder**: semantisches Chunking + Document-Pipeline (Tika + Embedding + DB-Ingest)
- **Learning Core**: kontinuierliche Verbesserung über anonymisierte Metadaten (optional Meta-Brain-Service)

---

## 3. Luna – Persona & Tonalität

### Sprachliche Identität
- **Stimme**: souverän, intelligent, präzise
- **Ton**: ruhig, analytisch, leicht britisch-sarkastisch, aber respektvoll
- **Ziel**: Vertrauen schaffen durch Kompetenz und Klarheit, nicht durch Übertreibung

### Kommunikationsprinzipien
- **Klarheit vor Komplexität** – Luna strukturiert Wissen, sie simplifiziert nicht.
- **Führung durch Sprache** – Luna leitet durch Fragen, nicht durch Befehle.
- **Fehlerkultur** – Fehlertexte sind freundlich, reflektiert, nie herablassend.
- **Dialogfähigkeit** – Luna reagiert wie eine Partnerin, nicht wie ein Sprachassistent.

### Beispiele (Microcopy)
- *Systemstatus*: „Ich bin wach – und alle Systeme summen im Takt.“
- *Fehlerhinweis*: „Oh, das war wohl ein Ausrutscher im Energiekosmos.“
- *Hilfetext*: „Ich denke laut – datenbasiert, versteht sich.“

### Umsetzung im UI / API
- `tone.md` im Designsystem mit Guidelines für Texte, Tooltips und Notifications
- Standardisierte Response-Messages mit abgestuftem Tonfall (debug → info → user)

---

## 4. UI / UX Architektur

### Kundendashboard (Frontend)
- **Framework**: React (Next.js oder Vite), Tailwind, shadcn/ui
- **Designsystem**: Enterprise-Style, Dark-Mode als Standard, Luna-Blau Akzente
- **Layout**:
  - **Header**: Branding + Schnellzugriff (Suche, Hilfe, User-Menü)
  - **Insight Panel**: interaktives Seitenpanel mit Luna-Kommunikation, Kontext-Hinweisen, Datenstatus
  - **Content Area**: dynamisch (Tab-basiert)
  - **Footer**: Systemstatus, Impressum, Support

### Kernseiten
1. **Übersicht** – Systemstatus, letzte Insights, Warnungen, KPIs
2. **Playbook View** – interaktive Darstellung der Energiedaten, Prozessflüsse, Maßnahmenpläne
3. **Simulation & Prognose** – Szenarien, Smart-Meter-Daten, Energieprognosen
4. **Dokumente** – KI-gestützter Zugriff (RAG), Uploads, Wissensverknüpfung
5. **Empfehlungen** – adaptive Vorschläge, Ursachenanalysen, Benchmarks
6. **Support / Hilfe** – geführte Problembehebung mit Luna-Dialog

### Administrator-Dashboard
- Getrennte UI für Systemüberwachung, Datenmanagement und KI-Feeding
- Funktionen: Health Checks, Logs, Modellmanagement, Ingest-Kontrolle, API-Monitoring

---

## 5. Infrastruktur & DevOps
- **Container Management**: Docker Compose (lokal), optional K8s (später)
- **Healthchecks & Ports**: Alle Services mit klar definierten Port-Ranges, keine Konflikte durch `.env`
- **Logging**: Zentralisiert (FluentBit → Loki)
- **Monitoring**: Prometheus + Grafana Dashboards (API, DB, Worker)
- **CI/CD**: GitHub Actions oder GitLab CI (Build, Test, Deploy)

---

## 6. Erweiterbarkeit & Zukunft
- Multi-Tenant fähige Architektur mit Kundenisolierung pro Instanz
- Zentrales anonymisiertes Meta-Brain für globale Lernprozesse
- API-Gateway für externe Integrationen (Marktdaten, IoT, ERP)
- Skalierbarer Vectorstore (Clustered Qdrant oder Milvus optional)
- Erweiterbare Simulation Engine für Energiemodelle

---

## 7. Offene Punkte & Empfehlungen
- **Simulation Framework**: einfache API zur Erzeugung realistischer Smart-Meter-Daten
- **Anonymisierungsschicht**: einheitliche Schnittstelle für Meta-Learning
- **CI/CD**: Container-Builds mit Healthchecks (Ports validiert)
- **Playbook Visualisierung**: dynamisches Dashboard mit interaktiven Grafiken (Recharts, D3.js)
- **Persona Testing**: UX-Validierung der Luna-Tonalität (realistische Use Cases)

---

**Kurzvision:** Luna ist kein Chatbot, sondern eine technische und kommunikative Schnittstelle zur Energieintelligenz – sie denkt, fragt, analysiert und begleitet. Sie lebt im System, nicht in einem Fenster.

