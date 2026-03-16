# Moduli ERP

## Cos'è un Modulo

Un **Modulo** in ERPSeed è l'unità funzionale completa che combina:

```
┌─────────────────────────────────────────────────────────────────┐
│                          MODULE                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│  │  SysModel   │  │    Block    │  │    Hook    │           │
│  │  (Dati)     │  │    (UI)     │  │  (Logica)  │           │
│  └─────────────┘  └─────────────┘  └─────────────┘           │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                         API                               │   │
│  │              Endpoint REST esposti                        │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

- **SysModel**: le entità dati (creati con il Builder)
- **Block**: le interfacce utente (collezioni di Component)
- **Hook**: la logica di business (validazioni, calcoli, automatismi)
- **API**: gli endpoint REST esposti

---

## Categorie di Moduli

| Categoria | Fornitore | Descrizione |
|-----------|-----------|-------------|
| **core** | Sistema | Funzionalità fondamentali, sempre presenti |
| **builtin** | Sviluppatori core | Moduli base inclusi |
| **premium** | Sviluppatori core | A pagamento |
| **marketplace** | Comunità | Pubblicati dalla comunità |

### Moduli Core

Sempre disponibili e necessari al sistema:

- **Auth**: Autenticazione e gestione utenti
- **Progetti**: Gestione ambienti isolati
- **Builder**: Creazione entità custom

### Moduli Builtin

Inclusi nell'installazione standard:

- **Anagrafica**: Gestione Soggetti, Ruoli, Indirizzi, Contatti
- **Prodotti**: Catalogo prodotti e servizi
- **Vendite**: Ciclo di vendita completo
- **Acquisti**: Ciclo di approvvigionamento
- **Magazzino**: Inventari e movimentazioni

---

## Moduli Disponibili

### Anagrafica (Parties)

Gestisce le entità con cui l'azienda interagisce.

**Soggetti**: Persone fisiche e giuridiche. Un soggetto può essere Cliente, Fornitore, Dipendente secondo i Ruoli associati.

**Ruoli**: Definiscono la relazione. Base: Cliente, Fornitore, Prospect, Partner.

**Indirizzi**: Localizzazioni geografiche (sede legale, operativa, magazzino).

**Contatti**: Canali comunicazione (email, telefono, fax, PEC).

### Prodotti

Gestisce il catalogo prodotti/servizi.

- Scheda prodotto completa
- Codici multipli (SKU, barcode, fornitore)
- Categorie e sottocategorie
- Listini prezzi
- Varianti (taglia, colore)

### Vendite

Ciclo di vendita completo.

- Preventivi
- Ordini cliente
- Note di credito
- Statistiche
- Dashboard commerciale

**Flusso**: Preventivo → Ordine → DDT → Fattura

### Acquisti

Ciclo di approvvigionamento.

- Richieste di acquisto
- Ordini fornitore
- Ricevimenti merce
- Comparazione fornitori

### Magazzino

Gestione inventari.

- Giacenze per ubicazione
- Movimenti carico/scarico
- Inventario
- Attrezzature
- Tracking lotti/seriali

---

## Moduli Builtin

Inclusi nell'installazione standard:

- **Anagrafica**: Gestione Soggetti, Ruoli, Indirizzi, Contatti
- **Prodotti**: Catalogo prodotti e servizi
- **Vendite**: Ciclo di vendita completo
- **Acquisti**: Ciclo di approvvigionamento
- **Magazzino**: Inventari e movimentazioni
- **GDO Reconciliation**: Riconciliazione automatica incassi GDO

---

## Modulo GDO Reconciliation

Il modulo **GDO Reconciliation** (Grande Distribuzione Organizzata) permette la riconciliazione automatica degli incassi di cassa con i versamenti bancari.

### Caratteristiche

- **Upload Excel**: Caricamento file estratti dal software cassa
- **Elaborazione automatica**: Algoritmo di matching progressive balance
- **Statistiche**: Totalizzazioni Dare/Avere, grafici
- **Export Excel**: Esportazione risultati riconciliazione

### Utilizzo

1. Carica il file Excel dal software cassa
2. Configura i parametri (algoritmo, tolleranza, finestra giorni)
3. Esegui la riconciliazione
4. Visualizza i risultati e le statistiche
5. Esporta o salva i dati

### Formato File Excel

Il file deve contenere le seguenti colonne (italiano):

| Colonna | Descrizione |
|---------|-------------|
| **Data** | Data operazione |
| **Dare** | Importo dare (incasso) |
| **Avere** | Importo avere (versamento) |
| **Data Valuta** | Data valuta (opzionale) |

### Integrazione con Block

Il modulo GDO può essere arricchito con Block layout creati tramite VisualBuilder. I Block vengono visualizzati nella dashboard App-like del modulo.

---

## Gestire i Moduli

### Attivare un Modulo

1. Accedi come amministratore
2. Vai su **Amministrazione → Moduli**
3. Trova il modulo
4. Clicca **Attiva**

Il sistema installa dipendenze e crea tabelle.

### Disattivare un Modulo

1. Vai su **Amministrazione → Moduli**
2. Trova il modulo
3. Clicca **Disattiva**

I dati rimangono nel database.

### Configurare un Modulo

Ogni modulo ha impostazioni specifiche:
- Parametri generali
- Numerazioni documenti
- Workflow di approvazione
- Integrazioni

---

## Dipendenze tra Moduli

Alcuni moduli richiedono altri moduli per funzionare.

**Esempio**: Il modulo Vendite richiede Anagrafica e Magazzino

Quando attivi un modulo, il sistema verifica automaticamente le dipendenze.

---

## Creare un Modulo Custom

Puoi creare moduli entirely custom usando il Builder.

### Struttura di un Modulo Custom

1. **Crea i SysModel** necessari (es: RichiesteSupporto)
2. **Crea i Block** per l'interfaccia (form, table, kanban)
3. **Definisci gli Hook** per la logica (validazioni, notifiche)
4. **Configura i permessi**
5. **Pubblica** il modulo

### Ciclo di Vita

```
draft ──► testing ──► published ──► deprecated
```

- **Draft**: In fase di sviluppo
- **Testing**: Pronto per test
- **Published**: Installabile
- **Deprecated**: Non più consigliato

### Associare Block ai Moduli

Ogni modulo custom può avere uno o più Block associati che definiscono il layout dell'interfaccia.

**Via UI (CustomModulesPage)**:
1. Crea o modifica un modulo
2. Seleziona i Block desiderati nel campo "Blocchi Layout"
3. Salva il modulo

**Via API**:
```bash
# Aggiungi un block al modulo
curl -X POST "/api/v1/modules/{module_id}/blocks/{block_id}" \
  -H "Authorization: Bearer <token>"

