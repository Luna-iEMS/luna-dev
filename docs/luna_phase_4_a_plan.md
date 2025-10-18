# 🧠 Luna Phase 4a – Wissensdatenbank befüllen & semantische Lernpipeline

## 🎯 Ziel

Luna soll Dokumente aller gängigen Formate (DOCX, PDF, TXT, MD …) automatisch analysieren, in Text konvertieren, in Vektoren umwandeln und in Qdrant speichern. Damit entsteht **Luna Brain v1 – das semantische Gedächtnis**.

---

## 🧩 Architekturübersicht

```
Upload → Parser → Textnormalisierung → Embedding-Generator → Qdrant-Speicher
                         │                       │
                         │                       └→ Postgres (Metadaten)
                         └→ Redis (Queue / Status)
```

---

## ⚙️ Komponenten & Rollen

### 1️⃣ Upload-Layer (API-Ebene)

**Zweck:** Eingangspunkt für Dokumente\
**Verantwortung:**

- Endpunkt `/ingest/upload`
- Annahme: DOCX / PDF / TXT / MD
- Validierung, Chunking (Textblöcke, max. 1000 Tokens)
- Übergabe an Redis-Queue für asynchrone Verarbeitung
- Speicherung der Metadaten in Postgres\
  (Dateiname, Upload-Zeit, Quelle, Hash, Status)

---

### 2️⃣ Parser-Layer (Core-Ebene)

**Zweck:** Umwandlung beliebiger Formate in sauberen, strukturierten Text\
**Verantwortung:**

- Nutzung von `unstructured`, `PyMuPDF`, `python-docx`, `markdown2`
- Entfernung von Formatierung, Tabellen-Rauschen, Sonderzeichen
- Optionale Segmentierung (Absätze → semantische Einheiten)
- Ausgabe: „doc\_chunks“ = Liste von Textblöcken mit Metadaten

---

### 3️⃣ Embedding-Generator (Core)

**Zweck:** Text → numerische Repräsentation\
**Verantwortung:**

- Nutzung eines lokalen Embedding-Modells via **Ollama**\
  (z. B. `nomic-embed-text`, `mxbai-embed-large`)
- API-Aufruf an Ollama-Endpoint → Vektor-Response
- Speicherung pro Textblock als JSON:
  ```json
  { "id": ..., "text": "...", "vector": [...], "meta": {...} }
  ```

---

### 4️⃣ Qdrant-Ingestion (Core)

**Zweck:** Persistente Speicherung semantischer Vektoren\
**Verantwortung:**

- Verbindung via Qdrant-Client (REST/gRPC)
- Collection: `luna_knowledge`
- Felder:
  - `id` (UUID)
  - `vector` (embedding)
  - `payload.text`
  - `payload.meta`
- Prüfung auf Dubletten (Hashvergleich)
- Rückmeldung des Status an API (OK / Duplicate / Error)

---

### 5️⃣ Postgres-Metadatenbank

**Zweck:** Verwaltung der Upload-Historie\
**Tabellenstruktur:**

| Feld         | Typ       | Beschreibung                 |
| ------------ | --------- | ---------------------------- |
| id           | UUID      | Primärschlüssel              |
| filename     | Text      | Originaldatei                |
| mimetype     | Text      | Typ (docx/pdf/…)             |
| chunks       | Integer   | Anzahl Textsegmente          |
| inserted\_at | Timestamp | Zeitstempel                  |
| status       | Enum      | uploaded / processed / error |

---

### 6️⃣ Redis-Worker (Background Tasks)

**Zweck:** Asynchrone Verarbeitung großer Datenmengen\
**Verantwortung:**

- Queue `luna_ingest`
- Konsument liest Tasks & ruft Parser + Embedding + Qdrant auf
- Fortschritt via Status-Key `luna:upload:{id}`
- Ermöglicht parallele Verarbeitung & Statusanzeige im Dashboard

---

## 🔍 Ablaufdiagramm

1. User lädt Datei hoch (Dashboard → API)
2. API legt Eintrag in Postgres + Task in Redis an
3. Worker liest Task, ruft Parser + Embedding-Pipeline auf
4. Core schreibt Daten in Qdrant + Update Status
5. Dashboard zeigt Fortschritt / Fertigmeldung
6. Luna kann sofort auf neues Wissen zugreifen (semantische Suche)

