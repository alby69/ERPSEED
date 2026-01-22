# 🏗️ Manuale Utente ERP Builder

Il **Builder (Admin)** è lo strumento che ti permette di creare nuove funzionalità (moduli) nell'ERP senza scrivere codice.

## Guida Passo-Passo

### Passo 1: Creare un Nuovo Modello (Tabella)
1.  Vai nel menu **Builder (Admin)**.
2.  Clicca su **"Create New Model"**.
3.  Compila il form:
    -   **Internal Name**: Il nome della tabella nel database (es. `fleet_vehicles`). Usa solo lettere minuscole e underscore.
    -   **Display Title**: Il nome visibile nel menu (es. `Gestione Flotta`).
    -   **Description**: Una breve descrizione.
4.  Clicca su **Create**.

### Passo 2: Configurare i Permessi (Importante!)
⚠️ **Se non configuri i permessi, non potrai accedere al modulo e verrai reindirizzato al login.**
1.  Nella lista dei modelli, clicca su **Manage Model** (o sul nome del modello).
2.  Clicca su **Edit Model** (pulsante in alto a destra).
3.  Nella tabella **Permissions (ACL)**, spunta le caselle **Read** e **Write** per il ruolo `admin` (e altri ruoli se necessario).
4.  Clicca **Update Model**.

### Passo 3: Aggiungere Campi (Colonne)
Nella pagina di dettaglio del modello, clicca su **"Add New Field"**.

#### Tipi di Campo Disponibili:
-   **String**: Testo breve (es. Nome, Targa). Supporta validazione Regex.
-   **Text**: Testo lungo (es. Descrizione, Note).
-   **Integer**: Numero intero (es. Quantità). Supporta formattazione (Valuta, %, Suffissi).
-   **Float**: Numero decimale (es. Prezzo). Supporta formattazione.
-   **Boolean**: Vero/Falso (Checkbox).
-   **Date / DateTime**: Date e orari.
-   **Select**: Menu a tendina statico. Inserisci le opzioni come lista JSON `["A", "B"]` o premendo Invio nel builder.
-   **Relation**: Collegamento a un'altra tabella (es. Cliente, Utente).
-   **File / Image**: Upload di file.
-   **Formula**: Calcolo lato backend (Python).
-   **Calculated**: Calcolo lato frontend (JS).
-   **Summary**: Aggregazione da tabelle collegate (Somma, Media, Conteggio, Min, Max).
-   **Lookup**: Recupero valore da tabella collegata.
-   **Master-Detail (Linee/Righe)**: Tabella annidata per gestire righe di dettaglio (es. Righe Ordine).

#### Esempi Comuni:
-   **Targa** -> Type: `String`, Name: `license_plate`, Required: `Yes`, Unique: `Yes`.
-   **Chilometraggio** -> Type: `Integer`, Name: `mileage`.
-   **Data Immatricolazione** -> Type: `Date`, Name: `registration_date`.
-   **Tipo Veicolo** -> Type: `Select`. Nel campo *Options (List)* scrivi le opzioni (es. `Auto`, `Furgone`, `Moto`).
-   **Assegnatario** -> Type: `Relation`. In *Target Table* seleziona `users`.

### Funzionalità Avanzate

#### 1. Formattazione Numerica
Per i campi **Integer** e **Float**, puoi definire come vengono visualizzati i numeri:
-   **Formato**: Valuta (€, $), Percentuale, Decimale fisso.
-   **Suffisso**: Unità di misura personalizzata (es. `kg`, `m²`, `pz`).

#### 2. Campi di Riepilogo (Summary)
Permettono di calcolare totali da una tabella collegata (es. Totale Ordine dalle Righe).
-   **Funzioni**: Somma (SUM), Media (AVG), Conteggio (COUNT), Minimo (MIN), Massimo (MAX).
-   **Configurazione**: Seleziona la tabella target, la chiave esterna e il campo su cui eseguire il calcolo.

#### 3. Relazioni Master-Detail
Per creare un modulo complesso come "Ordini" (Testata + Righe):
1.  Crea prima il modello **Detail** (es. `order_lines`) con un campo `relation` verso il Master (es. `order_id`).
2.  Crea il modello **Master** (es. `orders`).
3.  Nel Master, aggiungi un campo di tipo **Master-Detail (Linee/Righe)**.
    -   **Target Table**: `order_lines`.
    -   **Foreign Key**: `order_id`.
4.  Il sistema genererà automaticamente una griglia di inserimento nel form del Master.

### Passo 4: Generare la Tabella nel Database
Finché non esegui questo passaggio, il modello è solo una "bozza".
1.  Clicca sul pulsante blu **"Generate/Update DB Table"**.
2.  Conferma l'operazione.
    *Nota: Se modifichi i campi in futuro, dovrai cliccare di nuovo su questo pulsante per aggiornare il database.*

### Passo 5: Usare la Nuova Applicazione
1.  Ricarica la pagina (F5) per aggiornare il menu laterale.
2.  Nel menu laterale, sotto la voce **APPLICAZIONI**, troverai il tuo nuovo modulo (es. `Gestione Flotta`).
3.  Cliccaci per iniziare a inserire dati, cercare ed esportare.

## 💡 Risoluzione Problemi

### Accesso Negato (Redirect al Login)
Se vedi un'applicazione nel menu ma cliccandoci vieni rimandato al login:
1.  Vai su **Builder (Admin)**.
2.  Cerca il modello in questione.
3.  Clicca **Manage Model** -> **Edit Model**.
4.  Assicurati che il tuo ruolo (`admin`) abbia le spunte su **Read** e **Write**.
5.  Salva e riprova.