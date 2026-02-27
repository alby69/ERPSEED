# Roadmap - Stato dello Sviluppo

## Stato Attuale

FlaskERP è un progetto in continua evoluzione. Questa pagina documenta lo stato attuale delle funzionalità e la roadmap per gli sviluppi futuri.

---

## Funzionalità Completate

### Core System ✅

| Componente | Stato | Note |
|-----------|-------|------|
| Autenticazione JWT | ✅ Completo | Login, logout, refresh token |
| Multi-Progetto | ✅ Completo | Isolamento dati completo |
| Gestione Utenti | ✅ Completo | Ruoli, permessi |
| Modulo Sistema | ✅ Completo | Plugin, eventi |

### Builder ✅

| Componente | Stato | Note |
|-----------|-------|------|
| Creazione Modelli | ✅ Completo | CRUD completo |
| Tipi Campo Base | ✅ Completo | String, number, date, etc |
| Tipi Campo Avanzati | ✅ Completo | Relation, calculated, summary |
| Viste Kanban | ✅ Completo | Drag & drop |
| Relazioni | ✅ Completo | 1:N, N:N |
| Validazioni | ✅ Completo | Required, unique, regex |

### Marketplace ✅

| Componente | Stato | Note |
|-----------|-------|------|
| Pubblicazione Blocchi | ✅ Completo | Con workflow approvazione |
| Installazione | ✅ Completo | Con un click |
| Certificazione | ✅ Completo | Quality score >= 80% |
| Recensioni | ✅ Completo | Rating e commenti |

### Testing ✅

| Componente | Stato | Note |
|-----------|-------|------|
| Test Runner UI | ✅ Completo | Interfaccia web |
| Generazione Auto | ✅ Completo | Suite CRUD |
| Esecuzione Test | ✅ Completo | Con risultati |
| Quality Score | ✅ Completo | Calcolo automatico |

---

## In Sviluppo

### Contabilità 🟡

**Stato**: 70% completo

- [x] Piano dei conti
- [x] Prima nota
- [x] Partitario
- [ ] Bilancio
- [ ] Fatturazione elettronica (SDI)

### Risorse Umane 🟡

**Stato**: 50% completo

- [x] Anagrafica dipendenti
- [x] Dipartimenti
- [x] Presenze
- [x] Richieste ferie
- [ ] Calcolo stipendi
- [ ] Contratti

---

## Roadmap 2026

### Q1 2026 ✅ (Completato)

- [x] Sistema Builder avanzato
- [x] Marketplace con certificazione
- [x] Test Runner integrato
- [x] Refactoring documentazione

### Q2 2026

- [ ] Completamento Contabilità
  - Bilancio
  - Chiusure esercizio
  - Integrazione SDI (Italiane)

- [ ] AI Assistant v1
  - Integrazione Gemini/Claude
  - Generazione modelli da linguaggio naturale
  - Suggerimenti automatici

- [ ] CRM Module
  - Pipeline commerciali
  - Campagne
  - Lead scoring

- [ ] Produzione Module
  - Distinte basi
  - Cicli di lavorazione

### Q3 2026

- [ ] Progetti e Task
  - Gantt integrato
  - Allocazione risorse
  - Timeline

- [ ] Documentale
  - Archiviazione
  - Versioning
  - Ricerca

- [ ] Integrazioni avanzate
  - E-commerce connectors
  - Marketplace sync

### Q4 2026

- [ ] Helpdesk
  - Ticket
  - Knowledge base
  - SLA

- [ ] Multi-company
  - Consolidamento
  - Reporting cross-company

- [ ] Reporting avanzato
  - Designer grafico
  - Dashboard custom

---

## Come Contribuire

Se vuoi contribuire allo sviluppo:

1. **Segnala bug**: Apri un issue su GitHub
2. **Proponi funzionalità**: Discuti nel forum
3. **Contribuisci codice**: Pull request benvenuti
4. **Supporta**: Star il progetto, diffondi

---

## TODO - Prossima Sessione

### AI Assistant ✅ COMPLETATO

1. **Collegare pulsante "Applica al Progetto"** - ✅ COMPLETATO
   - Endpoint `POST /api/ai/apply` in `backend/ai/api.py`
   - Frontend collegato in `frontend/src/components/ui/AIAssistant.jsx`
   - Crea modelli, campi e tabelle nel database

2. **Ripristinare autenticazione JWT** sull'endpoint `/api/ai/generate`
   - Ancora disabilitato per testing

3. **Testare flow completo**: generazione → edit JSON → applica → modello creato
   - Da testare

---

### Sistema Moduli (Module System) 📋

#### Visione

Un **Modulo** è un'applicazione autosufficiente composta da:
- Uno o più **SysModel** (tabelle dati)
- Uno o più **Block/Component** (interfacce UI)
- **API** per comunicare con altri moduli

