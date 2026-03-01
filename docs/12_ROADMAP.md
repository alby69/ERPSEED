# Roadmap Completa FlaskERP

Questo documento raccoglie tutte le funzionalità implementate e quelle da implementare, organizzate per modulo/componente.

---

## AI Assistant

### ✅ Implementazioni Completate

| Funzionalità | Data | Note |
|--------------|------|------|
| Architettura base (service + API) | Feb 2026 | backend/ai/service.py, api.py |
| Integrazione LLM OpenRouter | Feb 2026 | NVIDIA Nemotron, Qwen3 |
| Generazione modelli da linguaggio naturale | Feb 2026 | Genera JSON config |
| Interfaccia chat frontend | Feb 2026 | Modal con chat Ant Design |
| Preview JSON modificabile | Feb 2026 | TextArea nel modal |
| Applicazione config al DB | Feb 2026 | Crea modelli, campi, tabelle |

### 📋 Da Implementare

| Funzionalità | Priorità | Note |
|--------------|----------|------|
| Ripristino autenticazione JWT | Alta | /api/ai/generate |
| Test end-to-end | Media | Generazione → apply → modello creato |
| Generazione automatica test | Bassa | Test per modelli creati |
| Integrazione Workflow Builder | Bassa | AI crea workflow |
| Suggerimenti intelligenti | Bassa | Analisi modelli esistenti |

### Riferimenti
- Documento: [09_AI_ASSISTANT.md](09_AI_ASSISTANT.md)
- Codice: `backend/ai/`, `frontend/src/components/ui/AIAssistant.jsx`

---

## Workflow Automation

### ✅ Implementazioni Completate

| Funzionalità | Data | Note |
|--------------|------|------|
| Workflow models | 2025 | Workflow, WorkflowStep, WorkflowExecution |
| WorkflowService | 2025 | Esecuzione step, trigger event |
| API Routes | 2025 | CRUD workflow, test, executions |
| WorkflowsPage UI | 2025 | Lista, creazione, monitoraggio |
| Tipi step base | 2025 | condition, action, notification, delay, webhook |
| Workflow Builder visivo | Feb 2026 | React Flow + Zustand + drag&drop |

### 📋 Da Implementare

| Funzionalità | Priorità | Note |
|--------------|----------|------|
| Estendere tipi step | Media | sub_workflow, HTTP request |
| Variabili di contesto | Media | {{user.name}}, {{date.today}} |
| Workflow asincroni | Bassa | Celery per delay lunghi |
| Versionamento workflow | Bassa | Cronologia modifiche |
| Validazione in tempo reale | Bassa | Nel builder |
| Output passo-passo test | Bassa | Debug esecuzione |

### Workflow Builder - Implementazione Completata

**FASE 1: Setup e Infrastruttura** ✅
- [x] Installare `@xyflow/react` e `zustand`
- [x] Creare store Zustand
- [x] Creare componenti base canvas

**FASE 2: Backend Enhancement** ✅
- [x] WorkflowService esistente
- [x] API Routes esistenti

**FASE 3: Canvas UI** ✅
- [x] Layout principale (toolbox, canvas, properties)
- [x] Toolbox con tipi step draggabili
- [x] Nodi personalizzati
- [x] Gestione rami True/False

**FASE 4: Properties Panel** ✅
- [x] Form dinamici per tipo nodo
- [x] Field picker con variabili

**FASE 5: Validazione e Test** ✅
- [x] Pulsante Test nel builder
- [ ] Validazione in tempo reale (futuro)

**FASE 6: Persistenza** ✅
- [x] Salvataggio/caricamento workflow

### File Creati
- `frontend/src/stores/workflowBuilderStore.js`
- `frontend/src/components/workflow/WorkflowNodes.jsx`
- `frontend/src/components/workflow/WorkflowPropertiesPanel.jsx`
- `frontend/src/pages/WorkflowBuilder.jsx`

### Accesso
- URL: `/projects/:projectId/workflow-builder`

### Riferimenti
- Documento: [01B_AUTOMAZIONE.md](01B_AUTOMAZIONE.md)
- Codice: `backend/workflow_service.py`, `backend/workflows.py`, `frontend/src/pages/WorkflowsPage.jsx`

---

## Hook e Eventi

### ✅ Implementazioni Completate

| Funzionalità | Data | Note |
|--------------|------|------|
| Hook Manager | 2025 | Callback lifecycle entità |
| Event Bus | 2025 | Comunicazione asincrona |
| Tipi hook base | 2025 | Before/After CRUD |
| Eventi sistema | 2025 | entity.created, etc. |

