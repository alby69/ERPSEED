# Guida al Builder

## Cos'è il Builder

Il Builder è il cuore low-code di ERPSeed. È uno strumento integrato nell'interfaccia web che permette di creare, modificare e gestire entità aziendali senza scrivere codice. Attraverso il Builder puoi definire tabelle, campi, relazioni, viste e molto altro.

Il Builder sfrutta il metaprogramming per generare automaticamente: le tabelle nel database, le API REST, i form e le tabelle nell'interfaccia utente.

---

## Accedere al Builder

Per utilizzare il Builder, accedi all'interfaccia di ERPSeed come amministratore. Dal menu di navigazione trovi la sezione Builder che contiene:

- **Modelli**: Le entità dati (SysModel)
- **Blocchi**: Collezioni di componenti UI (Block)
- **Componenti**: I singoli elementi UI (Component)

---

## Creare un Nuovo Modello (SysModel)

Un modello in ERPSeed corrisponde a una tabella nel database e rappresenta un'entità del tuo business.

### Passaggi per Creare un Modello

1. **Accedi alla sezione Builder** dal menu
2. **Clicca su "Nuovo Modello"**
3. **Compila le informazioni base**:
   - **Nome visualizzato**: Il nome mostrato nell'interfaccia (es: "Clienti")
   - **Nome tabella**: Il nome tecnico nel database (es: "clienti")
   - **Descrizione**: Una breve descrizione dell'entità
4. **Clicca "Crea"**

Il modello viene creato nel sistema, ma la tabella nel database non esiste ancora.

---

## Aggiungere Campi (SysField)

Dopo aver creato un modello, puoi aggiungere tutti i campi necessari.

### Tipi di Campo

| Tipo | Utilizzo | Esempio |
|------|----------|---------|
| **string** | Testo breve | Codice cliente, partita IVA |
| **text** | Testo lungo | Descrizione, note |
| **integer** | Numeri interi | Quantità, anno |
| **decimal** | Numeri con decimali | Prezzo, importo |
| **boolean** | Sì/No | Attivo, bloccato |
| **date** | Solo data | Data nascita |
| **datetime** | Data e ora | Data creazione |
| **select** | Scelta da menu | Stato, categoria |

### Configurazione di un Campo

Per ogni campo puoi impostare:
- **Label**: Nome visualizzato
- **Placeholder**: Testo di esempio
- **Required**: Campo obbligatorio
- **Unique**: Valore univoco
- **Default**: Valore predefinito

---

## Campi Avanzati

### Campo Relazione

Crea un collegamento tra due modelli.

**Esempio**: Collegare Ordini a Clienti
1. Crea il modello "Ordine"
2. Aggiungi un campo "cliente" di tipo **relation**
3. Seleziona il modello target "Clienti"

Il sistema crea automaticamente:
- Foreign key nel database
- Dropdown per selezione
- Navigazione bidirezionale

### Campo Calcolato

Valore derivato da altri campi.

**Server** (formula): `totale = quantita * prezzo_unitario`
**Client** (calculated): `nome_completo = nome + ' ' + cognome`

### Campo Riepilogo

Aggrega dati da modelli correlati.

**Esempio**: Numero ordini per cliente
- Tipo: **summary**
- Target: Ordini
- Funzione: count

---

## Relazioni tra Modelli

### Uno a Uno
Un record collegato a un solo altro record.
Esempio: Soggetto → IndirizzoPrincipale

### Uno a Molti
Un record ha molti record correlati.
Esempio: Cliente → Ordini

### Molti a Molti
Molti record collegati a molti altri.
Esempio: Prodotto ↔ Categoria

---

## Viste Alternative

Oltre alla vista tabella standard, puoi definire viste alternative.

### Vista Kanban

Ideale per workflow basati su stati.

1. Aggiungi campo "stato" di tipo select
2. Seleziona "Vista predefinita: Kanban"
3. Indica il campo stato

### Altre Viste
- **Calendario**: Per appuntamenti
- **Mappa**: Per geolocalizzazione

---

## Generare la Tabella

Dopo aver definito modello e campi:

1. **Vai sul modello**
2. **Clicca "Genera Tabella"**
3. **Conferma**

Il sistema esegue CREATE TABLE con indici e foreign key.

### Operazioni di Manutenzione

- **Sincronizza**: Applica modifiche (ALTER TABLE)
- **Ricrea**: Drop e ricrea (ATTENZIONE: cancella dati)
- **Backup**: Esporta in CSV
- **Reset**: Ricrea da zero

---

## Creare un Block

Un **Block** è una collezione di Component con relazioni.

