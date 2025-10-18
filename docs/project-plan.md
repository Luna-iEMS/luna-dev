# 🌙 Luna-IEMS Projektplan

Willkommen zum zentralen Projekt- und Entwicklungsplan des **Luna-IEMS** Systems.  
Dieses Dokument dient als Roadmap für Architektur, Entwicklung, Tests und Release.

---

## 🧭 Ziel des Projekts
Luna-IEMS ist ein intelligentes Energie-Informations- und Empfehlungssystem (IEMS), das
Energiedaten automatisch sammelt, analysiert und über Dashboards zugänglich macht.
Es kombiniert Simulationen (Smart-Meter, Marktpreise) mit KI-gestützter RAG-Analyse und
Empfehlungs-Engine.

---

## 📊 Statusübersicht (Stand: Oktober 2025)

| Bereich | Status | Beschreibung |
|----------|---------|--------------|
| **API-Backend (FastAPI)** | ✅ Fertig | Läuft stabil mit allen Endpunkten |
| **Postgres / TimescaleDB Schema** | ✅ Fertig | Tabellen & Migrationen erstellt |
| **Smart-Meter Simulation** | ✅ Läuft | Schreibt periodisch Messwerte |
| **Market-Simulation** | ✅ Läuft | Schreibt periodisch Marktpreise |
| **RAG-System (Qdrant + Ollama)** | ✅ Aktiv | Beantwortet Fragen mit Zitaten |
| **Admin-Tools & Healthchecks** | ✅ Implementiert | Smoke-Test grün |
| **Empfehlungssystem** | ⚙️ In Arbeit | Placeholder-Modul aktiv |
| **Frontend / Dashboards** | 🕓 Geplant | Noch nicht begonnen |
| **CI/CD (Tests & Build)** | ✅ Aktiv | GitHub Actions erfolgreich |
| **Dokumentation & Masterplan** | ✅ Online | Unter `/docs` und GitHub Pages |

---

## 🚀 Meilensteine

### 🧩 **M1 – Systemgrundlage (erreicht)**
- [x] FastAPI-Backend implementieren  
- [x] Postgres / Timescale aufsetzen  
- [x] Qdrant- und Ollama-Integration  
- [x] CI-Pipeline (Smoke-Test)  
- [x] Health-Checks / Migrations  

### ⚙️ **M2 – Simulation (erreicht)**
- [x] Smart-Meter Worker erstellt  
- [x] Market-Worker erstellt  
- [x] Dual-Launcher (beide Simulationen parallel)  
- [x] Daten in DB prüfen  
- [x] Integration in API-Charts  

### 🧠 **M3 – RAG & KI (erreicht)**
- [x] Dokumenten-Ingestion (Tika)  
- [x] Chunking + Vektorsuche (Qdrant)  
- [x] RAG-Abfragen + Zitate  
- [x] Lern-Feedback-Loop vorbereitet  

### 💡 **M4 – Empfehlungssystem (offen)**
- [ ] Content-basierte Empfehlung aktivieren  
- [ ] User-Feedback erfassen  
- [ ] LinUCB-/Thompson-Sampling evaluieren  
- [ ] Integration in Dashboard  

### 📈 **M5 – Dashboard & Visualisierung (geplant)**
- [ ] Customer-Dashboard (React + Tailwind)  
- [ ] Admin-Dashboard mit Systemstatus  
- [ ] Charts / Diagramme (Energie, Preise, Empfehlungen)  

### 🚢 **M6 – Release & Deployment**
- [ ] CI-Release-Tagging (GitHub Actions)  
- [ ] Docker Image + GitHub Packages  
- [ ] Optionale Cloud Deployment (VPS / Railway / Render)  

---

## 🧩 Task-Board (aktuell)

| Kategorie | Task | Status |
|------------|------|--------|
| **Simulation** | Smart-Meter + Market parallel starten | ✅ |
| **RAG** | Fragen mit Zitat beantworten | ✅ |
| **Recommender** | Erste Empfehlungen generieren | ⚙️ |
| **Docs** | GitHub Pages aktivieren | ✅ |
| **Testing** | Smoke-Test grün halten | ✅ |
| **Release** | Automatisches Tagging einrichten | 🕓 |

---

## 📦 Verlinkungen

- 🔗 [Technischer Masterplan](./luna_iems_technischer_masterplan_closed_gaps_v_1.md)  
- 🔗 [Schema.sql](./schema.sql)  
- 🔗 [Smoke Test (Skript)](../scripts/smoke_test.py)  
- 🔗 [CI-Workflow](../.github/workflows/smoke-test.yml)  
- 🔗 [GitHub Pages Website](https://monika-iems.github.io/iems-luna/)  

---

## 🧭 Nächste Schritte
- [ ] Empfehlungssystem fertigstellen  
- [ ] Dashboard-Frontend beginnen  
- [ ] Deployment & Monitoring  
- [ ] CI Release-Pipeline erweitern  

---

© 2025 Monika Pichlhöfer — _Luna IEMS Projekt_

