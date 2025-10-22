# 🌙 Luna IEMS – Intelligent Energy Management System

[![🔥 Smoke Test](https://github.com/Luna-iEMS/luna-dev/actions/workflows/smoke-test.yml/badge.svg)](https://github.com/Luna-iEMS/luna-dev/actions/workflows/smoke-test.yml)
[![🔬 Integration Tests](https://github.com/Luna-iEMS/luna-dev/actions/workflows/integration-test.yml/badge.svg)](https://github.com/Luna-iEMS/luna-dev/actions/workflows/integration-test.yml)
[![📦 Release Notes](https://github.com/Luna-iEMS/luna-dev/actions/workflows/release-drafter.yml/badge.svg)](https://github.com/Luna-iEMS/luna-dev/releases)
[![🔄 Project Sync](https://github.com/Luna-iEMS/luna-dev/actions/workflows/project-sync.yml/badge.svg)](https://github.com/Luna-iEMS/luna-dev/actions/workflows/project-sync.yml)

---

## 🚀 Überblick

**Luna IEMS (Intelligent Energy Management System)** ist ein modulares, KI-gestütztes Energiemanagement-Framework, das intelligente Steuerung, Datenanalyse und semantische Verarbeitung von Smart-Meter-Informationen ermöglicht.  
Das System kombiniert **LLMs**, **Vektordatenbanken**, **Daten-Ingest**, **Tika-Parsing** und **RAG-Empfehlungen** zu einem integrierten Ökosystem.

---

## ⚙️ Architektur

| Service | Beschreibung |
|----------|---------------|
| **API** | FastAPI-Backend mit RAG- und Recommendation-Routen |
| **DB** | PostgreSQL 15 mit Alembic-Migrationssystem |
| **Qdrant** | Vektor-Datenbank für Embeddings und Ähnlichkeitssuche |
| **Tika** | Apache Tika Server zur Dokumentenanalyse |
| **Ollama** | LLM-Runtime mit `llama3.1:8b` & `nomic-embed-text` |
| **Worker** | Background-Jobs (Training, Embedding, Crawling) |
| **Updater** | Automatischer Komponenten- und Modell-Updater |

**Netzwerk:** `iems-luna_luna-net`  
**Standardports:**  
API → `8000` • Ollama → `11434` • Qdrant → `6333` • Tika → `9998`

---

## 🐳 Setup & Lokaler Start

### 🧰 Voraussetzungen
- Docker ≥ 25.x  
- Docker Compose ≥ 2.24  
- mind. 12 GB RAM empfohlen  
- Zugriff auf das GitHub-Repository [`Luna-iEMS/luna-dev`](https://github.com/Luna-iEMS/luna-dev)

### 🧩 Setup-Schritte
```bash
# Repository klonen
git clone https://github.com/Luna-iEMS/luna-dev.git
cd luna-dev

# Alte Container entfernen & Cache leeren
docker compose down -v --remove-orphans
docker compose build --no-cache

# Stack starten
docker compose up -d

# Health prüfen
docker compose ps
curl http://localhost:11434/api/tags
curl http://localhost:8000/health
