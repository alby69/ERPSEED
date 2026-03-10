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

Mentre un SysModel definisce i **dati**, un Block definisce l'**interfaccia**. Un Block può contenere:
- Una tabella per visualizzare dati
- Un form per modificare dati
- Un chart per statistiche
- Relazioni tra questi componenti

### Creare un Block

1. **Vai su Builder → Blocchi**
2. **Clicca "Nuovo Block"**
3. **Assegna un nome** e descrizione
4. **Aggiungi Component** selezionando gli Archetypi
5. **Definisci le relazioni** tra i component

### Esempio Pratico: Card Cliente

Crea un Block "Card Cliente" che contiene:
- **Component 1**: Form (dati anagrafici del cliente)
- **Component 2**: Table (storico ordini)
- **Component 3**: Chart (andamento acquisti)

Le relazioni collegano i component: selezionando un cliente nel form, la tabella mostra i suoi ordini.

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
