# FlaskERP - Guida al Progetto

## Cos'è FlaskERP?

FlaskERP è un sistema ERP (Enterprise Resource Planning) moderno, flessibile e modulare pensato per le piccole e medie imprese. È scritto in Python (backend) e React (frontend), completamente open-source.

**ERP** significa che aiuta le aziende a gestire tutte le principali funzioni aziendali in un unico sistema integrato: vendite, acquisti, magazzino, contabilità, HR e molto altro.

---

## Architettura del Sistema

### Il Backend (Python/Flask)

Il backend è il "motore" dell'applicazione. Gestisce:
- **Database**: Dove vengono salvati tutti i dati
- **API**: Le interfacce che permettono al frontend di comunicare con il database
- **Logica di business**: Le regole che governano il funzionamento dell'azienda

Il backend è costruito con **Flask**, un framework leggero ma potente per creare applicazioni web in Python.

### Il Frontend (React)

Il frontend è ciò che vedi quando apri l'applicazione nel browser. È costruito con **React**, una libreria moderna per creare interfacce utente interattive e veloci.

### Il Database (PostgreSQL)

PostgreSQL è un database relazionale professioniale che garantisce:
- Affidabilità dei dati
- Sicurezza
- Ottime performance anche con grandi quantità di informazioni

---

## Moduli Principali

FlaskERP è organizzato in **moduli** che possono essere attivati o disattivati secondo le esigenze dell'azienda.

### 1. Anagrafiche (Parties)
Gestione di clienti, fornitori e contatti. Ogni anagrafica può essere classificata come:
- Cliente
- Fornitore
- Both (sia cliente che fornitore)

### 2. Prodotti (Products)
Catalogo prodotti e servizi con:
- Categorie gerarchiche
- Varianti (taglia, colore, ecc.)
- Listini prezzi multipli

### 3. Vendite (Sales)
Gestione ordini cliente con:
- Creazione e gestione ordini
- Stati: Bozza → Confermato → Spedito → Fatturato
- Calcoli automatici di totali e imposte
- Generazione PDF dell'ordine

### 4. Acquisti (Purchases)
Gestione ordini fornitore con:
- Creazione ordini di acquisto
- Ricezione merce
- Stati: Bozza → Confermato → Ricevuto

### 5. Magazzino (Inventory)
Gestione inventario con:
- Ubicazioni multiple
- Movimenti di stock (carico/scarico)
- Inventario periodico
- Giacenze in tempo reale

### 6. Contabilità (Accounting)
Contabilità generale con:
- Piano dei Conti
- Partita doppia (registrazioni)
- Fatture attive e passive
- Bilancio di verifica
- Report contabili

### 7. Risorse Umane (HR)
Gestione dipendenti:
- Anagrafica dipendenti
- Reparti
- Presenze
- Richieste permessi/ferie

### 8. Builder (No-Code)
Il cuore innovativo di FlaskERP: permette di creare nuove applicazioni senza scrivere codice!

- Creare modelli dati personalizzati
- Definire campi con diversi tipi (testo, numero, data, select, ecc.)
- Configurare relazioni tra tabelle
- Creare dashboard e report
- Gestire permessi utente

---

## Multi-Tenant: Cos'è e Perché è Importante

FlaskERP supporta il **multi-tenant**, cioè la possibilità di gestire più aziende (tenant) separate all'interno della stessa installazione.

**Vantaggi:**
- Un'unica infrastruttura per più clienti
- Dati completamente isolati tra i tenant
- Manutenzione semplificata
- Costi ridotti

Ogni tenant ha:
- I propri dati separati
- I propri utenti
- I propri moduli attivi
- Possibilità di scegliere il piano di servizio

---

## Piani di Servizio

FlaskERP offre diversi piani:

### Starter (Gratuito)
Include:
- Anagrafiche
- Prodotti
- Vendite
- Acquisti
- Contabilità base
- Magazzino

### Professional
Tutto di Starter più:
- Risorse Umane
- Progetti
- CRM
- Helpdesk
- Documenti

### Enterprise
Tutto di Professional più:
- Produzione (Manufacturing)
- Tutti i moduli premium

---

## Gestione Moduli

Gli amministratori possono:
- Visualizzare tutti i moduli disponibili
- Attivare/disattivare moduli per il proprio tenant
- Vedere quali moduli sono già attivi
- Controllare lo stato (attivo/non attivo) di ogni modulo

La gestione avviene dalla pagina **Modules** nell'area amministrativa.

---

## Sicurezza

FlaskERP implementa diverse misure di sicurezza:

1. **Autenticazione JWT**: Token sicuri per l'accesso
2. **Isolamento multi-tenant**: I dati di un'azienda non sono accessibili da altre
3. **Ruoli e permessi**: Utenti con ruoli diversi (admin, utente normale)
4. **Audit Log**: Tracciamento di tutte le operazioni importanti

---

## Tecnologie Utilizzate

### Backend
- **Python 3.12**: Linguaggio di programmazione
- **Flask**: Framework web
- **SQLAlchemy**: ORM per database
- **PostgreSQL**: Database
- **Flask-JWT-Extended**: Autenticazione
- **Flask-Smorest**: API REST
- **xhtml2pdf**: Generazione PDF

### Frontend
- **React 19**: UI framework
- **Ant Design**: Componenti UI
- **React Router**: Navigazione
- **Axios/Fetch**: Comunicazione API

### Infrastruttura
- **Docker**: Containerizzazione
- **PostgreSQL**: Database
- **Redis**: Cache (opzionale)

---

## Come Iniziare

### Requisiti
- Docker Desktop installato
- Browser moderno

### Avvio Rapido
```bash
# Clona il repository
cd flaskERP

# Avvia i container
docker compose up --build

# Accedi all'applicazione
# Frontend: http://localhost:5173
# Backend API: http://localhost:5002
```

### Credenziali Default
- Email: admin@example.com
- Password: admin123

---

## Sviluppo Futuro

Alcune delle funzionalità previste:
- Integrazione SDI per fattura elettronica (Italia)
- Report avanzati e grafici
- Export CSV/Excel
- Modulo Produzione completo
- Sistema di notifiche
- Integrazioni con servizi esterni (Stripe, payment gateway)
- App mobile

---

## Licenza

FlaskERP è distribuito con licenza open-source. Consulta il repository per i dettagli.

---

*Ultimo aggiornamento: Febbraio 2026*