# Rimuovi un block dal modulo
curl -X DELETE "/api/v1/modules/{module_id}/blocks/{block_id}" \
  -H "Authorization: Bearer <token>"
```

### Creare Block dalla Pagina Moduli

Dalla pagina **CustomModulesPage** è possibile creare nuovi Block direttamente:

1. Crea o modifica un modulo
2. Clicca **"Crea Nuovo Block"**
3. Si apre il **VisualBuilder** per disegnare il layout
4. Salva il Block - viene automaticamente associato al modulo

---

## Pubblicare un Modulo

Per pubblicare nel Marketplace:
1. Porta il modulo in stato "testing"
2. Esegui i test (quality score ≥ 80%)
3. Clicca **Pubblica**
4. Compila le informazioni (nome, descrizione, prezzo)

### Test e Qualità

FlaskERP include un sistema di test avanzato per garantire la qualità dei moduli.

**Tipi di test eseguiti**:

| Tipo | Descrizione | Peso |
|------|-------------|------|
| **CRUD** | Create, Read, Update, Delete | 40% |
| **Validation** | Campi required, unique, regex | 30% |
| **Relation** | Verifica foreign key | 20% |
| **Performance** | Tempo query < 1 secondo | 10% |

**Quality Score**: Il punteggio finale è una media ponderata. Per pubblicare serve ≥ 80%.

**Esegui test**:
```bash
curl -X POST "/api/v1/modules/{id}/test" \
  -H "Authorization: Bearer <token>"
```

### Backup e Migrazione

Prima di eliminare un modulo, puoi esportare tutti i dati in JSON.

**Esporta backup**:
```bash
curl -X GET "/api/v1/modules/{id}/backup" \
  -H "Authorization: Bearer <token>"
```

Il backup include:
- Informazioni modulo (nome, versione, stato)
- Schema campi per ogni modello
- Tutti i record dei modelli
- Configurazione block

**Elimina modulo**:
```bash
# Prima richiede conferma backup
curl -X DELETE "/api/v1/modules/{id}" \
  -H "Authorization: Bearer <token>"

# Con backup effettuato
curl -X DELETE "/api/v1/modules/{id}?backup=true" \
  -H "Authorization: Bearer <token>"
```

### Dashboard App-Like

Quando un modulo viene pubblicato, diventa accessibile come **applicazione standalone** con un'esperienza utente migliorata.

**Accesso**:
- Menu **Applicazioni** → Nome modulo → apre la dashboard
- URL diretto: `/projects/{id}/app/{module_name}`

**Caratteristiche**:
```
┌─────────────────────────────────────────────────────────────┐
│  [←] 📦 NOME MODULO                      v1.0             │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────┬──────────────────────────────────────────┐│
│ │ Panoramica │  Statistiche, descrizione, componenti   ││
│ │ ├─ Block 1 │                                           ││
│ │ ├─ Block 2 │  [Contenuto Block selezionato]           ││
│ │ └─ Block 3 │                                           ││
│ └─────────────┴──────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

