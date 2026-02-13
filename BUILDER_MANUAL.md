# Manuale Utente del Builder

Il **Builder** è il cuore "Low-Code" di FlaskERP. Permette agli amministratori di creare, modificare ed estendere le funzionalità dell'applicazione direttamente dall'interfaccia web, senza scrivere una singola riga di codice.

Questa guida ti accompagnerà attraverso i passaggi fondamentali per utilizzare il Builder e creare la tua applicazione personalizzata.

## 1. Gestione dei Progetti

Un **Progetto** è un contenitore isolato per le tue applicazioni. Ogni progetto ha i propri modelli, dati, membri e impostazioni.

### Creare un Nuovo Progetto

1.  Naviga alla pagina di **Selezione Progetto**.
2.  Se sei un amministratore, vedrai un pulsante **"Crea Progetto"**. Cliccalo.
3.  Compila il form:
    -   **Nome Interno**: Un identificatore unico per il progetto (es. `gestione_flotta`). Usa solo lettere minuscole, numeri e underscore. **Non può essere modificato dopo la creazione.**
    -   **Titolo Visibile**: Il nome che apparirà nell'interfaccia (es. "Gestione Flotta Aziendale").
    -   **Versione**: La versione iniziale del tuo progetto (es. `1.0.0`).
    -   **Descrizione**: Una breve spiegazione dello scopo del progetto.
4.  Clicca su **"Crea"**. Verrai reindirizzato alla dashboard del nuovo progetto.

### Gestire le Impostazioni di un Progetto

Una volta dentro un progetto, puoi modificarne le impostazioni:
1.  Nel menu laterale, clicca su **"Impostazioni"**.
2.  Da qui puoi aggiornare il **Titolo**, la **Descrizione** e la **Versione**.
3.  In fondo alla pagina, nella "Danger Zone", puoi **eliminare il progetto**. Questa azione è irreversibile e cancellerà tutti i modelli e i dati associati.

### Gestire i Membri del Progetto

Puoi decidere quali utenti hanno accesso a un progetto.
1.  Nel menu laterale, clicca su **"Membri del Team"**.
2.  Vedrai la lista degli utenti che fanno parte del progetto.
3.  Per aggiungere un nuovo membro, clicca su **"Aggiungi Membro"**.
    -   Se sei **Admin**, potrai selezionare un utente da una lista.
    -   Se sei **Owner** (proprietario), dovrai inserire l'ID numerico dell'utente.
4.  Per rimuovere un membro, clicca sull'icona del cestino accanto al suo nome.

---

## 2. Gestione dei Modelli (Tabelle)

Un **Modello** rappresenta una tabella nel database (es. `Veicoli`, `Manutenzioni`).

### Creare un Nuovo Modello

1.  Assicurati di essere nel progetto corretto.
2.  Nel menu laterale, vai su **Amministrazione -> Builder**.
3.  Clicca su **"Create New Model"**.
4.  Seleziona il **Progetto** a cui appartiene il modello.
5.  Compila i campi:
    -   **Internal Name**: Il nome della tabella (es. `vehicles`).
    -   **Display Title**: Il nome che apparirà nel menu (es. `Veicoli`).
6.  Clicca **Create**.

### Configurare i Permessi (ACL)

⚠️ **Passaggio Fondamentale**: Senza permessi, nessuno (nemmeno l'admin) potrà vedere o usare il nuovo modulo.

1.  Dalla lista dei modelli nel Builder, clicca su **"Manage"** accanto al tuo nuovo modello.
2.  Nella pagina di dettaglio, clicca su **"Edit Model"**.
3.  Nella sezione **Permissions (ACL)**, spunta le caselle per i ruoli che devono accedere.
    -   **Read**: Permette di visualizzare i dati.
    -   **Write**: Permette di creare, modificare ed eliminare dati.
4.  Clicca **"Update Model"**.

### Aggiungere Campi al Modello

Nella pagina di dettaglio del modello, vedrai la lista dei campi.
1.  Clicca su **"Add New Field"**.
2.  Compila il form:
    -   **Field Name**: Nome della colonna nel DB (es. `license_plate`).
    -   **Field Title**: Etichetta visualizzata nel form (es. `Targa`).
    -   **Type**: Il tipo di dato. Scegli tra `String`, `Integer`, `Date`, `Select`, `Relation`, etc.
    -   **Required/Unique**: Imposta se il campo è obbligatorio o deve essere unico.
3.  A seconda del tipo, appariranno opzioni aggiuntive (es. opzioni per `Select`, tabella target per `Relation`).
4.  Salva il campo.

### Generare la Tabella nel Database

Dopo aver definito i campi, devi creare la tabella fisica nel database.
1.  Nella pagina di dettaglio del modello, clicca sul pulsante blu **"Generate/Update DB Table"**.
2.  Conferma l'operazione.

Se in futuro modificherai i campi (aggiungendo, rimuovendo o cambiando tipo), dovrai cliccare di nuovo su questo pulsante per sincronizzare lo schema del database.

---

## 3. Utilizzare l'Applicazione Creata

Una volta generata la tabella, ricarica la pagina (F5). Nel menu laterale, sotto la voce **"Applicazioni"**, apparirà il tuo nuovo modulo. Cliccandoci, accederai a una pagina CRUD completa per gestire i tuoi dati.
