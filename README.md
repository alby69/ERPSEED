# MakeERP - The ERP Engine

MakeERP è un motore "Low-Code" open-source progettato per costruire, eseguire e distribuire sistemi gestionali complessi. Non è solo un ERP, ma una piattaforma per creare il *tuo* ERP (es. Gestione Flotta, CRM, WMS) attraverso una definizione dinamica dei dati.

## Visione del Progetto

L'obiettivo è creare un'alternativa open-source, flessibile e potente ai tradizionali ERP monolitici, seguendo principi di sviluppo moderni:

- **Modularità Estrema**: Ogni funzione aziendale (Contabilità, Vendite, Magazzino) è un modulo a sé stante che può essere attivato o disattivato.
- **Disaccoppiamento**: I moduli comunicano tramite API interne ben definite, riducendo le dipendenze e facilitando lo sviluppo parallelo.
- **Engine vs Blueprint**: Il motore (MakeERP) è separato dalla logica di business (Blueprint). Puoi esportare il tuo progetto "Parco Auto" in un file JSON e distribuirlo ovunque.
- **Multi-Progetto**: Il motore è progettato per gestire più progetti indipendenti (es. un'istanza per ogni cliente), ognuno con i propri modelli e dati, garantendo l'isolamento.
- **UI/UX Professionale**: Un'interfaccia web veloce, intuitiva e reattiva (Single Page Application).
- **Cloud-Native**: Progettato per essere deployato, scalato e gestito su piattaforme cloud.

---
## Gestione Progetti e Multi-Tenancy

Il FlaskERP è costruito sopra un potente sistema di gestione di progetti che permette un completo isolamento dei dati e delle configurazioni, rendendolo una soluzione ideale per il multi-tenancy.

- **Progetti come Contenitori**: Ogni progetto (es. "Logistica", "CRM Cliente Alpha", "WMS per il Magazzino Centrale") agisce come un contenitore autonomo per i propri modelli di dati, configurazioni, membri e permessi.

- **Isolamento dei Dati tramite Schema**: Per garantire la sicurezza e l'isolamento dei dati, FlaskERP crea uno schema PostgreSQL dedicato per ogni progetto (es. `project_1`, `project_2`). Questo significa che i dati di un cliente non si mescoleranno mai con quelli di un altro, anche se condividono la stessa infrastruttura.

- **Gestione dei Membri**: Aggiungi utenti a progetti specifici con ruoli distinti (es. Amministratore, Editor, Visualizzatore). I permessi vengono applicati a livello di progetto, garantendo che gli utenti vedano e modifichino solo ciò che è loro consentito.

- **Template di Progetto (Import/Export)**:
  - **Esporta**: Esporta l'intera architettura di un progetto—inclusi tutti i suoi modelli, campi e configurazioni—in un file di template JSON. Questo è perfetto per fare il backup delle tue applicazioni o per condividere "soluzioni pronte all'uso" con altri.
  - **Importa**: Crea nuovi progetti da un template con un solo clic. Il sistema può creare un nuovo progetto o aggiornarne uno esistente (upsert), gestendo in modo intelligente le modifiche a modelli e campi. Questo accelera drasticamente i tempi di implementazione per nuovi clienti o ambienti.

## 🏛️ Architettura

Proponiamo un'architettura "Modular Monolith" con una SPA frontend separata.

1.  **Backend (Flask)**:
    - **Struttura Modulare**: Il codice risiede nella cartella `backend/`. Ogni dominio (es. `users`, `projects`, `sales`) è un modulo isolato con le sue rotte, modelli e schemi.
    - **API-Driven**: Il backend espone unicamente API REST/JSON. Non fa rendering di HTML.
    - **Comunicazione Inter-Modulo**: I moduli comunicano tramite API interne ben documentate (standard OpenAPI), garantendo disaccoppiamento.

2.  **Frontend (React/SPA)**:
    - La UI è un'applicazione JavaScript completamente separata che vive nel browser.
    - Comunica con il backend Flask esclusivamente tramite le API REST.
    - Questo garantisce un'esperienza utente fluida e veloce, senza ricaricare la pagina.

3.  **Database (PostgreSQL)**:
    - Un singolo database PostgreSQL funge da "source of truth".
    - SQLAlchemy mappa le tabelle a oggetti Python, semplificando le query e garantendo la coerenza.

### 🏗️ ERP Builder (No-Code Engine) - *Attivo*

Il cuore del progetto è il **Builder**, un sistema per estendere l'ERP direttamente dall'interfaccia web, senza scrivere codice.

#### 1. Gestione Modelli Dinamica
Il backend ora supporta la definizione di modelli tramite API, permettendo di creare dinamicamente:
- **Progetti**: Contenitori logici per raggruppare modelli e configurazioni (es. "Gestione Flotta", "CRM Cliente X").
- **Tabelle** (Entità) tramite il modello `SysModel`.
- **Campi** (`SysField`) con un'ampia gamma di tipi: `string`, `integer`, `boolean`, `date`, `select`, `file`, `image`, `calculated` (frontend).
- **Relazioni** (tramite il tipo `relation`), **Campi Calcolati Backend** (`formula`), **Campi di Riepilogo** (`summary`) e **Campi di Ricerca** (`lookup`).

#### 2. Dynamic Runtime
Il backend includerà un motore capace di:
- Salvare la definizione dei modelli in tabelle di sistema (`sys_models`, `sys_fields`) all'interno di un **Progetto**.
- Generare/Aggiornare lo schema del database PostgreSQL per ogni progetto in modo isolato (`CREATE SCHEMA project_x`).
- Esporre automaticamente API CRUD per i nuovi modelli, contestualizzate per progetto (es. `/projects/<id>/data/<model_name>`).

#### 3. Frontend Automation (`GenericCrudPage.jsx`)
Il frontend è predisposto con componenti **Metadata-Driven**:
- **`GenericCrudPage`**: Renderizza tabelle e form basandosi su una configurazione JSON.
- Il Builder collegherà i metadati del backend direttamente a questo componente, permettendo di visualizzare le nuove tabelle istantaneamente.

**Componenti Chiave:**
- **`GenericCrudPage`**: Gestisce stato, fetch dati, modali, form, validazione errori backend, upload file.
- **`DataTable`**: Rendering tabellare puro con supporto per azioni custom.
- **`SearchBar` / `Pagination`**: Componenti UI riutilizzabili.
- **`Layout`**: Wrapper per la struttura applicativa (Sidebar, Navbar).

---

## 🗂️ Modello Dati (ER) - Concetto Iniziale

Il modello dati è progettato per essere flessibile e scalabile.

- **`User`**: Gestisce l'identità digitale. Contiene email, password hash, stato (attivo/inattivo). È l'attore che *usa* il sistema.
- **`Role` / `Permission`**: Definiscono i ruoli (es. "Amministratore", "Magazziniere") e i permessi granulari ("può creare ordine di vendita", "può vedere giacenze").
- **`Party` / `Contact`**: Anagrafica generica per qualsiasi entità legale o persona. Un attributo `type` distingue tra `Cliente`, `Fornitore`, `Azienda Controllata`, `Persona Fisica`, etc.
- **`Address`**: Indirizzi riutilizzabili, collegati alle anagrafiche.
- **`Product`**: Anagrafica prodotti/servizi.
- **Tabelle Modulo-Specifiche**: `SalesOrder`, `PurchaseOrder`, `InventoryMovement`, `GlEntry` (registrazione contabile), etc.

Questo approccio evita ereditarietà complesse e permette a un'entità di avere più ruoli (es. un'azienda può essere sia cliente che fornitore).

