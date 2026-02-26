# Guida al Builder

## Cos'è il Builder

Il Builder è il cuore low-code di FlaskERP. È uno strumento integrato nell'interfaccia web che permette di creare, modificare e gestire entità aziendali senza scrivere codice. Attraverso il Builder puoi definire tabelle, campi, relazioni, viste e molto altro, il tutto in modo visuale e intuitivo.

Il Builder sfrutta il pilastro del Metaprogramming per generare automaticamente tutto ciò che serve: le tabelle nel database, le API REST, i form e le tabelle nell'interfaccia utente. Tu ti concentri su cosa vuoi modellare, il sistema si occupa di come implementarlo.

---

## Accedere al Builder

Per utilizzare il Builder, accedi all'interfaccia di FlaskERP come amministratore. Dal menu di navigazione trovi la sezione Builder che contiene:

- **Modelli**: Le entità che hai creato
- **Blocchi**: Componenti riutilizzabili
- **Campi**: Definizioni dei campi

Se hai un nuovo progetto, partirai con un workspace vuoto dove potrai creare le tue entità da zero.

---

## Creare un Nuovo Modello

Un modello in FlaskERP corrisponde a una tabella nel database e rappresenta un'entità del tuo business. Ad esempio: Clienti, Fornitori, Prodotti, Ordini.

### Passaggi per Creare un Modello

1. **Accedi alla sezione Builder** dal menu
2. **Clicca su "Nuovo Modello"**
3. **Compila le informazioni base**:

   - **Nome visualizzato**: Il nome che verrà mostrato nell'interfaccia (es: "Clienti")
   - **Nome tabella**: Il nome tecnico nel database (es: "clienti", tutto minuscolo)
   - **Descrizione**: Una breve descrizione dell'entità

4. **Clicca "Crea"**

Il modello viene creato nel sistema, ma la tabella nel database non esiste ancora. Questo ti permette di definire tutti i campi prima di procedere.

---

## Aggiungere Campi

Dopo aver creato un modello, puoi aggiungere tutti i campi necessari. Ogni campo ha un tipo specifico che determina come i dati vengono gestiti e visualizzati.

### Tipi di Campo Base

| Tipo | Utilizzo | Esempio |
|------|----------|---------|
| **string** | Testo breve, codici | Codice cliente, partita IVA |
| **text** | Testo lungo, note | Descrizione, note |
| **integer** | Numeri interi | Quantità, anno |
| **decimal** | Numeri con decimali | Prezzo, importo |
| **boolean** | Sì/No | Attivo, bloccato |
| **date** | Solo data | Data nascita, data ordine |
| **datetime** | Data e ora | Data creazione |
| **select** | Scelta da menu a tendina | Stato, categoria |

### Configurazione di un Campo

Per ogni campo puoi impostare:

- **Label**: Il nome visualizzato nell'interfaccia
- **Placeholder**: Testo di esempio nel form
- **Required**: Se il campo è obbligatorio
- **Unique**: Se il valore deve essere univoco nel sistema
- **Default**: Valore predefinito quando si crea un nuovo record

### Esempio Pratico: Creare il Modello "Prodotti"

Immaginiamo di voler creare un modulo per gestire i prodotti:

1. **Crea il modello** chiamato "Prodotto" con tabella "prodotti"
2. **Aggiungi i campi**:
   - `codice` (string, required, unique) - codice identificativo
   - `nome` (string, required) - nome prodotto
   - `descrizione` (text) - descrizione dettagliata
   - `prezzo` (decimal) - prezzo di vendita
   - `costo` (decimal) - costo di acquisto
   - `giacenza` (integer) - quantità a magazzino
   - `attivo` (boolean, default: true) - se il prodotto è vendibile
   - `categoria` (select) - categoria del prodotto

3. **Genera la tabella** nel database

In pochi minuti hai un modulo prodotti completamente funzionante con CRUD automatico.

---

## Tipi di Campo Avanzati

Oltre ai tipi base, il Builder supporta campi avanzati che permettono di modellare situazioni più complesse.

### Campo Relazione

Il campo relazione crea un collegamento tra due modelli. È uno dei più potenti perché permette di costruire la struttura dati del tuo business.

**Esempio**: Collegare gli ordini ai clienti

1. Crea il modello "Ordine"
2. Aggiungi un campo "cliente" di tipo **relation**
3. Seleziona il modello target "Clienti"
4. Scegli come visualizzare la relazione (dropdown con ricerca)

Il sistema crea automaticamente:
- Il collegamento nel database (foreign key)
- Il dropdown nell'interfaccia per selezionare il cliente
- La possibilità di vedere tutti gli ordini di un cliente

### Campo Calcolato

Il campo calcolato mostra un valore derivato da altri campi. Il calcolo può essere:

**Lato server** (formula): Calcoli matematici eseguiti dal backend
```
totale = quantita * prezzo_unitario
```

**Lato client** (calculated): Calcoli eseguiti dal browser
```
nome_completo = nome + ' ' + cognome
```

### Campo Riepilogo

Il campo riepilogo aggrega dati da modelli correlati. Utile per vedere informazioni derivate.

**Esempio**: Numero di ordini per cliente
- Tipo: **summary**
- Target: Ordini
- Campo da aggregare: id
- Funzione: count (conteggio)

Ogni cliente vedrà automaticamente quanti ordini ha effettuato.

### Campo Lookup

Il campo lookup mostra un valore letto da un altro modello, senza creare una relazione completa.

**Esempio**: Mostrare la categoria del prodotto nella lista ordini
- Tipo: **lookup**
- Target: Prodotti
- Campo da leggere: categoria

---

## Relazioni tra Modelli

