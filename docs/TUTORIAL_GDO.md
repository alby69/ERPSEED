# Tutorial: Configurazione Modulo GDO con Aziende e Punti di Vendita

Questo tutorial spiega come configurare il modulo GDO Reconciliation per gestire Aziende e Punti di Vendita.

## Prerequisiti

- ERPSeed installato e funzionante
- Accesso come amministratore
- Modulo GDO Reconciliation attivato

---

## Fase 1: Creazione Modelli Dati

### Opzione A: Usa il Template (Consigliato)

Il file `/backend/templates/data/gdo_reconciliation.json` contiene già la definizione completa dei modelli necessari.

```python
# Crea i modelli dal template
from backend.orm.module_loader import ModuleLoader

loader = ModuleLoader()
loader.load_from_file('templates/data/gdo_reconciliation.json')
```

### Opzione B: Crea manualmente via Builder

1. Accedi a **Builder → Modelli**
2. Clicca **"Nuovo Modello"**

#### Modello 1: Azienda GDO

| Campo | Tipo | Opzioni |
|-------|------|---------|
| name | string | required: true |
| vat_number | string | - |
| address | string | - |

- Nome tabella: `gdo_companies`

#### Modello 2: Punto Vendita

| Campo | Tipo | Opzioni |
|-------|------|---------|
| company_id | many2one | relation: gdo_companies, required: true |
| name | string | required: true |
| code | string | required: true |

- Nome tabella: `gdo_stores`

#### Modello 3: Movimento Cassa

| Campo | Tipo | Opzioni |
|-------|------|---------|
| store_id | many2one | relation: gdo_stores, required: true |
| date | date | required: true |
| debit | float | default: 0 |
| credit | float | default: 0 |
| valuta_date | date | - |
| description | string | - |

- Nome tabella: `gdo_movements`

---

## Fase 2: Creazione Block Layout (VisualBuilder)

### Accesso al VisualBuilder

**Da CustomModulesPage:**
1. Vai su **Builder → Moduli Personalizzati**
2. Modifica il modulo **GDO Reconciliation**
3. Clicca **"Crea Nuovo Block"**

### Componenti VisualBuilder

#### Componente 1: Card Principale
```json
{
  "type": "card",
  "config": {
    "title": "Gestione GDO"
  },
  "x": 0, "y": 0, "w": 400, "h": 300
}
```

#### Componente 2: Titolo Sezione
```json
{
  "type": "title",
  "config": {
    "content": "Seleziona Azienda",
    "level": 4
  },
  "x": 20, "y": 20
}
```

#### Componente 3: Select Azienda
```json
{
  "type": "select",
  "config": {
    "placeholder": "Seleziona Azienda",
    "dataSource": "companies",
    "labelField": "name",
    "valueField": "id"
  },
  "x": 20, "y": 60
}
```

#### Componente 4: Tabella Punti Vendita
```json
{
  "type": "table",
  "config": {
    "columns": [
      {"title": "Codice", "dataIndex": "code"},
      {"title": "Nome", "dataIndex": "name"}
    ],
    "pagination": true
  },
  "dataSource": "stores",
  "x": 20, "y": 120
}
```

#### Componente 5: Pulsante Avvio Riconciliazione
```json
{
  "type": "button",
  "config": {
    "label": "Avvia Riconciliazione",
    "type": "primary",
    "action": "navigate",
    "path": "/projects/{projectId}/gdo-reconciliation"
  },
  "x": 20, "y": 200
}
```

### Salvataggio Block

1. Clicca **"Salva"** nel VisualBuilder
2. Nome: `gdo_company_manager`
3. Descrizione: "Gestione Aziende e Punti Vendita GDO"

---

## Fase 3: Associazione Block al Modulo

### Via UI

1. **Builder → Moduli Personalizzati**
2. Modifica il modulo **GDO Reconciliation**
3. Nel campo **"Blocchi Layout"** seleziona:
   - `gdo_launcher`
   - `gdo_company_manager`
4. Clicca **Salva**

### Via API

```bash
# Otteni ID modulo
curl -s "/api/v1/modules?search=gdo_reconciliation" \
  -H "Authorization: Bearer TOKEN" | jq '.modules[0].id'
# Output: 1

# Otteni ID block
curl -s "/api/projects/1/blocks" \
  -H "Authorization: Bearer TOKEN" | jq '.[] | select(.name=="gdo_company_manager") | .id'
# Output: 2

# Associa block al modulo
curl -X POST "/api/v1/modules/1/blocks/2" \
  -H "Authorization: Bearer TOKEN"

# Verifica associazione
curl -s "/api/v1/modules/1" \
  -H "Authorization: Bearer TOKEN" | jq '.blocks'
```

---

## Fase 4: Integrazione con GDOReconciliationTool

### Modifica Frontend

Per collegare la selezione azienda/punto vendita alla riconciliazione:

#### 1. Aggiungi stato per selezione
```javascript
const [selectedCompany, setSelectedCompany] = useState(null);
const [selectedStore, setSelectedStore] = useState(null);
const [companies, setCompanies] = useState([]);
const [stores, setStores] = useState([]);
```

#### 2. Carica aziende all'avvio
```javascript
useEffect(() => {
  async function loadData() {
    const companyRes = await apiFetch('/api/data/gdo_companies');
    const companyData = await companyRes.json();
    setCompanies(companyData.items || []);
  }
  loadData();
}, []);
```

#### 3. Carica punti vendita al cambio azienda
```javascript
const onCompanyChange = async (companyId) => {
  setSelectedCompany(companyId);
  const storeRes = await apiFetch(`/api/data/gdo_stores?company_id=${companyId}`);
  const storeData = await storeRes.json();
  setStores(storeData.items || []);
};
```

#### 4. Includi selezione nel salvataggio
```javascript
const saveResults = async () => {
  await apiFetch('/api/gdo/save', {
    method: 'POST',
    body: JSON.stringify({
      project_id: projectId,
      company_id: selectedCompany,
      store_id: selectedStore,
      results: results
    })
  });
};
```

---

## Struttura Finale

```
Modulo GDO Reconciliation
│
├── Dashboard App-Like (/projects/1/app/gdo_reconciliation)
│   │
│   ├── Panoramica
│   │   ├── Blocchi Layout: 2
│   │   └── Modelli Dati: 5
│   │
│   ├── gdo_launcher (Block)
│   │   └── Card con pulsante → GDOReconciliationTool
│   │
│   ├── gdo_company_manager (Block)
│   │   ├── Select Azienda
│   │   ├── Tabella Punti Vendita
│   │   └── Pulsante Avvio
│   │
│   └── Modelli Dati
│       ├── gdo_company (Azienda)
│       ├── gdo_store (Punto Vendita)
│       ├── gdo_movement (Movimento)
│       ├── gdo_session (Sessione)
│       └── gdo_match (Quadratura)
│
└── GDOReconciliationTool (/projects/1/gdo-reconciliation)
    ├── Upload File Excel
    ├── Selezione Azienda/Punto Vendita
    ├── Elaborazione
    └── Salvataggio con FK
```

---

## Risoluzione Problemi

### I modelli non appaiono nel menu

1. Verifica che siano stati generati nel DB
2. Controlla che il progetto sia associato
3. Aggiorna la pagina

### I block non si visualizzano nella dashboard

1. Verifica che il modulo sia in stato "published"
2. Controlla l'associazione Block-Module
3. Ricarica la pagina

### Errore nella riconciliazione

1. Verifica che i modelli esistano
2. Controlla i log del server
3. Testa con un file Excel semplice

---

*Documento creato: Marzo 2026*