---

## 🚀 Piano di Sviluppo a Fasi

1.  **Fase 0: Fondamenta e Setup (Completata)**
    - [x] Definizione dell'architettura e del piano di sviluppo.
    - [x] Creazione della struttura del progetto.
    - [x] Setup dell'ambiente virtuale (gestito via Docker).
    - [x] Installazione delle dipendenze iniziali (Flask, SQLAlchemy, etc.).
    - [x] Configurazione base dell'applicazione Flask e connessione al DB.
    - [x] Creazione del primo modello dati con SQLAlchemy e Alembic (`User`).

2.  **Fase 1: Gestione Utenti e Accessi (IAM) (Completata)**
    - [x] Modello `User`.
    - [x] Endpoint API per registrazione utenti.
    - [x] Endpoint API per login (con JWT).
    - [x] Endpoint protetto di prova (`/me`).
    - [x] Decoratori per proteggere gli endpoint in base ai ruoli/permessi.
    - [x] Creazione della UI di base (React SPA) per login e gestione utenti.
    - [x] Implementazione Frontend Generico (`GenericCrudPage`) per sviluppo rapido.

3.  **Fase 2: Anagrafiche di Base (Completata)**
    - [x] Modelli `Party` (Clienti/Fornitori) e `Product`.
    - [x] API CRUD (Create, Read, Update, Delete) con filtri e paginazione.
    - [x] UI per la gestione delle anagrafiche di base.