### Cos'è un Block

Mentre un SysModel definisce i **dati**, un Block definisce l'**interfaccia**. 
Un Block può contenere:
- Una tabella per visualizzare dati
- Un form per modificare dati
- Un chart per statistiche
- Relazioni tra questi componenti

### Creare un Block (via UI)

1. **Vai su Builder → Blocchi** (nel menu laterale)
2. **Clicca "New Block"**
3. **Assegna un nome** e descrizione
4. Si aprirà il **Visual Builder** dove potrai:
   - Aggiungere Component dalla palette
   - Trascinare e posizionare i componenti
   - Configurare ogni componente
   - Definire relazioni tra componenti
5. **Salva** il Block

### Creare un Block (via API)

```bash
# Crea un nuovo Block
curl -X POST "http://localhost:5000/api/projects/1/blocks" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Card Cliente",
    "description": "Scheda completa cliente",
    "component_ids": [1, 2, 3]
  }'
```

### Esempio Pratico: Card Cliente

Crea un Block "Card Cliente" che contiene:
- **Component 1**: Form (dati anagrafici del cliente)
- **Component 2**: Table (storico ordini)
- **Component 3**: Chart (andamento acquisti)

Le relazioni collegano i component: selezionando un cliente nel form, la tabella mostra i suoi ordini.

### Ciclo di Vita di un Block

```
draft → testing → published
```

1. **Draft**: Block in fase di sviluppo
2. **Testing**: Block in test (puoi eseguire i test)
3. **Published**: Block pronto per l'uso

---

## Block Template (Block Riutilizzabili)

I **Block Template** permettono di creare Block parametrici che possono essere riutilizzati in più Moduli o Progetti con personalizzazioni diverse.

### Cos'è un Block Template

Un Block Template è un Block pubblicato che può essere usato come base per creare altre istanze. Ogni istanza può avere **parametri diversi** senza dover duplicare la definizione.

### Parametri Supportati

| Parametro | Descrizione | Esempio |
|-----------|-------------|---------|
| `title` | Titolo visualizzato | "Scheda Cliente" |
| `model_id` | ID del modello dati | 5 |
| `fields` | Campi da mostrare | ["nome", "email"] |
| `style` | Stile grafico | "compact" |
| `permissions` | Visibilità | { "view": ["admin"] } |

### Creare un Block Template

**Passaggi:**

1. **Crea un Block** normale (vedi sezione precedente)
2. **Aggiungi i Component** necessari nel Visual Builder
3. **Pubblica il Block** (esegui i test e certifica)
4. **Converti in Template**: clicca "Make Template" nella lista Blocchi

**Via API:**
```bash
# Pubblica e certifica un block
curl -X POST "http://localhost:5000/api/blocks/1/certify" \
  -H "Authorization: Bearer <token>"

# Converti in template
curl -X POST "http://localhost:5000/api/blocks/1/convert-to-template" \
  -H "Authorization: Bearer <token>"
```

### Usare un Block Template

Dopo aver creato un Template, puoi creare istanze con parametri personalizzati:

**Via UI:**
1. Vai su **Builder → Blocchi**
2. Clicca **"New from Template"**
3. Seleziona il Template desiderato
4. Inserisci i parametri override in JSON
5. Crea l'istanza

**Via API:**
```bash
# Crea un'istanza da template
curl -X POST "http://localhost:5000/api/projects/1/blocks" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "template_id": 5,
    "name": "Card Fornitore",
    "description": "Scheda personalizzata per fornitori",
    "params_override": {
      "title": "Scheda Fornitore",
      "model_id": 10,
      "fields": ["ragione_sociale", "partita_iva", "telefono"]
    }
  }'
```

### Vantaggi dei Block Template

1. **Riutilizzo**: Uno stesso template può essere usato in contesti diversi
2. **Manutenzione centrale**: Modifiche al template si propagano (se desiderato)
3. **Personalizzazione**: Ogni istanza può avere parametri diversi
4. **Standardizzazione**: Crea librerie di block standard per l'organizzazione

### Esempio Pratico

**Template: "Card Dati Base"**
```json
{
  "name": "Card Dati Base",
  "params_override": {
    "title": "Dati",
    "fields": ["name", "email"],
    "style": "default"
  }
}
```

**Istanza 1: "Scheda Cliente"**
```json
{
  "template_id": 1,
  "name": "Scheda Cliente",
  "params_override": {
    "title": "Scheda Cliente",
    "model_id": 5,
    "fields": ["nome", "cognome", "email", "telefono"]
  }
}
```

