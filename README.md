# FlaskERP - Un ERP Modulare Moderno

Questo progetto è un sistema ERP (Enterprise Resource Planning) costruito con un'architettura moderna, modulare e scalabile, utilizzando Python e Flask. È progettato per le esigenze delle aziende italiane, con un focus sulla manutenibilità, estensibilità e una user experience di alta qualità.

## Visione del Progetto

L'obiettivo è creare un'alternativa open-source, flessibile e potente ai tradizionali ERP monolitici, seguendo principi di sviluppo moderni:

- **Modularità Estrema**: Ogni funzione aziendale (Contabilità, Vendite, Magazzino) è un modulo a sé stante che può essere attivato o disattivato.
- **Disaccoppiamento**: I moduli comunicano tramite API interne ben definite, riducendo le dipendenze e facilitando lo sviluppo parallelo.
- **Dati Robusti e Scalabili**: Un modello dati relazionale solido, gestito da un ORM potente, che garantisce integrità e performance.
- **UI/UX Professionale**: Un'interfaccia web veloce, intuitiva e reattiva (Single Page Application).
- **Cloud-Native**: Progettato per essere deployato, scalato e gestito su piattaforme cloud.

---

## 📚 Stack Tecnologico

- **Backend**: Python 3.11+
- **Framework Backend**: Flask
- **ORM**: SQLAlchemy con Alembic per le migrazioni del database.
- **Database**: PostgreSQL
- **Package Management**: `uv` (un gestore di pacchetti e ambienti virtuali Python ad alte prestazioni).
- **Frontend**: React (o Vue.js) come Single Page Application (SPA).
- **Styling UI**: Ant Design / Bootstrap 5.
- **BI & Analytics**: Dash by Plotly, Pandas.
- **Deployment**: Docker, Kubernetes.

---

## 🏛️ Architettura

Proponiamo un'architettura "Modular Monolith" con una SPA frontend separata.

1.  **Backend (Flask)**:
    - **Blueprints**: Ogni modulo ERP (es. `sales`, `inventory`, `accounting`) è un Flask Blueprint. Questo permette una separazione logica del codice e delle rotte.
    - **API-Driven**: Il backend espone unicamente API REST/JSON. Non fa rendering di HTML.
    - **Comunicazione Inter-Modulo**: I moduli comunicano tramite API interne ben documentate (standard OpenAPI), garantendo disaccoppiamento.

2.  **Frontend (React/SPA)**:
    - La UI è un'applicazione JavaScript completamente separata che vive nel browser.
    - Comunica con il backend Flask esclusivamente tramite le API REST.
    - Questo garantisce un'esperienza utente fluida e veloce, senza ricaricare la pagina.

3.  **Database (PostgreSQL)**:
    - Un singolo database PostgreSQL funge da "source of truth".
    - SQLAlchemy mappa le tabelle a oggetti Python, semplificando le query e garantendo la coerenza.

### ⚙️ Il "Motore ERP": Sviluppo Rapido e DRY

Per gestire la complessità di un ERP con centinaia di tabelle, abbiamo sviluppato un **framework interno** che automatizza le operazioni CRUD (Create, Read, Update, Delete), permettendo agli sviluppatori di concentrarsi sulla logica di business complessa.

#### 1. Backend Automation (`app/crud.py`)
Invece di scrivere manualmente gli endpoint per ogni entità, utilizziamo una **Factory Function** `register_crud_routes`.

**Come aggiungere una nuova entità (es. Prodotti):**
1.  Definire il Modello (`models/product.py`).
2.  Definire lo Schema di Validazione (`schemas.py`).
3.  Registrare le rotte con una riga di codice:
    ```python
    register_crud_routes(blp, Product, ProductSchema, url_prefix="/products", search_fields=["name"], multipart=True)
    ```
Questo genera automaticamente API sicure (JWT), paginata, ricercabili e capaci di gestire upload di file.

#### 2. Frontend Automation (`GenericCrudPage.jsx`)
Il frontend utilizza un approccio **Metadata-Driven**. Non disegniamo form o tabelle a mano per le anagrafiche standard.

**Come creare la pagina di gestione:**
Configuriamo semplicemente le colonne e i campi:
```javascript
const columns = [
  { header: 'Nome', accessor: 'name' },
  { header: 'Prezzo', accessor: 'price' }
];
const formFields = [
  { name: 'name', label: 'Nome Prodotto', required: true },
  { name: 'image', label: 'Foto', type: 'file' }
];
// Il componente fa tutto il resto
<GenericCrudPage apiPath="/products" columns={columns} formFields={formFields} />
```

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
    - [x] Implementazione "Motore ERP" (`register_crud_routes`, `GenericCrudPage`) per sviluppo rapido.

3.  **Fase 2: Anagrafiche di Base (In Corso)**
    - [x] Modello `Party` (Clienti/Fornitori).
    - [ ] Modelli `Address`, `Product`.
    - [ ] API CRUD (Create, Read, Update, Delete) per queste anagrafiche.
    - [ ] UI per la gestione delle anagrafiche di base.

4.  **Fase 3: Primo Modulo Funzionale (Es. Vendite)**
    - [ ] Modello `SalesOrder` e `SalesOrderLine`.
    - [ ] Logica di business per la creazione e gestione di un ordine di vendita.
    - [ ] API per il ciclo di vita dell'ordine.
    - [ ] UI per la gestione degli ordini di vendita.

5.  **Fase 4: Moduli Successivi**
    - [ ] Sviluppo iterativo dei moduli Acquisti, Magazzino, Cespiti.

6.  **Fase 5: Contabilità e Reporting**
    - [ ] Modelli per Piano dei Conti (`ChartOfAccounts`), Registrazioni (`GlEntry`), IVA (`VatLedger`).
    - [ ] Logica per la generazione del Libro Giornale e liquidazione IVA.
    - [ ] Integrazione con gli altri moduli per la contabilizzazione automatica.

---

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