```
Module (Gestione Parcheggi)
├── SysModel: CarPark
├── SysModel: Car
├── SysModel: ParkingSession
├── Block: ParkingMap (mappa interattiva)
├── Block: ParkingStats (statistiche)
└── API: /api/parking/* (esposti per integrazione)
```

#### Workflow Modulo

```
Draft → Testing → Published → (opzionalmente) Deprecated
    ↓         ↓           ↓
  Modifiche  Test       Visibile in 
  libere     obbligatori Applicazioni
```

#### Posizione nel Menu

**Opzione A**: Administration > Modules
- Pro: Già esiste come voce
- Contro: Confonde l'utente (i moduli si costruiscono nel Builder)

**Opzione B**: Builder > Moduli (nuova sezione) ⭐ SCELTA
- Pro: Flusso logico - costruisci e gestisci tutto nel Builder
- Pro: Workflow coerente con il resto del Builder
- Pro: Più intuitivo per l'utente
- Contro: Servono nuove UI

---

### Implementazione Sistema Moduli

#### Fase 1: Base Dati

1. **Aggiungere campo `status` a SysModel**
   ```python
   class SysModel(BaseModel):
       # ... existing fields ...
       status = db.Column(db.String(20), default="draft")  # draft, published
   ```
   - `draft`: non visibile in Applicazioni
   - `published`: visibile in Applicazioni

2. **Creare tabella `Module`**
   ```python
   class Module(BaseModel):
       __tablename__ = "modules"
       
       name = db.Column(String(80), unique=True, nullable=False)
       title = db.Column(String(120))
       description = db.Column(Text)
       status = db.Column(String(20), default="draft")  # draft, testing, published
       project_id = db.Column(Integer, ForeignKey("projects.id"))
       
       # Relazioni
       models = db.relationship("SysModel", secondary="module_models")
       blocks = db.relationship("Block", secondary="module_blocks")
       
       # API esposte
       api_definition = db.Column(JSON)  # {"endpoints": [...]}
       
       # Test
       test_suite_id = db.Column(Integer, ForeignKey("test_suites.id"))
       test_results = db.Column(JSON)
   ```

3. **Creare tabelle relazione N:N**
   ```python
   module_models = db.Table('module_models',
       db.Column('module_id', Integer, ForeignKey('modules.id')),
       db.Column('sysmodel_id', Integer, ForeignKey('sys_models.id'))
   )
   
   module_blocks = db.Table('module_blocks',
       db.Column('module_id', Integer, ForeignKey('modules.id')),
       db.Column('block_id', Integer, ForeignKey('blocks.id'))
   )
   ```

#### Fase 2: API Backend

4. **Creare `/api/modules` endpoints**
   - `POST /modules` - crea modulo
   - `GET /modules` - lista moduli (filtra per project)
   - `GET /modules/{id}` - dettaglio modulo
   - `PUT /modules/{id}` - modifica modulo
   - `DELETE /modules/{id}` - elimina modulo
   - `POST /modules/{id}/add-model/{modelId}` - aggiungi modello
   - `POST /modules/{id}/add-block/{blockId}` - aggiungi blocco
   - `POST /modules/{id}/test` - esegue test suite
   - `POST /modules/{id}/publish` - pubblica modulo
   - `POST /modules/{id}/unpublish` - rimuovi da Applicazioni

5. **Modificare `/projects/{id}/models`**
   ```python
   @blp.route("/<int:project_id>/models")
   class ProjectModels(MethodView):
       @blp.arguments(flask_smorestPagination)
       def get(self, project_id):
           # Filtra solo modelli pubblicati
           models = SysModel.query.filter_by(
               project_id=project_id,
               status="published"
           ).all()
           return models
   ```

#### Fase 3: API di Integrazione tra Moduli

6. **Sistema API Module**
   
   Ogni modulo espone automaticamente API basate sui suoi modelli:
   
   ```json
   // Definizione API in Module.api_definition
   {
     "endpoints": [
       {
         "path": "/parking-sessions",
         "method": "GET",
         "description": "Lista sessioni parcheggio",
         "auth_required": true
       },
       {
         "path": "/availability",
         "method": "GET", 
         "description": "Verifica disponibilità posti",
         "auth_required": true
       },
       {
         "path": "/book",
         "method": "POST",
         "description": "Prenotazione posto auto",
         "auth_required": true
       }
     ]
   }
   ```

7. **Registrazione automatica API**
   - Module espone `/api/modules/{module_name}/*`
   - Routing dinamico basato su api_definition

8. **Consumo API da altri moduli**
   - Possibilità di configurare "dependencies" in un modulo
   - Esempio:
     ```json
     {
       "dependencies": [
         {
           "module": "anagrafica",
           "api_path": "/api/anagrafica/clienti",
           "description": "Per selezionare cliente"
         }
       ]
     }
     ```