4.  **Fase 3: Primo Modulo Funzionale (Es. Vendite) (In Corso)**
    - [x] Modello `SalesOrder` e `SalesOrderLine`.
    - [x] API per la creazione e gestione ordini.
    - [ ] UI avanzata per la gestione degli ordini (es. Master-Detail).

5.  **Fase 4: Moduli Successivi**
    - [ ] Sviluppo iterativo dei moduli Acquisti, Magazzino, Cespiti.

6.  **Fase 5: Contabilità e Reporting**
    - [ ] Modelli per Piano dei Conti (`ChartOfAccounts`), Registrazioni (`GlEntry`), IVA (`VatLedger`).
    - [ ] Logica per la generazione del Libro Giornale e liquidazione IVA.
    - [ ] Integrazione con gli altri moduli per la contabilizzazione automatica.

7.  **Fase 6: ERP Builder (No-Code) (Completata)**
    - [x] Modelli di sistema (`SysModel`, `SysField`) per definire tabelle e campi.
    - [x] Motore di generazione e aggiornamento schema DB (`CREATE/ALTER TABLE`) per progetto.
    - [x] API Runtime Dinamica (`/projects/<id>/data/<model>`) completa (CRUD, relazioni, file, formule).
    - [x] UI di Amministrazione per il Builder (gestione modelli, campi, permessi ACL).
    - [x] Frontend Dinamico (`GenericCrudPage`) per l'utilizzo delle applicazioni create.
    - [x] Funzionalità Avanzate: Validazione Regex, Campi Calcolati Frontend, Widget Dashboard.
    - [x] **Gestione Progetti e Multi-Tenancy**:
        - [x] Aggiunta del modello `Project` per raggruppare le configurazioni.
        - [x] Gestione membri per progetto (Owner/Admin).
        - [x] Isolamento dei dati per progetto (schema-based multi-tenancy).
        - [x] API per creare, leggere, aggiornare ed eliminare Progetti.
        - [x] Funzionalità di Import/Export di un intero Progetto come template JSON.
        - [x] Gestione Versionamento Progetti e Backup automatici.
        
---

## 🔧 Debugging e Troubleshooting

Se riscontri problemi con le API o il Frontend, segui questa guida per isolare il problema.

### 1. Problemi di Routing (404 Not Found)
- **API Statiche**: Controlla `app/crud.py`. Le rotte sono generate automaticamente. Verifica che il modello sia registrato nel blueprint.
- **API Dinamiche**: Controlla `backend/dynamic_api.py`. Queste rotte rispondono a `/projects/<project_id>/data/<model_name>`.
  - Verifica che il `model_name` esista nella tabella `sys_models` e sia associato al `project_id` corretto.
  - Verifica che la tabella fisica esista nel DB (usa `Generate Table` dalla UI).

