# ERPSEED EVOLUTION

## Piano di Sviluppo FlaskERP: Da ERP Custom a Piattaforma Low-Code Enterprise

---

## Indice

1. [Analisi Competitiva](#1-analisi-competitiva)
2. [Le 7 Aree di Miglioramento](#2-le-7-aree-di-miglioramento)
3. [Le 3 Architetture Chiave](#3-le-3-architetture-chiave)
4. [Roadmap Dettagliata](#4-roadmap-dettagliata)
5. [Milestone e Obiettivi](#5-milestone-e-obiettivi)

---

## 1. Analisi Competitiva

### 1.1 Confronto con Appsmith e Budibase

| Feature | FlaskERP | Appsmith | Budibase |
|---------|----------|----------|----------|
| **Target** | ERP custom | Internal tools | Internal tools + apps |
| **Builder UI** | Previsto | Molto avanzato | Molto avanzato |
| **Data modeling** | Dinamico (SysModel) | DB esterno | Interno + esterno |
| **Automazioni** | Hooks/events | JS logic | Automation builder |
| **Marketplace** | Previsto | Limitato | Limitato |
| **AI** | Molto forte | Base | Base |
| **ERP modules** | Sì | No | No |

### 1.2 Punti di Forza e Debolezze

**FlaskERP - Punti di Forza:**
- Visione più ampia (ERP + low-code)
- AI assistant avanzato con tool calling
- Moduli ERP nativi
- Sistema dinamico di modelli

**FlaskERP - Aree di Miglioramento:**
- Maturità degli strumenti visuali
- Onboarding e velocità di setup
- Component library
- Workflow automation visuale

### 1.3 Opportunità

```
┌─────────────────────────────────────────────────────────────────────┐
│                     POSIZIONE STRATEGICA                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   FlaskERP può diventare:                                           │
│                                                                      │
│        ┌─────────────┐                                              │
│        │   ODOO     │  ← Funzionalità ERP complete                │
│        └──────┬──────┘                                              │
│               │                                                     │
│        ┌──────▼──────┐                                              │
│        │  APPSMITH  │  ← Builder UI visuale                       │
│        └──────┬──────┘                                              │
│               │                                                     │
│        ┌──────▼──────┐                                              │
│        │  BUDIBASE  │  ← Semplicità d'uso                          │
│        └──────┬──────┘                                              │
│               │                                                     │
│        ┌──────▼──────┐                                              │
│        │  FLASKERP  │  ← AI NATIVE                                  │
│        │  (TARGET)  │  ← IL MEGLIO DI TUTTI                       │
│        └─────────────┘                                              │
│                                                                      │
│   Con in più: AI-driven application platform                       │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Le 7 Aree di Miglioramento

### 2.1 UI Builder Visuale (Priorità MASSIMA)

**Stato Attuale**: Configurazione → generazione UI (potente ma meno interattivo)

**Obiettivo**: Drag & drop con live preview

```
┌─────────────────────────────────────────────────────────────────────┐
│  UI BUILDER TARGET                                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Block                                                              │
│   ├─ Table                                                         │
│   ├─ Form                                                          │
│   ├─ Kanban                                                        │
│   └─ Chart                                                         │
│                                                                     │
│  Editor tipo:                                                       │
│  drag component                                                     │
│  ↓                                                                 │
│  bind data                                                          │
│  ↓                                                                 │
│  configure actions                                                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Data Binding Semplice

**Obiettivo**: Binding tipo Appsmith `{{entity.field}}`

```
// Binding semplice
{{customer.name}}
{{order.total}}

// Binding con trasformazione
{{UPPER(customer.name)}}
{{IF(order.status == 'pending', '⚠️', '✅')}}

// Binding array
{{COUNT(orders)}}
{{SUM(orders.total)}}
```

### 2.3 Workflow Automation Visuale

**Obiettivo**: Workflow builder tipo n8n

```
    ┌──────────┐      ┌──────────────┐      ┌────────────┐
    │ TRIGGER  │─────▶│  CONDITION   │─────▶│   ACTION   │
    │          │      │              │      │            │
    │ order    │      │ total > 1000 │      │ send email │
    │ created  │      │              │      │            │
    └──────────┘      └──────────────┘      └────────────┘
```

### 2.4 Starter Templates

**Obiettivo**: Installazione 1-click

| Template | Descrizione |
|----------|-------------|
| CRM Base | Clienti, lead, attività |
| Inventory | Prodotti, movimenti |
| Project | Progetti, task, timesheet |
| Helpdesk | Ticket, FAQ |
| HR | Dipendenti, presenze |

### 2.5 Component Library

**Componenti da aggiungere**:

| Categoria | Nuovi Componenti |
|-----------|-----------------|
| Basic | Text, Heading, Badge, Tag, Avatar, Image |
| Advanced | RichText, Calendar, Tree, FileUpload, Map |
| Layout | Tabs, Accordion, Modal, Drawer |

### 2.6 Versioning e Migrations

**Funzionalità**:
- Model version history
- Schema migration engine
- Block/module versioning
- Rollback capability

### 2.7 Debugging Tools

**Strumenti necessari**:
- Request/response inspector
- AI modification diff preview
- Component state viewer
- Performance profiler

---

## 2A. Architettura SysModel/SysField (CUORE DEL SISTEMA)

> **Questa è la decisione architetturale più importante**: il sistema diventa un semplice CRUD builder o una piattaforma ERP estendibile come Odoo.

### 2A.1 Il Principio Fondamentale

```
Il database descrive il database

SysModel = descrive una tabella
SysField = descrive una colonna

Il sistema genera automaticamente:
├── API
├── UI
├── Form
├── Validazioni
├── Relazioni
└── Workflow
```

### 2A.2 Tabella SysModel

Rappresenta un'entità del sistema.

```
sys_model
----------
id
name                    # Nome visuale: "Cliente"
technical_name          # Nome tecnico: "customer"  
table_name              # Tabella DB: "customer"
description             # Descrizione
module                 # Modulo di appartenenza
is_system              # È un modello di sistema?
is_active              # È attivo?
created_at
updated_at
```

### 2A.3 Tabella SysField (LA PIÙ IMPORTANTE)

Definisce ogni campo di ogni modello.

```
sys_field
----------
id
model_id                # FK a sys_model
name                    # Label visuale: "Nome Cliente"
technical_name          # Nome tecnico: "name"
field_type              # Tipo campo
is_required             # Obbligatorio?
is_unique               # Unico?
is_index                # Indicizzato?
default_value           # Valore default
relation_model          # Per relazioni: modello target
relation_type           # Per relazioni: many2one, one2many, many2many
ui_widget               # Widget UI: text, select, radio, etc.
ui_placeholder          # Placeholder
ui_group                # Gruppo nel form
ui_order                # Ordine visualizzazione
ui_visible              # Visibile in UI?
ui_readonly             # Solo lettura?
ui_searchable           # Ricercabile?
ui_filterable           # Filtrabile?
help_text               # Help text
validation_regex        # Regex validazione
validation_min          # Min valore
validation_max          # Max valore
order                   # Ordine campo
is_active               # Attivo?
```

### 2A.4 Field Types (ERP Grade)

| Tipo | Descrizione | Uso |
|------|-------------|-----|
| `string` | Testo breve | Nome, telefono |
| `text` | Testo lungo | Descrizione |
| `integer` | Numero intero | Quantità |
| `float` | Numero decimale | Prezzo |
| `boolean` | True/False | Attivo, visibile |
| `date` | Data | Data nascita |
| `datetime` | Data+ora | Creazione |
| `select` | Select singola | Stato |
| `multiselect` | Select multipla | Tags |
| `many2one` | Relazione 1→N | Cliente → Nazione |
| `one2many` | Relazione 1←N | Cliente → Ordini |
| `many2many` | Relazione N↔N | Prodotto → Categorie |
| `json` | JSON libero | Dati custom |
| `file` | File upload | Documenti |
| `image` | Immagine | Foto |
| `computed` | Campo calcolato | Totale ordine |

### 2A.5 Relazioni (ERP Level)

**Esempio Invoice → Customer**:

```
technical_name: customer_id
field_type: many2one
relation_model: customer
```

**Genera automaticamente**:
- ✅ Dropdown di selezione
- ✅ JOIN SQL automatico
- ✅ API relazionale `/api/invoice/1/customer`
- ✅ UI con link al record correlato
- ✅ Cascade delete

### 2A.6 UI Metadata

| Campo | Descrizione |
|-------|-------------|
| `ui_widget` | text, textarea, select, radio, checkbox, datepicker, fileupload |
| `ui_placeholder` | Placeholder input |
| `ui_group` | Gruppo nel form (es. "Anagrafica", "Contabilità") |
| `ui_order` | Ordine nel form |
| `ui_visible` | Visibile in lista? |
| `ui_readonly` | Solo lettura? |
| `ui_searchable` | Incluso nella ricerca? |
| `ui_filterable` | Filtrabile in lista? |

### 2A.7 Workflow State (per ERP serio)

```
sys_workflow_state
------------------
id
model_id
name                # draft, confirmed, paid, cancelled
sequence            # 0, 1, 2, 3
is_initial          # Stato iniziale?
is_final            # Stato finale?
allowed_from        # Da quali stati si può arrivare
allowed_to          # A quali stati si può andare
required_role       # Ruolo necessario per transizione
```

**Esempio Invoice**:
```
draft → confirmed → paid → cancelled
```

### 2A.8 Permissions (ACL come Odoo)

```
sys_model_permission
--------------------
id
model_id
role                # admin, user, guest
can_read            # Lettura?
can_write           # Scrittura?
can_delete          # Eliminazione?
can_create          # Creazione?
field_permissions   # JSON: {field_name: {read: bool, write: bool}}
```

### 2A.9 Hooks (Business Logic)

```
sys_hook
---------
id
model_id
event               # before_create, after_create, before_update, etc.
hook_type          # script, webhook, email
script             # Codice Python
priority           # Ordine esecuzione
is_active          # Attivo?
```

### 2A.10 Computed Fields

```
is_computed         # È un campo calcolato?
compute_script      # Script Python
depends_on          # Campi da cui dipende (per invalidazione cache)
```

**Esempio**:
```python
# invoice_total = sum(invoice_lines.amount)
def compute(self):
    self.invoice_total = sum(line.amount for line in self.lines)
```

### 2A.11 Audit Log

```
sys_record_log
--------------
id
record_id
model_id
user_id
action          # create, update, delete
old_values      # JSON valori vecchi
new_values      # JSON valori nuovi
timestamp
ip_address
```

### 2A.12 Schema Finale (Versione Forte)

```
┌─────────────────────────────────────────────────────────────────────┐
│                  TABELLE CORE METADATA                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  sys_module                                                          │
│  ├── id, name, technical_name, description                         │
│  ├── version, dependencies, is_core                                │
│                                                                      │
│  sys_model                                                           │
│  ├── id, name, technical_name, table_name                          │
│  ├── module_id, is_system, is_active                               │
│                                                                      │
│  sys_field                                                           │
│  ├── id, model_id, name, technical_name, field_type               │
│  ├── is_required, is_unique, is_index                              │
│  ├── relation_model, relation_type                                 │
│  ├── ui_widget, ui_group, ui_order                                 │
│  ├── validation_regex, is_computed, compute_script                │
│                                                                      │
│  sys_model_permission                                               │
│  ├── id, model_id, role, can_read, can_write                      │
│  ├── can_create, can_delete                                         │
│                                                                      │
│  sys_workflow_state                                                 │
│  ├── id, model_id, name, sequence                                 │
│  ├── is_initial, is_final, allowed_from, allowed_to              │
│                                                                      │
│  sys_view                                                            │
│  ├── id, model_id, name, view_type                                │
│  ├── config (JSON), is_default                                     │
│                                                                      │
│  sys_record_log                                                     │
│  ├── id, record_id, model_id, user_id                             │
│  ├── action, old_values, new_values, timestamp                    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 2A.13 Runtime Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     FLASKERP RUNTIME                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌─────────────┐                                                  │
│   │  Flask API  │                                                  │
│   └──────┬──────┘                                                  │
│          │                                                          │
│   ┌──────▼──────┐                                                  │
│   │ Metadata    │  ← Legge SysModel/SysField                      │
│   │   Engine    │                                                  │
│   └──────┬──────┘                                                  │
│          │                                                          │
│   ┌──────▼──────┐                                                  │
│   │  Dynamic    │  ← Genera SQL/ORM dinamicamente                 │
│   │    ORM      │                                                  │
│   └──────┬──────┘                                                  │
│          │                                                          │
│   ┌──────▼──────┐                                                  │
│   │ PostgreSQL  │                                                  │
│   │  Database   │                                                  │
│   └─────────────┘                                                  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 2A.14 Generazione Automatica

**API REST**:
```
GET    /api/customer          → List
POST   /api/customer         → Create
GET    /api/customer/{id}    → Read
PUT    /api/customer/{id}    → Update
DELETE /api/customer/{id}    → Delete

GET    /api/customer/{id}/orders    → Related records
```

**UI React**:
```
/api/meta/customer  →  Legge metadata
                      ↓
Genera automaticamente:
├── Tabella con colonne
├── Form con campi
├── Filtri
├── Ricerca
├── Relazioni
└── Validazioni
```

### 2A.15 Differenza con Other Platforms

| Sistema | Estendibilità | Moduli ERP | Metadata-driven |
|---------|---------------|------------|-----------------|
| App custom | ❌ Bassa | - | ❌ |
| Appsmith | ⚠️ Media | ❌ | ⚠️ |
| Budibase | ⚠️ Media | ❌ | ⚠️ |
| Odoo | ✅ Alta | ✅ | ✅ |
| **FlaskERP** | **✅ Altissima** | **✅** | **✅** |

### 2A.16 Scelta Strategica Fondamentale

> **FlaskERP = ERP Framework Low-Code**
> 
> Non un semplice low-code builder, ma una piattaforma ERP modulare configurabile via metadata con UI generata automaticamente.

**Questo posizionamento è molto raro nel mercato**.

---

## 2B. Architettura a 6 Livelli (Livello Odoo/Salesforce)

> Per raggiungere il livello di Odoo/Salesforce, FlaskERP deve essere pensato come piattaforma meta-programmabile, non come semplice app Flask.

```
┌─────────────────────────────────────────────────────────────────────┐
│          ARCHITETTURA A 6 LIVELLI                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────────────────────────────────┐                     │
│  │              6. UI Layer                    │                    │
│  │    (Admin, Forms, Views, Dashboards, API)   │                    │
│  └──────────────────────┬──────────────────────┘                     │
│                         │                                            │
│  ┌──────────────────────▼──────────────────────┐                     │
│  │           5. Workflow Engine                  │                    │
│  │     (state machine, automation, triggers)    │                    │
│  └──────────────────────┬──────────────────────┘                     │
│                         │                                            │
│  ┌──────────────────────▼──────────────────────┐                     │
│  │             4. ORM Layer                     │                    │
│  │     (dynamic models, relations, validation)  │                    │
│  └──────────────────────┬──────────────────────┘                     │
│                         │                                            │
│  ┌──────────────────────▼──────────────────────┐                     │
│  │             3. Meta Model                    │                    │
│  │    (SysModel, SysField, SysView, SysAction)  │                    │
│  └──────────────────────┬──────────────────────┘                     │
│                         │                                            │
│  ┌──────────────────────▼──────────────────────┐                     │
│  │      2. Module Loader + Plugin Engine        │                    │
│  └──────────────────────┬──────────────────────┘                     │
│                         │                                            │
│  ┌──────────────────────▼──────────────────────┐                     │
│  │         1. Multi-Tenant SaaS Layer           │                    │
│  └─────────────────────────────────────────────┘                     │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

### 2B.1 Livello 1: Multi-Tenant SaaS Layer

**Strategie di Isolamento**:

| Strategia | Descrizione | Pro | Contro |
|-----------|-------------|-----|--------|
| **Schema per tenant** (consigliato) | PostgreSQL schema separati | ✓ Isolamento ✓ Performance | Gestione più complessa |
| Database per tenant | DB separati | ✓ Massimo isolamento | ✓ Backup facile | ✖ Overhead gestione |
| Row-level security | tenant_id su ogni tabella | ✓ Semplice | ✖ Meno sicuro | ✖ Query join complesse |

**Implementazione**:

```python
# Tenant Resolver Middleware
class TenantMiddleware:
    def resolve_tenant(self, request):
        # company1.flaskerp.com → tenant_id = 1
        subdomain = get_subdomain(request.host)
        tenant = Tenant.get(subdomain)
        
        # Set schema per session
        set_search_path(tenant.schema)
        return tenant
```

**Schema Database**:

```
public (metadati globali)
  ├── sys_tenant
  ├── sys_module
  └── sys_model

tenant_1_schema
  ├── crm_lead
  ├── sale_order
  └── ...

tenant_2_schema
  ├── crm_lead
  ├── sale_order
  └── ...
```

---

### 2B.2 Livello 2: Module Loader + Plugin Engine

**Struttura Modulo**:

```
modules/
   crm/
       __manifest__.json       # Metadata
       models/
           lead.py           # Business logic
       views/
           lead_form.xml
           lead_list.xml
       data/
           lead_data.xml
       security/
           ir.model.access.csv
       hooks.py              # Install/uninstall
       __init__.py
```

**Manifest Schema**:

```json
{
  "name": "CRM",
  "version": "1.0.0",
  "depends": ["base"],
  "category": "Sales",
  "description": "Customer Relationship Management",
  
  "models": ["crm.lead", "crm.team"],
  "views": ["crm_lead_form", "crm_lead_tree", "crm_lead_kanban"],
  "data": ["crm_data.xml", "crm_demo.xml"],
  "security": ["crm_security.xml"],
  
  "hooks": {
    "pre_install": "crm.hooks.pre_install",
    "post_install": "crm.hooks.post_install"
  },
  
  "css": ["static/src/css/crm.css"],
  "js": ["static/src/js/crm.js"]
}
```

**Module Loader Flow**:

```
1. scan_modules()
       ↓
2. resolve_dependencies()  ( topological sort )
       ↓
3. load_models()          ( ORM registration )
       ↓
4. load_views()           ( View definitions )
       ↓
5. load_data()            ( Seed data )
       ↓
6. register_hooks()       ( Plugin registration )
       ↓
7. verifyIntegrity()
```

**Plugin Engine**:

```python
# Plugin hooks disponibili
PLUGIN_HOOKS = [
    "model.before_create",
    "model.after_create",
    "model.before_write",
    "model.after_write",
    "model.before_unlink",
    "model.after_unlink",
    "workflow.transition",
    "api.endpoint_called",
]

# Esempio: CRM Plugin
@plugin_hook("crm.lead.create")
def notify_sales_on_new_lead(record):
    """Notifica il team vendite quando viene creato un nuovo lead"""
    send_notification(
        to="sales@company.com",
        subject=f"New Lead: {record.name}",
        body=f"Lead {record.name} from {record.company}"
    )

# Esempio: Inventory Plugin
@plugin_hook("sale.order.confirm")
def decrease_stock_on_sale(record):
    """Decrementa il magazzino quando un ordine viene confermato"""
    for line in record.order_lines:
        line.product_id.stock_qty -= line.product_uom_qty
```

---

### 2B.3 Livello 3: Meta Model (già dettagliato in 2A)

Questo è il cuore che definisce i modelli dinamicamente.

---

### 2B.4 Livello 4: ORM Dinamico

**Architettura ORM**:

```
flaskerp/
 ├ orm/
 │   ├ __init__.py
 │   ├ registry.py        # Registro modelli
 │   ├ environment.py    # Ambiente (like Odoo)
 │   ├ model.py          # Classe base Model
 │   ├ fields.py         # Definizione campi
 │   ├ relations.py      # Gestione relazioni
 │   └ query.py          # Query builder
```

**Registry**:

```python
class Registry:
    """Registro centrale di tutti i modelli"""
    
    def __init__(self):
        self.models = {}  # {technical_name: ModelClass}
        self.fields = {}  # {model_name: {field_name: Field}}
    
    def register_model(self, model_class):
        self.models[model_class._name] = model_class
    
    def get_model(self, name):
        return self.models.get(name)
    
    def get_fields(self, model_name):
        return self.fields.get(model_name, {})
```

**Environment** (stile Odoo):

```python
class Environment:
    """Ambiente per accesso ai modelli"""
    
    def __init__(self, tenant_id, user_id):
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.registry = Registry()
    
    def __getitem__(self, model_name):
        """Accesso ai modelli: env['crm.lead']"""
        return ModelProxy(model_name, self)
    
    def __call__(self, model_name, domain=None):
        """Search: env['crm.lead']([('state', '=', 'new')])"""
        model = self[model_name]
        return model.search(domain) if domain else model
```

**Usage**:

```python
# Creazione record
lead = env["crm.lead"].create({
    "name": "Big Deal",
    "partner_id": 10,
    "expected_revenue": 50000.0
})

# Ricerca
leads = env["crm.lead"].search([
    ("state", "=", "new"),
    ("team_id", "=", 1)
])

# Scrittura
lead.write({"state": "qualified"})

# Eliminazione
lead.unlink()

# Lettura correlati
customer = lead.partner_id
orders = lead.sale_order_ids
```

**Dynamic Field System**:

```python
# Field disponibili
class Char(Field): pass
class Integer(Field): pass
class Float(Field): pass
class Boolean(Field): pass
class Date(Field): pass
class Datetime(Field): pass
class Many2one(Field): pass      # Relazione 1→N
class One2many(Field):          # Relazione 1←N
class Many2many(Field):         # Relazione N↔N
class Computed(Field):          # Campo calcolato
class Json(Field): pass
```

---

### 2B.5 Livello 5: Workflow Engine

**Stati e Transizioni**:

```python
# Esempio: Ordine di vendita
sale_order workflow:
    draft → confirmed → shipped → invoiced → done
         ↘           ↘         ↘
          X          X         X (cancelled)
```

**Tabelle**:

```
sys_workflow
├── id
├── model_id           # sale.order
├── name               # Sale Order Workflow

sys_workflow_state
├── id
├── workflow_id
├── name               # draft, confirmed, paid
├── sequence           # 0, 1, 2, 3
├── is_initial         # True per 'draft'
├── is_final           # True per 'done'

sys_workflow_transition
├── id
├── workflow_id
├── from_state_id
├── to_state_id
├── action             # Funzione da eseguire
├── condition         # Condizione per transizione
├── signal            # Signal per trigger manuale
```

**Workflow Engine API**:

```python
# Transizione automatica
workflow.transition(record, "confirm")

# Transizione con signal
record.signal_confirm()

# Verifica stato
record.state → "draft"

# Get available transitions
record.get_workflow_transitions()
```

**Automazioni Integrate**:

```
┌─────────────────────────────────────────────────────────────────┐
│              AUTOMATION RULES                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Trigger: on_time                                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ cron: 0 8 * * 1                                          │   │
│  │ action: send_weekly_report()                             │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  Trigger: on_create                                             │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ model: crm.lead                                          │   │
│  │ condition: type == 'website'                             │   │
│  │ action: assign_to_round_robin()                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  Trigger: on_state_change                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ from: draft → to: confirmed                              │   │
│  │ action: create_invoice()                                │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

### 2B.6 Livello 6: UI Layer (Auto-Generated)

**Grazie al Meta Model**, l'UI si genera automaticamente:

| Componente | Generato da |
|------------|-------------|
| **Form** | SysField (type, required, widget, validators) |
| **List/Table** | SysView + SysField (searchable, filterable) |
| **Kanban** | SysView with state grouping |
| **Search** | SysField (searchable) |
| **Filters** | SysField (filterable) |
| **Relazioni** | SysField (many2one, one2many) |

**View Types Supportati**:

```
Views
 ├── Form View        (edit record)
 ├── List View        (tree, tabular)
 ├── Kanban View      (card, drag-drop)
 ├── Calendar View    (schedule)
 ├── Gantt View       (timeline)
 ├── Graph View       (charts)
 ├── Pivot View       (analytics)
 └── Dashboard View   (aggregated)
```

---

### 2B.7 Architettura Finale Completa

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FLASKERP PLATFORM                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                         UI Layer                               │ │
│  │   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐          │ │
│  │   │  Admin  │ │  Forms  │ │  Views  │ │   API   │          │ │
│  │   └─────────┘ └─────────┘ └─────────┘ └─────────┘          │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                              │                                       │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                    Workflow Engine                             │ │
│  │   ┌────────────┐ ┌────────────┐ ┌────────────┐              │ │
│  │   │  State     │ │ Transition │ │ Automation │              │ │
│  │   │  Machine   │ │   Rules    │ │   Rules    │              │ │
│  │   └────────────┘ └────────────┘ └────────────┘              │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                              │                                       │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                       ORM Layer                                 │ │
│  │   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐          │ │
│  │   │Registry │ │  Model  │ │ Fields  │ │ Query   │          │ │
│  │   └─────────┘ └─────────┘ └─────────┘ └─────────┘          │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                              │                                       │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                      Meta Model                                │ │
│  │   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐          │ │
│  │   │SysModel │ │SysField │ │SysView  │ │SysAction│          │ │
│  │   └─────────┘ └─────────┘ └─────────┘ └─────────┘          │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                              │                                       │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │              Module Loader + Plugin Engine                     │ │
│  │   ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │ │
│  │   │   Loader    │ │  Manifest   │ │   Hooks     │            │ │
│  │   └─────────────┘ └─────────────┘ └─────────────┘            │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                              │                                       │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                   Multi-Tenant Layer                           │ │
│  │   ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │ │
│  │   │  Tenant     │ │   Schema    │ │  Billing    │            │ │
│  │   │  Manager    │ │  Resolver   │ │             │            │ │
│  │   └─────────────┘ └─────────────┘ └─────────────┘            │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

### 2B.8 Comparazione con Grandi ERP

| Componente | FlaskERP | Odoo | Salesforce | ERPNext |
|------------|----------|------|------------|----------|
| Meta-Model | ✅ | ✅ | ✅ | ✅ |
| ORM Dinamico | ✅ | ✅ | ✅ | ⚠️ |
| Module Loader | ✅ | ✅ | ✅ | ✅ |
| Plugin Engine | ✅ | ✅ | ✅ | ⚠️ |
| Workflow Engine | ✅ | ✅ | ✅ | ✅ |
| Multi-Tenant | ✅ | ✅ | ✅ | ⚠️ |
| AI Native | ✅⚡ | ⚠️ | ⚠️ | ❌ |
| Open Source | ✅ | ✅* | ❌ | ✅ |

> *Odoo ha versione community

---

## 3. Le 3 Architetture Chiave

### 3.1 Meta-Architecture per Builder Dinamico

**Concept**: Non costruire componenti hardcoded, ma definizioni configurabili.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    META LAYER ARCHITECTURE                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   Meta Layer                                                         │
│   ├─ SysModel                                                        │
│   ├─ SysField                                                         │
│   ├─ SysRelation                                                     │
│   ├─ SysView                                                         │
│   ├─ SysComponent                                                    │
│   └─ SysAction                                                       │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

**Esempio Configurazione**:

```json
{
  "view": "customer_list",
  "components": [
    {
      "type": "table",
      "entity": "customer",
      "columns": ["", "phone"]
    }
  ]
name", "email}
```

**Frontend Renderer**:

```
ViewRenderer
   ↓
ComponentRegistry
   ↓
TableComponent | FormComponent | KanbanComponent
```

**Vantaggi**:
1. UI completamente dinamica
2. Plugin di componenti
3. Marketplace UI
4. AI può generare configurazioni

### 3.2 AI Native Architecture

**Concept**: Separare AI reasoning da execution.

```
User Prompt
     │
     ▼
┌─────────────┐
│ AI Planner  │  ← Produce execution plan
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Diff      │  ← Preview prima di applicare
│  Generator  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Execution  │  ← Apply changes
│   Layer     │
└─────────────┘
```

**Tool Registry**:

| Categoria | Tool |
|-----------|------|
| Entity | `create_entity`, `delete_entity`, `update_entity` |
| Field | `add_field`, `remove_field`, `update_field` |
| View | `create_view`, `add_component`, `configure_binding` |
| Block | `create_block` |
| Workflow | `create_workflow`, `add_automation` |

**AI Planner Output**:

```json
{
  "plan": [
    {"tool": "create_entity", "params": {"name": "customer"}},
    {"tool": "add_field", "params": {"entity": "customer", "field": {"name": "email", "type": "string"}}},
    {"tool": "create_view", "params": {"name": "customer_list", "entity": "customer"}}
  ]
}
```

**Diff Preview**:

```
✓ NEW ENTITY: customer
  ├─ name: string
  └─ email: string (required)

✓ NEW VIEW: customer_list
  └─ Table with columns: name, email
```

### 3.3 Marketplace & Module Architecture

**Tipi di Pacchetti**:

```
Marketplace
    │
    ├── Modules        (CRM, Inventory, HR, Accounting)
    │       ├── entities
    │       ├── views
    │       ├── workflows
    │       └── permissions
    │
    ├── Blocks         (Sales Pipeline, Dashboard)
    │
    ├── Components     (Advanced Table, Calendar)
    │
    ├── Templates      (Full app template)
    │
    ├── Automations    (Workflow templates)
    │
    └── AI Prompts    (Assistant templates)
```

**Package Manifest Schema**:

```json
{
  "package": {
    "id": "crm-module",
    "name": "CRM Module",
    "version": "1.0.0",
    "type": "module",
    "contents": {
      "entities": [...],
      "views": [...],
      "workflows": [...]
    },
    "permissions": {...},
    "upgrades": {...}
  }
}
```

**Installer Engine**:
- Validate dependencies
- Create entities
- Create views
- Install workflows
- Set permissions
- Run seed data

---

## 4. Roadmap Dettagliata

### Panoramica

- **Team**: 1-2 sviluppatori
- **AI**: Open-source (Ollama)
- **Approccio**: Parallelo con milestone incrementali
- **Durata**: ~22 settimane (5-6 mesi)

### FASE 0: SysModel/SysField Core (Settimane 1-6) - **COMPLETATO** ✅

| Task | Descrizione | Status | Dependencies |
|------|-------------|--------|--------------|
| SM1.1 | Estendere SysModel: add technical_name, table_name, module, is_system, is_active | ✅ Completato | - |
| SM1.2 | Estendere SysField: add all ui_*, validation_*, computed fields | ✅ Completato | - |
| SM1.3 | Creare SysModule table | ✅ Già esiste in backend/core/models/module.py | SM1.1 |
| SM1.4 | Creare SysModelPermission table | ✅ Già in permissions JSON field | SM1.3 |
| SM1.5 | Creare SysWorkflowState table | ✅ Già esiste in backend/workflows.py | SM1.4 |
| SM1.6 | Creare SysRecordLog table | ✅ Già esiste come AuditLog | SM1.5 |
| SM1.7 | Implementare Dynamic ORM (genera SQL da metadata) | ✅ Completato | SM1.2 |
| SM1.8 | Implementare relation handlers (many2one, one2many, many2many) | ✅ Completato | SM1.7 |
| SM1.9 | Implementare computed fields engine | ✅ Completato | SM1.8 |
| SM1.10 | Implementare hooks engine (before/after CRUD) | ✅ Già esiste in backend/composition/hooks.py | SM1.9 |

### FASE 0B: ORM Dinamico + Module Loader (Settimane 4-10) - **COMPLETATO** ✅ - **COMPLETATO** ✅

| Task | Descrizione | Status | Dependencies |
|------|-------------|--------|--------------|
| ORM1.1 | Registry: registro modelli dinamico | ✅ Completato | SM1.7 |
| ORM1.2 | Environment: accesso ai modelli (stile Odoo) | ✅ Completato | ORM1.1 |
| ORM1.3 | ModelProxy: CRUD operations dinamico | ✅ Completato | ORM1.2 |
| ORM1.4 | Query builder per ricerche complesse | ✅ Completato | ORM1.3 |
| ORM1.5 | Relation handlers (many2one, one2many, many2many) | ✅ Completato | SM1.8 |
| ML1.1 | Module scanner (cerca moduli in /modules) | ✅ Completato | - |
| ML1.2 | Dependency resolver (topological sort) | ✅ Completato | ML1.1 |
| ML1.3 | Manifest parser (__manifest__.json) | ML1.2 |
| ML1.4 | Model registration nel registry | ML1.3 |
| ML1.5 | View loading e registration | ML1.4 |
| ML1.6 | Data seeding | ML1.5 |
| PE1.1 | Plugin hook system | ML1.6 |
| PE1.2 | Decorator @plugin_hook | PE1.1 |
| PE1.3 | Hook registry e execution | PE1.2 |
| PE1.4 | Event dispatching | PE1.3 |

### FASE 0C: Multi-Tenant Layer (Settimane 6-12) - **COMPLETATO** ✅

| Task | Descrizione | Status | Dependencies |
|------|-------------|--------|--------------|
| MT1.1 | Tenant model (subdomain, schema, settings) | ✅ Già esiste | - |
| MT1.2 | Tenant middleware (subdomain → schema resolution) | ✅ Già esiste in backend/core/middleware/tenant_middleware.py | MT1.1 |
| MT1.3 | Schema per tenant (PostgreSQL schema isolation) | ✅ Implementato in tenant_service.py | MT1.2 |
| MT1.4 | Tenant-aware query builder | ✅ Già esiste in backend/core/services/query_filter.py | MT1.3 |
| MT1.5 | Tenant provisioning (create/drop schema) | ✅ Implementato in tenant_service.py | MT1.4 |
| MT1.6 | Cross-tenant queries (reporting) | ✅ Implementato in tenant_service.py | MT1.5 |

### FASE 1: Meta-Architecture (Settimane 1-8)

| Task | Descrizione | Dependencies |
|------|-------------|--------------|
| M1.1 | Aggiungere SysView, SysComponent, SysAction | - |
| M1.2 | Creare ViewRenderer base | M1.1 |
| M1.3 | Implementare ComponentRegistry | M1.2 |
| M1.4 | Config JSON per ogni componente | M1.3 |
| M1.5 | Serializer/deserializer view config | M1.4 |

### FASE 2: UI Builder Visuale (Settimane 1-10)

| Task | Descrizione | Dependencies |
|------|-------------|--------------|
| A1.1 | Setup drag-and-drop (react-dnd) | - |
| A1.2 | Canvas grid system (32px snap) | A1.1 |
| A1.3 | Selection, resize, reposition | A1.2 |
| A1.4 | Property Panel | M1.3 |
| A1.5 | Component Palette | A1.4 |

### FASE 3: Data Binding (Settimane 4-8)

| Task | Descrizione | Dependencies |
|------|-------------|--------------|
| B1.1 | Tokenizer per {{expressions}} | - |
| B1.2 | AST builder | B1.1 |
| B1.3 | Evaluator con context | B1.2 |
| B1.4 | Built-in functions | B1.3 |
| B1.5 | Binding UI | B1.4 |

### FASE 4: AI Native (Settimane 6-14)

| Task | Descrizione | Dependencies |
|------|-------------|--------------|
| AI1.1 | ToolRegistry completo | - |
| AI1.2 | AI Planner service | AI1.1 |
| AI1.3 | Diff generator | AI1.2 |
| AI1.4 | Preview UI | AI1.3 |
| AI1.5 | Context Builder (RAG) | - |
| AI1.6 | Ollama integration | AI1.5 |

### FASE 5: Workflow Visuale (Settimane 8-16)

| Task | Descrizione | Dependencies |
|------|-------------|--------------|
| W1.1 | Estendere Workflow model | - |
| W1.2 | NodeExecutor base | W1.1 |
| W1.3 | Trigger handlers | W1.2 |
| W1.4 | React Flow integration | - |
| W1.5 | Node configuration | W1.4 |

### FASE 6: Starter Templates (Settimane 6-14)

#### Modello Concettuale: Universal ERP Meta-Model (25 entità)

Alla base dei template e dei moduli riutilizzabili c'è un modello concettuale universale che definisce le entità di business comuni a qualsiasi organizzazione. Questo è il livello "core", indipendente dal settore, che viene poi esteso e specializzato dai moduli verticali.

**Universal ERP Meta-Model (25 entità)**

**1. Core Aziendale**
*   **Company** – informazioni base dell’azienda (ragione sociale, partita IVA, indirizzo, contatti).
*   **Branch / Division** – sedi o divisioni operative.
*   **Business Unit** – unità organizzative interne, spesso legate a linee di prodotto o servizi.

**2. Persone e Ruoli**
*   **Employee** – anagrafica dipendenti e contratti.
*   **User Account** – credenziali di accesso e ruoli ERP.
*   **Role / Permission** – definizione ruoli, permessi e responsabilità.
*   **Contact / Partner** – clienti, fornitori, prospect, partner commerciali.

**3. Prodotti e Servizi**
*   **Product / Service** – beni e servizi offerti dall’azienda.
*   **Product Category** – classificazioni e famiglie di prodotti.
*   **Price List / Pricing Rule** – regole di prezzo, sconti e promozioni.

**4. Vendite e Marketing**
*   **Opportunity / Lead** – gestione prospect e pipeline vendite.
*   **Sales Order / Quote** – ordini clienti e preventivi.
*   **Campaign / Marketing Activity** – gestione campagne marketing e attività promozionali.

**5. Acquisti e Fornitori**
*   **Purchase Order / Request** – ordini di acquisto e richieste materiali.
*   **Supplier / Vendor** – anagrafica fornitori.
*   **Contract / Agreement** – contratti e accordi commerciali.

**6. Magazzino e Logistica**
*   **Inventory / Stock** – gestione scorte e movimenti.
*   **Warehouse / Location** – magazzini, depositi e ubicazioni.
*   **Shipment / Delivery** – spedizioni e consegne.

**7. Produzione e Operations**
*   **Bill of Materials (BOM)** – distinta base prodotti.
*   **Work Order / Job** – ordini di produzione o di lavoro.
*   **Resource / Machine** – risorse produttive o operative.

**8. Contabilità e Finanza**
*   **Account / Ledger** – conti contabili e strutture bilancio.
*   **Invoice / Payment** – fatture e pagamenti.
*   **Expense / Cost** – spese interne, rimborsi e costi di progetto.

**✅ Caratteristiche chiave**
*   **Universale**: copre tutte le funzioni fondamentali di qualsiasi azienda.
*   **Estendibile**: ogni entità può avere campi personalizzati tramite `SysField`.
*   **Relazioni tipiche**:
    *   `Company` → `Branch` → `Business Unit`
    *   `Employee` → `Role` → `Permission`
    *   `Sales Order` → `Customer` → `Product` → `Inventory`
    *   `Purchase Order` → `Supplier` → `Product` → `Inventory`
    *   `Invoice` → `Account` → `Payment` → `Expense`

| Task | Descrizione | Dependencies |
|------|-------------|--------------|
| T1.1 | Template metadata schema | - |
| T1.2 | Template loader service | T1.1 |
| T1.3 | Installer engine | T1.2 |
| T1.4 | CRM Base template | T1.3 |
| T1.5 | Inventory template | T1.4 |

### FASE 7: Component Library (Settimane 8-18)

| Task | Descrizione | Dependencies |
|------|-------------|--------------|
| C1.1 | Refactor Archetype → Component | - |
| C1.2 | Dynamic loader | C1.1 |
| C1.3 | Basic components (10) | C1.2 |
| C1.4 | Advanced components (10) | C1.3 |

### FASE 8: Versioning (Settimane 12-20)

| Task | Descrizione | Dependencies |
|------|-------------|--------------|
| V1.1 | ModelVersion table | - |
| V1.2 | Auto-change detection | V1.1 |
| V1.3 | Diff generator | V1.2 |
| V1.4 | Migration engine | V1.3 |
| V1.5 | Version UI | V1.4 |

### FASE 9: Debugging Tools (Settimane 16-22)

| Task | Descrizione | Dependencies |
|------|-------------|--------------|
| D1.1 | Request logging middleware | - |
| D1.2 | Log viewer | D1.1 |
| D1.3 | AI diff preview | AI1.3 |
| D1.4 | State inspector | - |

### FASE 10: Piattaforma Meta-Meta-Model (Livello Enterprise)

Questa fase rappresenta l'evoluzione finale di FlaskERP da piattaforma low-code a un vero e proprio "costruttore di ERP". È il livello che astrae la definizione stessa dei modelli, consentendo una personalizzazione e una flessibilità senza precedenti.

**Quello che chiedi è il vero livello “enterprise”: il Meta-Meta-Model.**
È lo strato sotto il meta-modello ERP e descrive come si costruiscono i modelli stessi.
È la filosofia usata (in forme diverse) da:
*   Odoo
*   SAP S/4HANA
*   Salesforce Platform

Questi sistemi non salvano solo dati aziendali, ma salvano anche la definizione dei modelli che rappresentano quei dati. Questo è il segreto dei veri ERP low-code.

**Architettura Logica:**
```
META-META MODEL (definisce la struttura dei modelli)
   ↓
META MODEL (es. SysModel, SysField)
   ↓
BUSINESS MODEL (es. Cliente, Ordine)
   ↓
DATA (es. 'Mario Rossi', 'Ordine #123')
```

#### Meta-Meta-Model ERP (40 entità core)

L'architettura si divide in 8 layer logici, ognuno responsabile di un aspetto della definizione della piattaforma.

**1️⃣ MODEL DEFINITION LAYER**
(definisce i modelli)

| Entità | Descrizione |
|---|---|
| **Model** | definizione di una tabella logica |
| **Field** | campo del modello |
| **FieldType** | tipo campo |
| **FieldConstraint** | regole |
| **ModelInheritance** | ereditarietà |
| **ModelMixin** | comportamento condiviso |
_Esempio: Model: Customer, Fields: name, email, vat_number_

**2️⃣ RELATIONSHIP LAYER**

| Entità | Descrizione |
|---|---|
| **Relation** | relazione generica |
| **RelationType** | tipo relazione |
| **ForeignKey** | FK |
| **ManyToMany** | relazione M2M |
| **RelationConstraint**| vincoli relazione |
_Esempio: Customer -> Orders (1:N)_

**3️⃣ UI META MODEL**
(Questo è ciò che rende low-code vero)

| Entità | Descrizione |
|---|---|
| **View** | definizione vista |
| **ViewType** | form/list/kanban |
| **ViewField** | campo nella vista |
| **Layout** | layout |
| **Component** | componente UI |
_Esempio: Customer Form con Name, Email, e tab Ordini_

**4️⃣ WORKFLOW META MODEL**

| Entità | Descrizione |
|---|---|
| **Workflow** | processo |
| **State** | stato |
| **Transition** | cambio stato |
| **Action** | azione |
| **Trigger** | evento |
_Esempio: Order (Draft → Confirmed → Shipped → Invoiced)_

**5️⃣ AUTOMATION ENGINE**

| Entità | Descrizione |
|---|---|
| **Rule** | regola |
| **Condition** | condizione |
| **Expression** | espressione |
| **Script** | script |
| **Scheduler** | job pianificato |
_Esempio: if order.total > 10000 → require approval_

**6️⃣ SECURITY MODEL**

| Entità | Descrizione |
|---|---|
| **User** | utente |
| **Role** | ruolo |
| **Permission** | permesso |
| **AccessRule** | regola accesso |
| **RecordRule** | accesso su record |
_Esempio: L'utente "Sales" può vedere solo i propri clienti._

**7️⃣ MODULE SYSTEM**
(Questo è ciò che permette ERP modulari)

| Entità | Descrizione |
|---|---|
| **Module** | modulo |
| **ModuleDependency**| dipendenze |
| **ModuleVersion** | versione |
| **Feature** | funzionalità |
| **Extension** | estensione modello |
_Esempio: Moduli CRM, Sales, Inventory, Accounting_

**8️⃣ PLATFORM LAYER**

| Entità | Descrizione |
|---|---|
| **Tenant** | azienda |
| **Environment** | dev/test/prod |
| **Configuration** | configurazioni |
| **Integration** | integrazione |
| **APIEndpoint** | endpoint API |

📊 **Schema delle 40 entità**

| Categoria | Entità |
|---|---|
| **MODEL CORE** | 1. Model, 2. Field, 3. FieldType, 4. FieldConstraint, 5. ModelInheritance |
| **RELATION** | 6. Relation, 7. RelationType, 8. ForeignKey, 9. ManyToMany, 10. RelationConstraint |
| **UI** | 11. View, 12. ViewType, 13. ViewField, 14. Layout, 15. Component |
| **WORKFLOW** | 16. Workflow, 17. State, 18. Transition, 19. Action, 20. Trigger |
| **AUTOMATION** | 21. Rule, 22. Condition, 23. Expression, 24. Script, 25. Scheduler |
| **SECURITY** | 26. User, 27. Role, 28. Permission, 29. AccessRule, 30. RecordRule |
| **MODULE** | 31. Module, 32. ModuleDependency, 33. ModuleVersion, 34. Feature, 35. Extension |
| **PLATFORM** | 36. Tenant, 37. Environment, 38. Configuration, 39. Integration, 40. APIEndpoint |

🧠 **Perché questo è potente**
Con questo meta-meta-model puoi costruire qualsiasi ERP senza scrivere codice: CRM, HR, Inventory, Accounting, Manufacturing, Projects, Helpdesk.

🔥 **Se vuoi costruire FlaskERP serio servono 3 livelli:**
1.  **META-META-MODEL** (40 entità)
2.  **META-MODEL** (20 entità ERP universali)
3.  **BUSINESS MODELS**
4.  **DATA**

---

## 5. Milestone e Obiettivi

### Timeline Visiva Aggiornata

```
Settimana | SysModel | ORM+Mod | MultiT | Meta | UI Builder | AI Native | Workflow | Templates
----------|----------|---------|--------|------|------------|-----------|----------|-----------
1-2       | ██████   |         |        | ██████    |           |           |          |
3-4       | ██████████████   |         | ██████████████ |           |           |          |
5-6       | ████████ | ██████  | ██████ | ████      | ██████████ | ████      | ██████   | ██████████
7-8       |          | ██████████████ | ██████ |           | ██████     | ████████  | ██████   |
9-10      |          | ████████ | ██████ |           |            | ████      | ██████████████████████| ██████████
11-14     |          |          |        |           |            |           | ████████████████████████████████| ██████████████████
15-18     |          |          |        |           |            |           | ████      |           | ██████████████████
19-22     |          |          |        |           |            |           |           |           |
```

### Milestone Keys

| Milestone | Settimana | Feature |
|-----------|-----------|---------|
| M0 | 6 | SysModel/SysField Core completo |
| M0b | 8 | ORM Dinamico + Module Loader funzionante |
| M0c | 10 | Multi-Tenant Layer attivo |
| M1 | 10 | Meta layer attivo (view → config) |
| M2 | 12 | UI Builder MVP (drag + property panel) |
| M3 | 12 | Data Binding funzionante |
| M4 | 14 | AI Planner con diff preview |
| M5 | 16 | Workflow Builder + automazioni |
| M6 | 14 | 3 Starter Templates installabili |
| M7 | 18 | 20+ Componenti UI |
| M8 | 20 | Versioning completo |
| M9 | 22 | Sistema completo (livello Odoo/Salesforce) |

---

## Feature "Magica"

Il comando che può rendere FlaskERP "enorme":

```
"Create a CRM with leads, opportunities, 
 sales pipeline, email tracking, and dashboard"
```

**Output automatico**:
- Entity: lead, opportunity, activity, note
- Views: kanban, list, form, dashboard
- Workflows: new lead notification, stage change alert
- Blocks: pipeline kanban, revenue chart, activity timeline

---

## Tech Stack Raccomandato

### Frontend
- `@xyflow/react` - Workflow editor
- `dnd-kit` - Drag and drop
- `@tiptap/react` - Rich text editor
- `react-monaco-editor` - Code editor
- `react-leaflet` - Maps

### Backend
- Ollama (esterno) - AI inference locale
- `sqlglot` - SQL parsing

---

## Risorse Necessarie

### Sviluppatore 1 (Full-stack)
- UI Builder
- Data Binding
- Workflow Engine

### Sviluppatore 2 (Backend + Frontend)
- Template System
- Component Library
- Versioning + Debugging

---

*Documento creato: Marzo 2026*
*Versione: 1.0*
