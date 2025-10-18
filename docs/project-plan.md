# 🌙 Luna-IEMS – Projektplan & Fortschritt

[![Build Status](https://github.com/Luna-iEMS/iems-luna/actions/workflows/smoke-test.yml/badge.svg)](https://github.com/Luna-iEMS/iems-luna/actions)
[![Documentation](https://img.shields.io/badge/docs-online-blue)](https://luna-iems.github.io/iems-luna/)
[![Version](https://img.shields.io/badge/version-v1.0.0-green)]()

---

## 🧭 Ziel
**Luna-IEMS** ist ein intelligentes Energie-Informations- und Empfehlungssystem.  
Es verbindet Echtzeit-Simulationen (Smart-Meter, Marktpreise) mit KI-basierter RAG-Analyse und Empfehlungssystemen.

---

## 📈 Gesamtfortschritt

██████████████████████████░░░░ 85%

> ✅ 85 % der MVP-Funktionen sind fertiggestellt  
> 🧩 Recommender & Dashboards in Arbeit  

---

## 📊 Statusübersicht

| Komponente | Status | Fortschritt |
|-------------|:------:|:-----------:|
| **API / Backend (FastAPI)** | 🟢 **Fertig** | ██████████ 100 % |
| **Postgres / Timescale Schema** | 🟢 **Fertig** | ██████████ 100 % |
| **Smart-Meter Simulation** | 🟢 **Fertig** | ██████████ 100 % |
| **Market-Simulation** | 🟢 **Fertig** | ██████████ 100 % |
| **RAG / KI-Komponente (Qdrant + Ollama)** | 🟢 **Fertig** | ██████████ 100 % |
| **Empfehlungssystem (Recommender)** | 🟡 **In Arbeit** | ██████░░░░ 60 % |
| **Frontend / Dashboard** | ⚪ **Geplant** | ███░░░░░░░ 30 % |
| **CI/CD & Tests (GitHub Actions)** | 🟢 **Aktiv** | ██████████ 100 % |
| **Dokumentation / Masterplan** | 🟢 **Online** | ██████████ 100 % |

---

## 🚀 Meilensteine

### 🧩 M1 – Systemgrundlage ✅ *(abgeschlossen)*
- [x] FastAPI-Backend implementiert  
- [x] Postgres/Timescale eingerichtet  
- [x] Qdrant & Ollama integriert  
- [x] CI-Pipeline mit Smoke-Test aktiv  
- [x] Healthchecks & Migrationen

### ⚙️ M2 – Simulation ✅ *(abgeschlossen)*
- [x] Smart-Meter-Worker  
- [x] Market-Worker  
- [x] Dual-Launcher  
- [x] Datenverifizierung (DB)  

### 🧠 M3 – RAG & KI ✅ *(abgeschlossen)*
- [x] Dokumenten-Ingestion (Tika)  
- [x] Chunking & Embeddings  
- [x] RAG-Abfragen mit Zitaten  
- [x] Feedback-Loop vorbereitet  

### 💡 M4 – Empfehlungssystem 🟡 *(laufend)*
- [x] Grundstruktur Recommender  
- [ ] Content-basierte Logik aktivieren  
- [ ] Feedback-Speicherung  
- [ ] Bewertung + Ranking  

### 📈 M5 – Dashboard / Frontend ⚪ *(geplant)*
- [ ] Kunden-Dashboard (React/Tailwind)  
- [ ] Admin-Dashboard (Status & Charts)  
- [ ] Chart-Visualisierung SmartMeter + Preise  

### 🚢 M6 – Release / Deployment ⚪ *(geplant)*
- [ ] Automatisches Tagging  
- [ ] Docker Image Build  
- [ ] Optionales Deployment (Railway/Render)  

---

## 🧩 Offene Tasks (To-Do-Liste)

| Bereich | Aufgabe | Status |
|----------|----------|--------|
| Recommender | Content-basierten Algorithmus integrieren | ⏳ |
| RAG | Test mit großen Dokumenten (>10 MB) | ⏳ |
| Frontend | Dashboard UI starten | 🔲 |
| Docs | README mit Status-Badge aktualisieren | ✅ |
| CI | Release-Workflow einbauen | ⏳ |

---

## 🧾 Wichtige Ressourcen

| Thema | Datei / Link |
|--------|---------------|
| 🧠 Technischer Masterplan | [`docs/luna_iems_technischer_masterplan_closed_gaps_v_1.md`](./luna_iems_technischer_masterplan_closed_gaps_v_1.md) |
| 🧩 Datenbankschema | [`docs/schema.sql`](./schema.sql) |
| 🧪 Smoke-Test-Script | [`scripts/smoke_test.py`](../scripts/smoke_test.py) |
| ⚙️ CI Workflow | [`.github/workflows/smoke-test.yml`](../.github/workflows/smoke-test.yml) |
| 🌐 Website | [Luna-IEMS GitHub Pages](https://luna-iems.github.io/iems-luna/) |

---

## 📅 Nächste Schritte
- [ ] Recommender-Modul finalisieren  
- [ ] Dashboard Frontend entwickeln  
- [ ] CI-Release-Tagging integrieren  
- [ ] Deployment vorbereiten  

---

© 2025 Monika Pichlhöfer – *Luna IEMS*  
„Luna denkt für dich mit.“