#### Fase 4: Test Suite Auto-generata

9. **Generazione automatica test**
   
   Quando un modulo passa a status "testing", il sistema genera automaticamente:
   
   - **CRUD Test** per ogni SysModel:
     - Test creazione record
     - Test lettura record
     - Test aggiornamento record
     - Test eliminazione record
   
   - **Validazione Test** per ogni campo:
     - Test campi required
     - Test validazioni regex
     - Test unicità
   
   - **Relazioni Test**:
     - Test integrità referenziale
     - Test cancellazione cascata
   
   - **UI Test** (per Block/Component):
     - Test rendering componenti
     - Test interazioni base

10. **Regole pubblicazione**
    ```
    modulo.publish() → se:
      ✓ Tutti i test superati
      ✓ Quality score >= 80%
      ✓ Almeno una vista (list/detail/form) definita
    
    altrimenti → Messaggio errore con dettagli test falliti
    ```

#### Fase 5: UI Frontend

11. **Nuova pagina Builder > Moduli**
    
    Creare `frontend/src/pages/ModulesPage.jsx`:
    
    - Lista moduli con stato visivo (badge colorati)
      - 🟡 Draft
      - 🟠 Testing
      - 🟢 Published
      - 🔴 Deprecated
    
    - Creazione modulo:
      - Nome e descrizione
      - Seleziona modelli (multi-select da sys_models)
      - Seleziona blocchi (multi-select da blocks)
      - Definizione API (JSON editor opzionale)
    
    - Azioni per ogni modulo:
      - 📝 Modifica
      - 🧪 Test (esegue suite)
      - 📤 Pubblica
      - 🗑️ Elimina

12. **Modificare Applicazioni**
    
    Invece di mostrare singoli modelli, mostrare moduli pubblicati:
    
    ```javascript
    // In ProjectLayout.jsx
    const appItems = modules
      .filter(m => m.status === 'published')
      .map(m => ({
        key: m.name,
        label: m.title,
        path: `/projects/${projectId}/app/${m.name}`
      }));
    ```

13. **Dashboard modulo pubblicato**
    
    Quando si accede a un modulo pubblicato:
    - `/projects/{id}/app/{module_name}`
    - Mostra tutti i componenti/blocks del modulo
    - Menu di navigazione interno al modulo

---

### Domande Aperte per Implementazione