### 2. Problemi di Database (SQLAlchemy)
- Se modifichi un modello Python (`app/models/`), devi generare una migrazione:
  ```bash
  flask db migrate -m "descrizione"
  flask db upgrade
  ```
- Se modifichi un modello Dinamico (dal Builder), devi cliccare su **"Generate/Update DB Table"** nella pagina di dettaglio del modello.

### 3. Frontend (React)
- **Schermata Bianca / Crash**: Spesso dovuto a import ciclici o doppi export (es. `SysModelDetail`). Controlla la console del browser (F12).
- **Campi non visibili**: Verifica che i metadati (`sys_fields`) siano allineati con la risposta API `/data/<model>/meta`.

### 4. Reset Completo del Database (Ambiente Docker)

Se il database si corrompe, lo schema non è più sincronizzato o semplicemente vuoi ripartire da zero, puoi usare lo script di reset. **Attenzione: questa operazione cancellerà tutti i dati.**

1.  **Assicurati che i container siano attivi**:
    ```bash
    docker compose up -d
    ```

2.  **Esegui lo script di reset dentro il container `web`**:
    ```bash
    docker compose exec web python -m backend.reset_db
    ```
    Questo comando eseguirà lo script `reset_db.py` che si occupa di cancellare il database, ricreare tutte le tabelle secondo i modelli SQLAlchemy e inserire i dati di seed (amministratore, KPI, etc.).

3.  **Riavvia il servizio web per applicare le modifiche**:
    ```bash
    docker compose restart web
    ```

### 🏗️ Architettura del Codice (Refactoring in corso)

Stiamo migrando verso un'architettura più pulita (KISS/DRY):
- **`app/crud.py`**: Gestisce i modelli "Hard-coded" (User, Party).
- **`backend/dynamic_api.py`**: Gestisce i modelli "No-Code". *Nota: In futuro queste due logiche verranno unificate in un unico `QueryBuilder`.*

---

## 📖 Manuale Utente del Builder

Il **Builder** è il cuore "Low-Code" di FlaskERP. Permette agli amministratori di creare, modificare ed estendere le funzionalità dell'applicazione direttamente dall'interfaccia web.

Per una guida dettagliata su come creare progetti, modelli, campi e utilizzare le funzionalità avanzate, consulta il **Manuale del Builder**.

## ✨ Funzionalità Avanzate del Builder

Oltre alla creazione base di tabelle e campi, il Builder supporta funzionalità avanzate per creare logiche complesse senza codice.

### 1. Campi Calcolati e di Riepilogo
-   **Formula (Backend)**: Esegue calcoli matematici lato server usando i valori di altri campi. Esempio: `{quantity} * {price}`.
-   **Calculated (Frontend)**: Esegue calcoli lato client (JavaScript) per logiche di visualizzazione immediate. Esempio: `{firstName} + ' ' + {lastName}`.
-   **Summary (Riepilogo)**: Aggrega dati da una tabella "figlia" (relazione 1-a-N). Utile per calcolare totali, medie, o conteggi. Esempio: `SUM(total)` dalle righe di una fattura.
-   **Lookup**: Recupera e visualizza un valore da una tabella correlata, evitando join complesse nel frontend.

### 2. Logica Condizionale
-   **Visibilità Condizionale**: Mostra o nascondi un campo nel form in base al valore di un altro campo. Esempio: mostra il campo "Motivazione" solo se lo stato è "Rifiutato".
-   **Requisito Condizionale**: Rendi un campo obbligatorio solo se un altro campo ha un determinato valore.

### 3. Viste Personalizzate (Kanban)
Il Builder permette di definire viste alternative ai dati oltre alla classica tabella.
-   **Vista Kanban**: Visualizza i record come card in colonne che rappresentano uno stato (es. To Do, In Progress, Done).
-   **Configurazione**:
    1.  Nel modello, definisci un campo di tipo `Select` per lo stato (es. "status_pedido").
    2.  Nelle impostazioni del modello, imposta la **Vista di Default** su `kanban`.
    3.  Seleziona il campo di stato nel nuovo menu a tendina **Campo Stato Kanban**.
