# FlaskERP - Testing System TO-DO

## Panoramica

Questo documento elenca le attività necessarie per completare il Testing System di FlaskERP.

**Stato attuale**: ~70% implementato  
**Tempo stimato**: 4-7 giorni

---

## Fase 1: Bug Fix (Priorità Alta)

### 1.1 URL Backend Hardcoded
**File**: `backend/core/services/test_engine.py:179`
**Problema**: L'URL `http://backend:5000` è hardcoded e non funziona in tutti gli ambienti
**Soluzione**: Usare variabile d'ambiente o configurazione

### 1.2 Delete Esecuzioni Fallisce
**File**: `backend/core/api/test_runner.py`
**Problema**: Occasionally il delete di executions restituisce 500
**Soluzione**: Investigare e correggere constraint DB

### 1.3 Schema Serializzazione
**File**: `backend/core/api/test_runner.py`
**Problema**: La proprietà `ultimo_esito` non viene serializzata correttamente nello schema
**Soluzione**: Correggere TestSuiteSchema

---

## Fase 2: Funzionalità Core

### 2.1 Pagination Test Suites
**Endpoint**: `GET /api/v1/tests/suites`
**Problema**: Nessuna paginazione
**Soluzione**: Aggiungere parametri `page`, `per_page`

### 2.2 CRUD Test Case
**Endpoint**: `POST /api/v1/tests/cases/<id>`, `DELETE /api/v1/tests/cases/<id>`
**Problema**: Non è possibile modificare/eliminare singoli test case
**Soluzione**: Implementare API per edit/delete test case

### 2.3 Report Dettagliato
**Frontend**: `TestRunnerPage.jsx`
**Problema**: L'export include solo errori, non tutti i test
**Soluzione**: Includere dettagli completi (passati, falliti, errori)

### 2.4 Dettagli Esecuzione
**Frontend**: `TestRunnerPage.jsx`
**Problema**: Nessun drill-down sui risultati dei test
**Soluzione**: Creare vista dettagliata con tutti i test eseguiti

---

## Fase 3: Miglioramenti UX

### 3.1 Filtri e Ricerca
**Frontend**: `TestRunnerPage.jsx`
**Funzionalità**: Aggiungere search bar per filtrare suite per nome/modulo

### 3.2 Selezione Multipla
**Frontend**: `TestRunnerPage.jsx`
**Funzionalità**: Checkbox per bulk delete suite

### 3.3 Timeout HTTP
**Backend**: `test_engine.py`
**Funzionalità**: Aggiungere timeout alle richieste HTTP (default 30s)

### 3.4 Logging Esecuzioni
**Backend**: `test_engine.py`
**Funzionalità**: Log delle esecuzioni nel sistema di audit

---

## Funzionalità Opzionali Future

| # | Funzionalità | Descrizione |
|---|--------------|-------------|
| 1 | **Esecuzione Asincrona** | Eseguire test in background con polling |
| 2 | **Test Paralleli** | Parallelizzare test suites |
| 3 | **Scheduler** | Eseguire test automaticamente a intervalli |
| 4 | **Notifiche** | Notifiche email/slack dopo esecuzione |
| 5 | **Coverage** | Calcolo code coverage |
| 6 | **CI/CD Integration** | Integrazione con GitHub Actions, GitLab CI |

---

## Note Tecniche

### Endpoint Esistenti

```
GET    /api/v1/tests/suites              # Lista suite
POST   /api/v1/tests/suites              # Crea suite
GET    /api/v1/tests/suites/<id>        # Dettagli suite
PUT    /api/v1/tests/suites/<id>        # Aggiorna suite
DELETE /api/v1/tests/suites/<id>        # Elimina suite
POST   /api/v1/tests/suites/<id>/run     # Esegue suite
POST   /api/v1/tests/suites/<id>/cases   # Aggiungi test case

GET    /api/v1/tests/executions          # Lista esecuzioni
GET    /api/v1/tests/executions/<id>    # Dettagli esecuzione
DELETE /api/v1/tests/executions/<id>   # Elimina esecuzione

POST   /api/v1/tests/generate           # Genera suite automaticamente
POST   /api/v1/tests/module/status      # Cambia stato modulo
GET    /api/v1/tests/module/status/<name>  # Stato modulo
GET    /api/v1/tests/modules/status      # Tutti gli stati
```

### Entità Database

- **test_suites**: Suite di test
- **test_cases**: Singoli test case
- **test_executions**: Esecuzioni registrate
- **module_status_history**: Storico cambi stato

### Moduli Supportati per Test

- soggetti
- indirizzi
- ruoli
- contatti

---

## Riferimenti

- File backend: `backend/core/`
- File frontend: `frontend/src/pages/TestRunnerPage.jsx`
- Documentazione: `docs/`

---

*Documento creato: Febbraio 2026*