### 📋 Da Implementare

| Funzionalità | Priorità | Note |
|--------------|----------|------|
| Hook configurabili da UI | Bassa | Simili ai workflow ma più semplici |
| Eventi custom | Bassa | Utenti definiscono eventi |

### Riferimenti
- Documento: [01B_AUTOMAZIONE.md](01B_AUTOMAZIONE.md)
- Codice: `backend/composition/hooks.py`, `backend/composition/events.py`

---

## Builder (No-Code)

### ✅ Implementazioni Completate

| Funzionalità | Data | Note |
|--------------|------|------|
| Creazione modelli | 2024 | CRUD completo |
| Tipi campo base | 2024 | string, number, date, etc |
| Tipi campo avanzati | 2024 | relation, calculated, summary |
| Viste Kanban | 2024 | Drag & drop |
| Relazioni | 2024 | 1:N, N:N |
| Validazioni | 2024 | required, unique, regex |
| Import/Export | Feb 2026 | Toolbar, context menu, backup completo |

---

## Moduli Personalizzati

### ✅ Implementazioni Completate

| Funzionalità | Data | Note |
|--------------|------|------|
| Status su SysModel | Feb 2026 | draft/published |
| Tabella Module | Feb 2026 | Già esistente |
| API CRUD per Module | Feb 2026 | Già esistente |
| Filtro DynamicApiService per status | Feb 2026 | Solo published |
| Filtro /projects/{id}/models per ruolo | Feb 2026 | Admin vs utenti |
| UI Lista Moduli nel Builder | Feb 2026 | CustomModulesPage |
| Sistema test auto-generati | Feb 2026 | CRUD, validation, FK, performance |
| Pubblicazione con regole | Feb 2026 | Test + quality score >= 80% |
| Dashboard App-Like | Feb 2026 | ModuleAppPage |
| Sistema API Ibrido | Feb 2026 | /api/modules/{module_name}/* |
| FK tra moduli | Feb 2026 | Campo relation con target_table |
| Menu Builder > Moduli | Feb 2026 | Administration > Modules |
| Migrazione/Backup dati | Feb 2026 | /backup endpoint |

### 📋 Da Implementare

| Funzionalità | Priorità | Note |
|--------------|----------|------|
| Validazione in tempo reale | Bassa | Nel builder workflow |
| Output passo-passo test | Bassa | Debug esecuzione |

### File Riferimento
- Codice: `backend/core/api/custom_modules.py`, `frontend/src/pages/CustomModulesPage.jsx`, `frontend/src/pages/ModuleAppPage.jsx`

---

## Moduli ERP

### Contabilità 🟡

**Stato**: 70%

- [x] Piano dei conti
- [x] Prima nota
- [x] Partitario
- [ ] Bilancio
- [ ] Fatturazione elettronica (SDI)

### Risorse Umane 🟡

**Stato**: 50%

- [x] Anagrafica dipendenti
- [x] Dipartimenti
- [x] Presenze
- [x] Richieste ferie
- [ ] Calcolo stipendi
- [ ] Contratti

### 📋 Prossimi Moduli

| Modulo | Stato | Priorità |
|--------|-------|----------|
| CRM | Da iniziare | Media |
| Produzione | Da iniziare | Bassa |
| Progetti/Task | Da iniziare | Media |
| Documentale | Da iniziare | Bassa |
| Helpdesk | Da iniziare | Bassa |

---

## Struttura Documentazione

```
docs/
├── README.md              # Indice principale
├── 01_CONCETTI.md         # Architettura, pilastri
├── 01B_AUTOMAZIONE.md    # Hook, Eventi, Workflow
├── 02_BUILDER.md         # Guida al Builder
├── 03_MODULI.md          # Moduli ERP
├── 04_AMMINISTRAZIONE.md # Gestione sistema
├── 05_MARKETPLACE.md     # Marketplace
├── 06_INTEGRAZIONI.md    # API, Webhooks
├── 07_TESTING.md         # Testing
├── 08_DEPLOYMENT.md      # Deploy
├── 09_AI_ASSISTANT.md    # AI Assistant
├── 11_TODO.md            # Stato attuale + task attivi
└── 12_ROADMAP.md         # Roadmap completa dettagliata
```

---

## Come Aggiornare Questo Documento

Quando implementi una nuova funzionalità:

1. Aggiungi la funzionalità nella sezione ✅ appropriata
2. Se è da fare, aggiungi in 📋 con priorità
3. Aggiorna la data
4. Rimuovi dalla lista TODO se completata

---

*Ultimo aggiornamento: 1 Marzo 2026*