-   Il sistema genererà automaticamente una board interattiva con drag-and-drop per cambiare lo stato dei record.

### 4. Gestione dei Modelli
- **Clonazione**: Clona un modello esistente con un solo clic, duplicando tutti i suoi campi e configurazioni. Utile per creare rapidamente nuove varianti di modelli complessi.
- **Sincronizzazione dello Schema**: Applica in modo sicuro le modifiche alla definizione del modello (aggiunta di campi, modifica di tipi) alla tabella del database sottostante (`ALTER TABLE`), preservando i dati esistenti.

### 5. Sicurezza e Manutenzione Dati
- **Reset Tabella**: Funzionalità per ricreare lo schema fisico della tabella (DROP/CREATE) in caso di disallineamento critico.
- **Backup Automatico**: Prima di ogni operazione distruttiva (Reset), il sistema crea automaticamente un backup CSV dei dati.
- **Download Backup**: Gli amministratori possono visualizzare la lista dei backup e scaricarli direttamente dall'interfaccia.
- **Audit Log**: Tutte le azioni significative del builder (creazione, modifica, cancellazione di modelli/campi) sono registrate in un log di audit, fornendo una traccia completa delle modifiche.

## ⚙️ Setup dell'Ambiente di Sviluppo

Il progetto è configurato per funzionare con **Docker**, che gestisce sia l'applicazione che il database.

**Prerequisiti**:
- Docker Desktop (o Docker Engine + Compose) installato.
- (Consigliato) Estensione **Container Tools** (ex Docker) per VS Code per gestire i container visivamente.

**Passaggi**:

1.  **Clonare il repository (se esiste)**
    ```bash
    cd flaskERP
    ```

2.  **Avviare l'ambiente con Docker Compose**
    ```bash
    docker compose up --build
    ```
    Questo scaricherà le immagini, costruirà il container dell'app e avvierà PostgreSQL.

3.  **Eseguire le migrazioni del database (in un altro terminale)**
    Poiché il DB è nuovo e vive dentro Docker, dobbiamo lanciare le migrazioni *dentro* il container `web`:
    ```bash
    docker compose exec web flask db upgrade
    ```

4.  **Accedere all'applicazione**
    - API/Swagger: http://localhost:5000/swagger-ui
    - Il codice locale è montato nel container: ogni modifica ai file `.py` riavvierà automaticamente il server.
---

## 📊 BI e Data Analysis

Per l'analisi dei dati, integreremo un modulo di BI basato su **Dash by Plotly**.

- **Vantaggi**:
  - **Puro Python**: Le dashboard si scrivono interamente in Python.
  - **Integrazione Perfetta**: Può essere eseguito come parte dell'applicazione Flask, accedendo direttamente ai modelli SQLAlchemy.
  - **Interattività**: Crea grafici e tabelle interattive, drill-down, filtri dinamici.
- **Alternative**: Sebbene si possano esportare dati per Power BI, la soluzione integrata riduce la complessità e mantiene tutti i dati all'interno dell'ecosistema applicativo, migliorando sicurezza e real-time analytics.

---

## ☁️ Strategia Cloud e Deployment

L'architettura è pensata per il cloud.

- **Containerizzazione**: L'applicazione Flask e la SPA React verranno containerizzate con **Docker**.
- **Orchestrazione**: Si consiglia l'uso di **Kubernetes** per gestire i container in produzione, garantendo scalabilità, auto-riparazione e rolling updates.
- **PaaS**: Piattaforme come Heroku, Google App Engine, o AWS Elastic Beanstalk possono essere alternative più semplici per un avvio rapido.
- **Database Gestito**: Utilizzare servizi come Amazon RDS, Google Cloud SQL o Azure Database for PostgreSQL per gestire il database in modo affidabile.