---

## 🧠 Datenfluss (End-to-End)

```
User Upload → API (/ingest)
    ↳ Postgres (Metadaten)
    ↳ Redis Queue
        ↳ Core Worker
            ↳ Parser → Embeddings → Qdrant
            ↳ Status-Update (Redis)
```

---

## 🤌 Sicherheits- & Qualitätsmaßnahmen

- Hash-Abgleich (SHA256) zur Dublettenvermeidung
- Max-File-Size (z. B. 20 MB)
- Logging via Fluent-Bit → Loki
- Retry-Mechanismus bei Qdrant- oder Ollama-Timeouts
- Versionierung der Dokumente (V1, V2 …)

---

## 📈 Ergebnis dieser Phase

- Vollständig funktionierende „Knowledge Ingest Pipeline“
- Upload → Embedding → Qdrant funktioniert automatisch
- Admin-Dashboard zeigt Upload-Status & Speicherbelegung
- Grundlage für Lunas antifragile Lernlogik (Phase 4b)

---

# 🔧 Praktischer Implementierungs-Plan (4a.1 – 4a.4)

## 4a.1 Upload-API + Postgres-Integration

**Ziele:**

- API-Endpunkt `/ingest/upload` erstellen
- Dateiannahme und Validierung (Format / Größe)
- Speicherung der Metadaten in `uploads`-Tabelle
- Task-Erstellung in Redis Queue `luna_ingest`

**Tabellenentwurf (Postgres)**

```sql
CREATE TABLE uploads (
  id UUID PRIMARY KEY,
  filename TEXT,
  mimetype TEXT,
  filesize INTEGER,
  chunks INTEGER DEFAULT 0,
  status TEXT DEFAULT 'uploaded',
  inserted_at TIMESTAMP DEFAULT NOW()
);
```

---

## 4a.2 Parser-Service + Format Detection

**Ziele:**

- Datei anhand `mimetype` automatisch erkennen
- Konvertierung zu Text via:
  - `python-docx` (DOCX)
  - `PyMuPDF` (PDF)
  - `markdown2` (MD)
  - Standard-Reader (TXT)
- Chunking-Funktion: Textabschnitte in Segmente (max. 1000 Tokens)

**Ausgabe:**

```json
{
  "chunks": ["Abschnitt 1 ...", "Abschnitt 2 ..."],
  "meta": {"source": "dateiname.pdf"}
}
```

---

## 4a.3 Embedding-Integration via Ollama

**Ziele:**

- Anbindung an Ollama-Endpoint `http://luna-ollama-1:11434/api/embed`
- Modell: `nomic-embed-text`
- Rückgabe numerischer Vektoren
- Speicherung in Qdrant mit Metadaten

**Datenstruktur:**

```json
{
  "id": "uuid",
  "text": "chunk",
  "vector": [0.123, 0.456, 0.789],
  "meta": {"file": "docx", "timestamp": "2025-10-16"}
}
```

---

## 4a.4 Qdrant-Einspielung & Statusverwaltung

**Ziele:**

- Verbindung zu Collection `luna_knowledge`
- Upsert von Vektoren
- Update des Upload-Status in Postgres auf `processed`
- Logging in Redis: Fortschritt pro Chunk

**Redis Keys:**

```
luna:upload:<uuid>:status → uploaded / processing / done / error
luna:upload:<uuid>:progress → Prozentwert
```

---

## 4a.5 Monitoring & Dashboard-Integration

**Ziele:**

- Anzeige laufender Uploads & Fortschritt in Admin-Dashboard
- Healthcheck: Qdrant / Ollama / Core erreichbar?
- Visualisierung der Qdrant-Belegung (Dokumente, Vektoren, Speicher)

**API-Erweiterungen:**

- `/status/health` → alle Services
- `/ingest/status/{uuid}` → Fortschritt eines Uploads
- `/qdrant/stats` → Sammlungsinformationen

---

> Nach Abschluss dieser Phase kann Luna selbstständig Wissen aufnehmen, strukturieren und abrufbar machen – der erste Schritt hin zur antifragilen KI.