#### 1. Nomenclatura
**Come chiamare questa entità?**
- Moduli ⭐ (più generico, include dati+UI)
- App (più orientato all'utente finale)
- Pacchetti (più tecnico)

#### 2. Sistema API
**Come gestire le API tra moduli?**

- **Opzione A**: CRUD automatico
  - Ogni modello nel modulo espone automaticamente CRUD
  - API: `/api/modules/{module}/{model}`
  - + Veloce da implementare
  - - Meno flessibile

- **Opzione B**: Definizione manuale
  - Dev specificare esattamente quali endpoint esporre
  - API: `/api/modules/{module}/{custom_path}`
  - + Totale controllo
  - - Più lavoro per l'utente

- **Opzione C**: Ibrido ⭐
  - CRUD automatico di default
  - Possibilità di aggiungere custom endpoints
  - ✅ Consigliato

#### 3. Relazioni tra Moduli
**Come gestire le dipendenze?**

Esempio: "Modulo Vendite" usa "Modulo Anagrafica"

- **Opzione A**: Dipendenze esplicite
  - In "Vendite" configuro: "usa Modulo Anagrafica per clienti"
  - Integrazione runtime
  - + Chiaro
  - - Configurazione aggiuntiva

- **Opzione B**: Lookup automatico
  - Se cerco cliente, cerco in tutti i moduli pubblicati
  - + Semplice
  - - Possibili conflitti

- **Opzione C**: Foreign key esplicite ⭐
  - Relazioni normali tra SysModel di moduli diversi
  - Similar a Foreign key tra tabelle
  - + SQL-like, familiare
  - - Richiede che moduli siano nello stesso progetto

#### 4. Tipi di Test
**Quali test generare automaticamente?**

- [ ] CRUD base per ogni modello
- [ ] Validazione campi (required, regex)
- [ ] Unicità campi unique
- [ ] Test relazioni (FK)
- [ ] Test rendering blocchi UI
- [ ] Test performance (opzionale)
- [ ] Test sicurezza (opzionale)

#### 5. Strategia Migrazione Dati
**Cosa succede quando un modulo viene eliminato?**

- **Opzione A**: Eliminazione a cascata
  - Elimina tutti i dati
  - ⚠️ Pericoloso ma pulito

- **Opzione B**: Soft delete
  - I dati rimangono ma modulo sparisce
  - + Sicuro
  - - Dati orfani

- **Opzione C**: Backup obbligatorio ⭐
  - Prima di eliminare, scarica export JSON
  - + Sicuro + tracciabile
  - - Più complesso

---

### Priorità Implementative

| # | Task | Priorità | Difficoltà |
|---|------|----------|------------|
| 1 | Aggiungere status a SysModel | Alta | Bassa |
| 2 | Creare tabella Module | Alta | Media |
| 3 | API CRUD per Module | Alta | Media |
| 4 | Modificare /projects/{id}/models per filter | Alta | Bassa |
| 5 | UI Lista Moduli nel Builder | Media | Media |
| 6 | Sistema test auto-generati | Media | Alta |
| 7 | Pubblicazione modulo | Media | Media |
| 8 | UI modifica modulo | Media | Media |
| 9 | Sistema API tra moduli | Bassa | Alta |
| 10 | Dashboard modulo pubblicato | Bassa | Alta |

---

### Riferimenti File da Modificare

**Backend:**
- `backend/models.py` - Aggiungere status a SysModel, creare Module
- `backend/modules/api.py` - Nuovo file per API moduli
- `backend/modules/models.py` - Nuovo file per modelli Module
- `backend/projects.py` - Modificare /models endpoint

**Frontend:**
- `frontend/src/pages/ModulesPage.jsx` - Nuovo file
- `frontend/src/ProjectLayout.jsx` - Modificare per usare moduli
- `frontend/src/App.jsx` - Aggiungere rotta /app/{module_name}
- `frontend/src/components/Sidebar.jsx` - Aggiungere menu Builder > Moduli

---

### Workflow Builder Visivo ✅ COMPLETATO

**Stato**: Implementato

#### Descrizione
Interfaccia visuale per permettere agli amministratori di creare workflow automatizzati senza scrivere codice, tramite drag&drop.

#### Architettura

```
UI (React)          API Layer           Backend
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Canvas      │───▶│ Validazione │───▶│WorkflowService
│ (ReactFlow) │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
```

#### Componenti Implementati

**FASE 1: Setup e Infrastruttura** ✅
- [x] Installare `@xyflow/react` e `zustand`
- [x] Creare store Zustand per workflow builder
- [x] Creare componenti base canvas

**FASE 2: Backend Enhancement** ✅ (esistente)
- [x] WorkflowService esistente
- [x] API Routes esistenti

**FASE 3: Canvas UI** ✅
- [x] Layout principale con toolbox, canvas, properties
- [x] Toolbox con tipi step draggabili
- [x] Nodi personalizzati per ogni tipo (condition, action, notification, delay, webhook)
- [x] Gestione rami True/False per condizioni

**FASE 4: Properties Panel** ✅
- [x] Form dinamici per tipo nodo
- [x] Field picker con variabili
- [x] Dropdown per selezione modelli/azioni

**FASE 5: Validazione e Test** ✅
- [x] Pulsante Test nel builder
- [ ] Validazione in tempo reale (futuro)
- [ ] Output passo-passo (futuro)

**FASE 6: Persistenza** ✅
- [x] Salvataggio nodi/archi → struttura steps
- [x] Caricamento workflow nel canvas

#### Tipi di Step Supportati

| Step | Configurazione |
|------|----------------|
| condition | field, operator, value |
| action | action_type, field, value |
| notification | type, to, subject, template |
| delay | duration, unit |
| webhook | url, method, headers, body |

#### File Creati
- `frontend/src/stores/workflowBuilderStore.js`
- `frontend/src/components/workflow/WorkflowNodes.jsx`
- `frontend/src/components/workflow/WorkflowPropertiesPanel.jsx`
- `frontend/src/pages/WorkflowBuilder.jsx`

#### Accesso
- URL: `/projects/:projectId/workflow-builder`
- Da WorkflowsPage: pulsante "Builder Visivo"

---

## Note sulla Versione

FlaskERP usa versioning semantico:

- **Major**: Cambiamenti non retrocompatibili
- **Minor**: Nuove funzionalità retrocompatibili
- **Patch**: Bug fix

La versione attuale è **0.x** - in questa fase le API possono cambiare.

---

## Prossimi Obiettivi Strategici

### Short-term (3-6 mesi)

1. Stabilizzare il core
2. Completare Contabilità
3. Lannciare AI Assistant
4. Far crescere il Marketplace

### Medium-term (6-12 mesi)

1. Raggiungere parità con ERP commerciali per PMI
2. Creare community attiva
3. Supporto enterprise (SLA)

### Long-term (1-2 anni)

1. Leader nel mercato ERP open-source
2. Marketplace fiorente
3. Integrazioni AI avanzate

---

*Ultimo aggiornamento: Febbraio 2026*