**Istanza 2: "Scheda Fornitore"**
```json
{
  "template_id": 1,
  "name": "Scheda Fornitore", 
  "params_override": {
    "title": "Scheda Fornitore",
    "model_id": 10,
    "fields": ["ragione_sociale", "partita_iva", "indirizzo"]
  }
}
```

---

## Visual Builder

Il **Visual Builder** è uno strumento integrato che permette di creare interfacce utente trascinando e rilasciando componenti sulla canvas.

### Accedere al Visual Builder

1. **Da Builder → Blocchi**: Crea un nuovo Block o modifica uno esistente
2. **Da CustomModulesPage**: Crea un Block direttamente dalla pagina dei moduli

### Componenti Disponibili

| Componente | Descrizione |
|------------|-------------|
| **Card** | Contenitore con titolo |
| **Statistic** | Card per statistiche con valore numerico |
| **Row** | Riga del grid system |
| **Col** | Colonna del grid system |
| **Button** | Pulsante con azione |
| **Text** | Testo semplice |
| **Title** | Titolo con livello |
| **Space** | Spaziatura tra elementi |
| **Table** | Tabella per visualizzare dati |
| **Div** | Contenitore generico |

### Configurazione Componenti

Ogni componente può essere configurato con:
- **x, y**: Posizione sulla canvas
- **w, h**: Larghezza e altezza
- **config**: Oggetto di configurazione specifico per tipo
- **children**: Componenti nidificati

### Azioni dei Pulsanti

I pulsanti possono eseguire diverse azioni:

| Azione | Descrizione |
|--------|-------------|
| `navigate` | Naviga a un percorso |
| `navigate_external` | Apre URL esterno |
| Custom | Callback personalizzato |

**Esempio di configurazione button**:
```json
{
  "type": "button",
  "config": {
    "label": "Apri Modulo",
    "type": "primary",
    "action": "navigate",
    "path": "/projects/{projectId}/app/gdo_reconciliation"
  }
}
```

Il placeholder `{projectId}` viene sostituito automaticamente.

### BlockRenderer

Il **BlockRenderer** è il componente React che renderizza dinamicamente i Block basati sulla loro configurazione VisualBuilder.

**Usage**:
```jsx
import { StaticBlockRenderer } from '@/components/BlockRenderer';

<StaticBlockRenderer 
  components={block.visual_builder_config}
  data={{}}
  projectId={projectId}
  onAction={(action, config, data) => {
    console.log('Azione:', action);
  }}
/>
```

---

## Sistema di Validazione

### Validazione Built-in
- **Required**: Campo obbligatorio
- **Unique**: Valore non duplicato
- **Min/Max length**: Lunghezza stringhe
- **Min/Max value**: Valori numerici
- **Pattern**: Espressione regolare

### Validazione Personalizzata
```
Pattern: ^[A-Z]{6}[0-9]{2}[A-Z][0-9]{2}[A-Z][0-9]{3}[A-Z]$
```

---

## Gestione Permessi

Ogni modello ha un sistema di permessi granulare.

### Livelli di Permesso

| Livello | Azioni |
|---------|--------|
| **Admin** | Tutte le operazioni |
| **Editor** | Crea, legge, modifica |
| **Viewer** | Solo lettura |
| **Nessuno** | Nessun accesso |

### Configurare i Permessi

1. **Apri il modello** nel Builder
2. **Vai su "Permessi"**
3. **Aggiungi regole** per ruolo

---

## Clonare un Modello

Per creare varianti:

1. **Apri il modello** da clonare
2. **Clicca "Clona"**
3. **Indica il nuovo nome**

Tutti i campi e configurazioni vengono copiati.

---

## Best Practices

### Pianifica Prima
- Quali informazioni servono?
- Come si relazionano?
- Quali report servono?
- Chi accederà?

### Inizia Semplice
Crea i campi essenziali, usa il sistema, scopri cosa manca.

### Usa Nomi Chiari
"Fattura" è meglio di "Doc1"

### Testa Sempre
Inserisci dati di test, verifica relazioni e calcoli.

### Backup Prima di Modifiche Grandi
Scarica un backup prima di operazioni destructive.

---

## Risoluzione Problemi

### La tabella non appare nel menu
- Verifica che il modello sia attivo
- Controlla che la tabella sia stata generata
- Assicurati di avere permessi

### Errore in una relazione
- Verifica che il modello target esist
- Controlla che non ci siano cicli
- Assicurati di avere permessi su entrambi

### I dati non si salvano
- Controlla la validazione
- Verifica i campi required
- Consulta i log di sistema

---

*Documento aggiornato: Febbraio 2026*
