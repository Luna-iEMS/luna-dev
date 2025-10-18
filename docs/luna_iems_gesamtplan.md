# Luna-IEMS Gesamtplan (Technische & Strategische Dokumentation)

## Zielsetzung
Luna-IEMS ist eine modulare, lokal und cloud-fähige KI-Plattform für Energie-, Markt- und Unternehmensdaten. Sie verbindet Dokumentenanalyse (RAG), Zeitreihen (Smart Meter, Marktpreise), Simulationen, Empfehlungen und Monitoring in einer integrierten Architektur.

---

## 1. Systemarchitektur

**Architektur-Typ:** Modular, Container-basiert (Docker Compose)

**Hauptkomponenten:**
- **API Layer** – FastAPI-Services für Daten, Ingest, RAG, Empfehlungen
- **Data Layer** – PostgreSQL + TimescaleDB (Zeitreihen, Relationen)
- **Vektor-Datenbank** – Qdrant für Embeddings und semantische Suche
- **LLM-Layer (Luna-Core)** – Ollama mit lokaler Modellbereitstellung
- **Cache Layer** – Redis für Task-/Session-/Context-Caching
- **Monitoring Layer** – Prometheus, Grafana, Loki
- **Storage Layer** – MinIO für Dateien und Dokumente
- **Frontend Layer** – React/Tailwind (Kunden- & Admin-Dashboard)

**Ziel:** Voll isolierte Mandantenarchitektur pro Kunde (lokal oder hybrid).

---

## 2. Datenbanken & Struktur

### PostgreSQL / TimescaleDB
- **users** – Benutzerverwaltung (optional anonymisiert)
- **items** – Dokumente & Wissenselemente
- **item_chunks** – Textsegmente für RAG (mit Qdrant-ID)
- **events** – Interaktionen (view, click, like, feedback)
- **smart_meter_readings** – Zeitreihen von Verbrauch & Produktion
- **market_prices** – Markt- und Energiedaten (simuliert/real)
- **labels** – Bewertung & Reward-Daten für Empfehlungssysteme

### Qdrant
- Collection `luna_knowledge`
  - **vector size:** 768
  - **distance:** cosine
  - **payload:** { text, item_id, tags, metadata }

### Redis
- Task Caching (z. B. generierte Antworten)
- Session Management (Kontextspeicher)

---

## 3. API-Design

**Framework:** FastAPI

**Wichtige Endpunkte:**
- `/ingest/doc` – Upload & Vektorisierung von Dokumenten
- `/rag/ask` – Kontextuelle Abfrage (RAG via Qdrant + Ollama)
- `/recommend` – Personalisierte Empfehlungen
- `/events` – Logging von Nutzeraktionen
- `/metrics` – Monitoring & Telemetrie-API

**Architekturprinzip:** REST + Event-driven (Redpanda optional)

---

## 4. Frontend Layer

### Kunden-Dashboard (Enterprise UI)
**Technologien:** React + Tailwind + shadcn/ui + Framer Motion

**Bereiche:**
1. **Luna Insight Panel** – Hauptinterface, Dark Mode (default), Conversational View, Datenkontext, Playbook-Visualisierung
2. **Smart Meter View** – Echtzeitdaten, Charts, Simulationen
3. **Market Data** – Börsenpreise, Prognosen, Trends
4. **Documents & Wissen** – Uploads, KI-Zusammenfassungen, RAG-Explorer
5. **Recommendations** – Handlungsvorschläge, KI-Empfehlungen
6. **Systemstatus & Hilfe** – Online-Status, FAQ, Luna-Assistent-Hilfe
7. **Footer & Supportbereich** – Impressum, Datenschutz, Kontakt

**Tonality Luna:**
- Deutschsprachig
- Leicht sarkastisch, charmant-britischer Humor
- Modern, professionell, empathisch

---

### Admin-Dashboard (Nur für Administratorin)

**Funktion:**
- **Daten-Ingestion:** Upload neuer Dokumente, CSVs, Schnittstellen-Integration
- **Monitoring:** API-Health, Containerstatus, Logs, Speicherverbrauch
- **Model Control:** Laden/Aktualisieren von Ollama-Modellen
- **Event-Tracking:** Nutzerverhalten, Fehlerlogs, Systemmetriken
- **Backup & Restore:** Datenbank, Qdrant, MinIO
- **Simulation Control:** Start/Stop von Smart-Meter- und Markt-Simulatoren

**Zugang:** Single-User (lokal), kein Multi-Tenant nötig

---

## 5. Simulation Layer

### Smart-Meter-Simulator
- Generiert Messdaten (1–60 Sek. Intervalle)
- Variablen: consumption_kw, production_kw, voltage, quality
- Output → TimescaleDB (table: `smart_meter_readings`)

### Marktpreis-Simulator
- Zufallsbasierte Preisentwicklung (Börsenprodukte)
- Parameter: Markt, Produkt, Preis, Volumen
- Output → `market_prices`

Beide können später durch API-Anbindungen ersetzt werden (Plug&Play-Schnittstellenstruktur).

---

## 6. Monitoring & Observability

**Stack:**
- Prometheus – Metriken (API, DB, Ollama)
- Grafana – Visualisierung
- Loki – Logs (via FluentBit)
- Healthchecks – Docker-basiert, zentraler Endpoint `/health`

**Kennzahlen:**
- API Response Times
- Embedding/Generate-Performance
- DB-Health
- Qdrant-Status
- Speicherverbrauch, Containerstatus

---

## 7. Sicherheit & Infrastruktur

- Netzwerksegmentierung (interne Docker-Netze)
- Zugriff nur über Reverse Proxy
- TLS auf API-Ebene (optional Nginx-Proxy)
- Lokaler Betrieb ohne Cloudabhängigkeit
- Später: Cloud-native Deployment (AWS, Azure, GCP via Terraform)

**Ports (Standardkonfiguration):**
- API: 8000
- Postgres: 5432
- Qdrant: 6333/6334
- Redis: 6379
- Ollama: 11434
- MinIO: 9000/9001

---

## 8. Entwicklungsprozess & Sprints

**Sprintstruktur (kontinuierlich):**
1. Infrastruktur & Containerisierung
2. Data Layer (DB, Qdrant, Simulation)
3. API Layer (RAG, Ingest, Recommend)
4. Frontend (Customer Dashboard)
5. Frontend (Admin Dashboard)
6. Monitoring & Observability
7. Testing & Optimierung
8. Deployment & Packaging

**Pipeline:**
- Git + GitHub Actions
- pytest für Backend-Tests
- Docker Compose Dev/Prod Variablen
- Pre-commit Hooks (Black, Ruff)

---

## 9. Erweiterung & Zukunftsvision

- Federated Learning: Kundendaten anonymisieren und aggregiert ins zentrale Luna-Wissensnetz einfließen lassen.
- KI-Agenten: Luna wird als proaktive Assistentin agieren (Alerting, Empfehlungen, Lernpfade)
- Erweiterte Simulationen (Marktverhalten, Energieoptimierung)
- Multi-Kanal-Zugriff (Web, Mobile, Voice)
- Adaptive UI (Luna passt Sprache & Darstellung an Kundentyp an)

---

## 10. Fazit
Dieser Gesamtplan vereint alle bisherigen technischen, architektonischen und konzeptionellen Entscheidungen in einem strukturierten Entwicklungsleitfaden. Er dient als zentrale Referenz für das Dev-Team zur Umsetzung, Erweiterung und Dokumentation von Luna-IEMS.