- **Header App-like**: Titolo, versione, breadcrumb
- **Sidebar interna**: Navigazione tra Panoramica, Blocchi Layout e Modelli Dati
- **Panoramica**: Statistiche, descrizione, lista Blocchi e Modelli
- **Blocchi Layout**: I block VisualBuilder vengono renderizzati con BlockRenderer
- **Modelli Dati**: Accesso ai modelli dati del modulo

#### Renderizzazione Blocchi

I Block associati al modulo vengono renderizzati automaticamente nella dashboard:

1. **VisualBuilder Config**: Se il Block ha una configurazione VisualBuilder (`visual_builder_config`), viene renderizzato usando `StaticBlockRenderer`
2. **Componenti Legacy**: Se il Block ha solo ID dei componenti, mostra la lista dei componenti
3. **Navigazione**: I pulsanti supportano azioni `navigate` con placeholder `{projectId}`

**Esempio Block GDO**:
```json
{
  "id": "gdo-card-1",
  "type": "card",
  "config": { "title": "Riconciliazione GDO" },
  "children": [
    {
      "type": "button",
      "config": {
        "label": "Apri Modulo",
        "action": "navigate",
        "path": "/projects/{projectId}/app/gdo_reconciliation"
      }
    }
  ]
}
```

### Sistema API Ibrido

Ogni modulo pubblicato espone automaticamente API CRUD per i suoi modelli, con la possibilità di aggiungere endpoint personalizzati.

**Endpoint disponibili**:

| Metodo | Endpoint | Descrizione |
|--------|----------|-------------|
| GET | `/api/modules/{module_name}` | Info modulo e modelli |
| GET | `/api/modules/{module_name}/{model_name}` | Lista record |
| POST | `/api/modules/{module_name}/{model_name}` | Crea record |
| GET | `/api/modules/{module_name}/{model_name}/{id}` | Leggi record |
| PUT | `/api/modules/{module_name}/{model_name}/{id}` | Aggiorna record |
| DELETE | `/api/modules/{module_name}/{model_name}/{id}` | Elimina record |

**Esempio di utilizzo**:

```bash
# Lista clienti dal modulo "vendite"
curl -X GET "/api/modules/vendite/clienti" \
  -H "Authorization: Bearer <token>"

# Crea nuovo ordine
curl -X POST "/api/modules/vendite/ordini" \
  -H "Authorization: Bearer <token>" \
  -d '{"cliente_id": 1, "totale": 1500}'
```

### Relazioni tra Moduli

I moduli possono comunicare tra loro tramite **Foreign Key esplicite**. Usa il tipo di campo "relation" specificando il modello di destinazione.

**Configurazione**:
1. Crea un campo di tipo "relation"
2. Nelle opzioni specifica `target_table`: nome del modello di destinazione

```json
{
  "target_table": "clienti",
  "target_model_id": 5
}
```

Il sistema automaticamente解析 le relazioni e permette di:
- Visualizzare i dati correlati nelle tabelle
- Filtrare per campo correlato
- Navigare tra entità collegate

**Vantaggi**:
- Esperienza "Applicazione" dedicata
- Navigazione interna al modulo
- I moduli pubblicati appaiono nel menu Applicazioni prima dei singoli modelli

---

## Integrazione tra Moduli

I moduli comunicano attraverso l'**EventBus**.

**Esempio - Ciclo di vendita**:

1. Commerciale crea **Ordine** (Vendite)
2. Sistema verifica **disponibilità** (Magazzino)
3. Se confermato, genera **DDT**
4. **Contabilità** registra la fattura

Tutto automatico una volta configurato.

Vedi [06_AUTOMAZIONE.md](06_AUTOMAZIONE.md) per dettagli su Hook, Eventi e Workflow.

---

## Roadmap Moduli

| Modulo | Descrizione | Stato |
|--------|-------------|-------|
| Contabilità | Piano conti, prima nota, partitario, fatt. elettronica | 70% |
| HR | Anagrafica dipendenti, presenze, ferie | 50% |
| Produzione | Distinte basi, cicli, commesse | Pianificato |
| CRM | Pipeline commerciali, campagne | Pianificato |
| Progetti | Gestione task e milestone | Pianificato |
| Documentale | Archiviazione documenti | Pianificato |
| Helpdesk | Ticket assistenza | Pianificato |

---

*Documento aggiornato: Febbraio 2026*
