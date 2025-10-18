# Technischer Projektplan – Luna System (Greenfield / Docker Architektur)

---

## 1. Zielbild

Luna wird als **containerisierte, modulare Systemplattform** aufgebaut, die fünf Schichten umfasst:

| Ebene | Beschreibung |
|--------|---------------|
| **1. User Experience** | Zwei Dashboards: Kunden-Frontend (Energie-Entscheidungssystem) & Admin-Konsole (Qualität, Daten, Monitoring) |
| **2. KI- & Wissensschicht** | Kontext- und Wissensmanagement, Lernlogik, Feedbackarchitektur |
| **3. API-Schicht** | Schnittstellen zu Datenquellen, Modulen, externen Systemen |
| **4. Datenhaltung & Verarbeitung** | Postgres/Timescale für strukturierte Daten, Qdrant/OpenSearch für semantische Inhalte |
| **5. Container & Infrastruktur** | Docker-basierte Umgebung mit klaren Service-Grenzen, orchestriert und versioniert |

---

## 2. Projektstruktur & Rollen

| Rolle | Aufgabe | Verantwortungsbereich |
|--------|----------|------------------------|
| **Monika (PM / QA)** | Planung, Priorisierung, Testdaten, Feedback, Validierung | Steuerung, Kommunikation, Qualitätssicherung |
| **Systemarchitekt (GPT)** | Aufbau technischer Architektur, Definition Schnittstellen, Datenmodelle | Dev-Design & Infrastruktur |
| **Entwicklungsteam (GPT)** | Implementierung der Module in Containern | Backend, Frontend, KI |
| **Daten- & Testkoordinator (Monika)** | Bereitstellung realer Daten & Szenarien | Smart-Meter, Börsendaten, regulatorische Inputs |
| **Review & Strategy Team (EPRIS Core)** | Feedback auf Funktionen, antifragile Lernprüfung | Governance & Validierung |

---

## 3. Projektphasen

### Phase 1 – Setup & Architekturdesign (2 Wochen)
**Ziel:** Technische Grundlage schaffen und Containerstruktur definieren.

**Aufgaben:**
- Architektur-Blueprint: Services, Container, Schnittstellen  
- Docker-Basisaufbau (DB, API, KI, Frontends)  
- Projektstruktur & Versionierung (lokale Entwicklungsumgebung)  
- Festlegung der Datenmodelle (Wissen, Events, Messwerte, Prognosen)  
- Definition interner Kommunikationskanäle (REST, gRPC, Pub/Sub)  

**Ergebnis:** Entwicklungsumgebung mit funktionsfähigem Stack-Grundgerüst.

---

### Phase 2 – Wissenssystem & Datenbasis (3–4 Wochen)
**Ziel:** Wissensdatenbank und Datenhaltungsschicht implementieren.

**Aufgaben:**
- Aufbau strukturierter Datenhaltung (Postgres/Timescale)  
- Aufbau unstrukturierter Wissensbasis (Qdrant/OpenSearch)  
- Einrichtung der Datenpipelines (Smart-Meter, Marktpreise, Dokumente)  
- Testdateneinspielung (Monika)  
- Validierung der Datenqualität und Semantik  

**Ergebnis:** Antifragiles Datenfundament, bereit für KI-Integration.

---

### Phase 3 – API- & Integrationsschicht (3 Wochen)
**Ziel:** Zentrale Steuerlogik und Datenaustausch zwischen Modulen.

**Aufgaben:**
- Definition der API-Endpunkte (interne Services)  
- Aufbau der Kommunikationslogik zwischen Datenbank, Wissensbasis und KI-Schicht  
- Monitoring-Endpoints für Admin-Dashboard  
- Test-Calls & Validation (Monika: funktionale Kontrolle der Schnittstellen)  

**Ergebnis:** Stabiler Kommunikationskern zwischen Frontend, Daten und KI.

---

### Phase 4 – Luna Core (6 Wochen)
**Ziel:** Aufbau der eigentlichen Luna-Logik: Lernen, Reflexion, Interaktion.

**Aufgaben:**
- Definition der Entscheidungslogik (Systemverhalten bei Unsicherheit)  
- Aufbau der Feedbackarchitektur (Events, Nutzung, Lernen)  
- Implementierung antifragiler Mechanismen (Erkennen von Störungen, Bewertung von Feedback)  
- Entwicklung des Kommunikationskerns (Luna versteht Kontext, reagiert empathisch, lernt mit)  
- Testläufe mit Kundenszenarien (Monika: simulierte Interaktionen)  