Il Builder permette di definire tre tipi di relazioni:

### Uno a Uno

Un record è collegato a un solo altro record. Raramente usato nelle entità business, più comune per dati annessi.

Esempio: Soggetto ha un indirizzo principale### Uno.

 a Molti

Un record ha molti record correlati. È il tipo più comune.

Esempio: Un Cliente ha molti Ordini.

### Molti a Molti

Molti record possono essere collegati a molti altri.

Esempio: Un Prodotto può appartenere a più Categorie, e una Categoria può contenere molti Prodotti.

Per creare relazioni molti a molti, il Builder genera automaticamente una tabella di collegamento.

---

## Viste Alternative

Oltre alla vista tabella standard, puoi definire viste alternative per visualizzare i dati in modo diverso.

### Vista Kanban

La vista Kanban mostra i record come schede in colonne, ideale per workflow basati su stati.

**Configurazione**:
1. Aggiungi un campo "stato" di tipo select (es: bozza, confermato, evaso, annullato)
2. Nelle impostazioni del modello, seleziona "Vista predefinita: Kanban"
3. Indica quale campo rappresenta lo stato

Il sistema crea automaticamente una board drag-and-drop dove puoi spostare le schede tra le colonne per cambiare stato.

### Altre Viste

- **Calendario**: Per appuntamenti e scadenze
- **Mappa**: Per visualizzare record geolocalizzati

---

## Generare la Tabella nel Database

Dopo aver definito modello e campi, devi generare la tabella fisica nel database.

1. **Vai sul modello** che hai creato
2. **Clicca "Genera Tabella"**
3. **Conferma** l'operazione

Il sistema esegue automaticamente:
- CREATE TABLE nel database PostgreSQL
- Creazione degli indici
- Setup delle foreign key per le relazioni

**Nota**: La prima generazione è sempre sicura. Se modifichi la struttura successivamente (aggiungi campi, cambi tipi), il sistema esegue ALTER TABLE preservando i dati esistenti.

### Operazioni di Manutenzione

Dalla scheda del modello hai anche accesso a:

- **Sincronizza**: Applica modifiche al database
- **Ricrea**: Drop e ricrea la tabella (attenzione: cancella i dati)
- **Backup**: Esporta i dati in CSV prima di operazioni destructive
- **Reset**: Ricrea da zero mantenendo la definizione

---

## Sistema di Validazione

Il Builder permette di definire regole di validazione sui campi.

### Validazione Built-in

- **Required**: Campo obbligatorio
- **Unique**: Valore non duplicato
- **Min/Max length**: Lunghezza minima e massima per stringhe
- **Min/Max value**: Valore minimo e massimo per numeri
- **Pattern**: Espressione regolare per formati specifici

### Validazione Personalizzata

Puoi aggiungere regole custom usando espressioni regolari. Ad esempio, per validare un codice fiscale italiano:

```
Pattern: ^[A-Z]{6}[0-9]{2}[A-Z][0-9]{2}[A-Z][0-9]{3}[A-Z]$
```

---

## Gestione Permessi

Ogni modello ha un sistema di permessi integrato che controlla chi può fare cosa.

### Livelli di Permesso

| Livello | Azioni Consentite |
|---------|-------------------|
| **Admin** | Tutte le operazioni |
| **Editor** | Crea, legge, modifica |
| **Viewer** | Solo lettura |
| **Nessuno** | Nessun accesso |

### Configurare i Permessi

1. **Apri il modello** nel Builder
2. **Vai sulla scheda "Permessi"**
3. **Aggiungi regole** specificando ruolo e azioni consentite

I permessi vengono applicati sia sull'interfaccia che sulle API.

---

## Clonare un Modello

Se hai bisogno di un modello simile a uno esistente, puoi clonarlo:

1. **Apri il modello** che vuoi clonare
2. **Clicca "Clona"**
3. **Indica il nuovo nome**

Tutti i campi, le relazioni e le configurazioni vengono copiati. Puoi poi modificare ciò che serve.

Questa funzione è utilissima per creare varianti: ad esempio, partendo dal modulo Ordini, puoi creare Preventivi o Ordini di acquisto.

---

## Best Practices

### Pianifica Prima di Creare

Prima di creare un modello, fermati a pensare:

- Quali informazioni devo tracciare?
- Come si relazionano con le altre entità?
- Quali report o viste mi serviranno?
- Chi dovrà accedere a questi dati?

### Inizia Semplice

Non cercare di modellare tutto subito. Crea i campi essenziali, usa il sistema, scopri cosa manca. Il Builder permette di aggiungere campi in qualsiasi momento.

### Usa Nomi Chiari

Scegli nomi descrittivi per modelli e campi. "Fattura" è meglio di "Doc1", "data_consegna_prevista" è meglio di "dcp".

### Testa Sempre

Dopo aver creato un modello, inserisci alcuni record di test. Verifica che i form funzionino, che le relazioni siano corrette, che i calcoli siano esatti.

### Backup Prima di Modifiche Grandi

Se stai per fare modifiche significative (cambiare tipi di campi, eliminare campi), scarica un backup prima. Meglio prevenire che rimediare.

---

## Risoluzione Problemi

### La tabella non appare nel menu

- Verifica che il modello sia attivo
- Controlla che la tabella sia stata generata
- Assicurati di avere permessi di accesso

### Errore nel creare una relazione

- Verifica che il modello target esista
- Controlla che non ci siano relazioni circolari
- Assicati di avere i permessi su entrambi i modelli

### I dati non si salvano

- Controlla la validazione dei campi
- Verifica che i campi required abbiano valore
- Consulta i log di sistema per errori

---

*Documento aggiornato: Febbraio 2026*