**Ergebnis:** Luna-Kern mit Lernfähigkeit und Kontextverständnis.

---

### Phase 5 – Dashboards (Kunde & Admin) (6–8 Wochen)
**Ziel:** Luna sichtbar machen: visuelle Interaktion, Navigation, Reporting, Lernen.

#### Kunden-Dashboard
- Navigation über IEMS-Module  
- Systemzustände & Prognosen visualisiert  
- Luna begleitet Entscheidungen kontextbezogen  
- Szenarien-Explorer (Energie, Finanzen, CO₂, Strategie)  

#### Admin-Dashboard
- Wissens-Uploads, Qualitätsbewertungen  
- Datenflussüberwachung & Statuskontrolle  
- Systemgesundheit, Konflikterkennung, Alerts  

**Ergebnis:** Zwei vollständig nutzbare Dashboards (intern + extern).

---

### Phase 6 – Lernzyklen & Antifragile Optimierung (laufend)
**Ziel:** Luna lernt aus Realität, Nutzung und Feedback.

**Aufgaben:**
- Einrichtung kontinuierlicher Lernschleifen (System, Nutzer, Daten)  
- Qualitäts-Reviews (monatlich)  
- Datendrift-Monitoring (Smart-Meter, Markt)  
- Luna-Feedback-System (User-Verhalten → Modellanpassung)  
- Iterative Verbesserungen auf Basis echter Nutzung  

**Ergebnis:** Selbstanpassendes, antifragiles System mit realem Lernverhalten.

---

## 4. Laufende Prozesse

| Prozess | Frequenz | Ziel |
|----------|-----------|------|
| **Sprint-Planung & Review** | 2-wöchentlich | Priorisierung, Transparenz, Feedback |
| **Test & Validierung (Monika)** | nach jeder Phase | Qualität & User-Erfahrung sicherstellen |
| **Systemreflexion (Team)** | monatlich | Lernen aus Fehlern, Hypothesenanpassung |
| **Architektur-Check** | alle 6 Wochen | Konsistenz, Sicherheit, Ressourceneffizienz |
| **Wissensintegration** | kontinuierlich | Daten + Text → semantisches Wissen |

---

## 5. Abhängigkeiten & Prioritäten

| Bereich | Abhängigkeit | Bedeutung |
|----------|--------------|------------|
| **Luna Core** | Wissensbasis + API | Ohne Daten keine Lernlogik |
| **Dashboard** | API + Luna Core | UI hängt von stabiler KI-Logik ab |
| **Feedbacksystem** | Nutzung & Admin-Daten | Braucht echte Interaktionen |
| **Qualitätssteuerung** | Admin-Dashboard | Grundlage antifragiler Entwicklung |
| **Datenströme (Smart-Meter etc.)** | stabile Datenverbindungen | essenziell für Prognosen |

---

## 6. Antifragile Steuerung

- **Planung in Spannungsfeldern:** Jede Phase enthält Unsicherheiten → Luna wird präziser durch Erfahrung.  
- **Fehlerlogik integriert:** Fehler werden dokumentiert und reflektiert.  
- **Zyklusprinzip:** Kein linearer Fortschritt, sondern Test → Feedback → Adaption.  
- **Reflexionszeit:** Am Ende jeder Phase ein „Learning Sprint“ zur Erkenntnissicherung.

---

## 7. Gesamtergebnis

Nach ca. **6 Monaten Entwicklung + 3 Monaten Testphase**:

- Luna ist technisch funktionsfähig und lernfähig.  
- Datenflüsse, Wissen, KI-Logik und UI sind integriert.  
- Monika steuert Test- und Freigabeprozesse.  
- Antifragiles Feedbacksystem implementiert.  
- Erste Pilotierung mit Kund:innen möglich.

---

## 8. Leitprinzipien

> **Transparenz vor Tempo.**  
> **Lernen vor Perfektion.**  
> **Kohärenz vor Komplexität.**  

Luna ist kein Tool, sondern eine Denkarchitektur in Softwareform –  
**jede Komponente dient dem Ziel: Klarheit in einer unsicheren Welt.**

