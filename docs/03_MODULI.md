# Moduli ERP

## Panoramica dei Moduli

FlaskERP include moduli predefiniti che coprono le funzionalità essenziali di un sistema gestionale. Ogni modulo può essere attivato o disattivato in base alle esigenze, permettendo di avere un sistema snello e focalizzato.

I moduli sono organizzati in categorie:

- **Core**: Funzionalità fondamentali sempre presenti
- **Builtin**: Moduli base inclusi nell'installazione
- **Premium**: Moduli avanzati disponibili nel Marketplace

---

## Moduli Core

Questi moduli sono sempre disponibili e gestiscono le funzionalità fondamentali del sistema.

### Autenticazione e Utenti

Gestisce l'accesso degli utenti al sistema, le sessioni e i permessi base. Ogni utente appartiene a un progetto e ha un ruolo definito.

**Funzionalità principali:**
- Registrazione e login
- Gestione password
- Sessioni JWT
- Ruoli base: Admin, Editor, Viewer

### Progetti

Il modulo che permette di creare ambienti isolati. Ogni progetto ha i propri dati, utenti, moduli attivi e configurazioni.

**Funzionalità principali:**
- Creazione progetti multipli
- Isolamento dati per progetto
- Template di progetto
- Import/Export configurazioni

---

## Moduli Builtin

### Anagrafica (Parties)

L'anagrafica è il cuore informativo del sistema. Gestisce le entità con cui l'azienda interagisce.

**Soggetti**: Persone fisiche e giuridiche. Un soggetto può essere contemporaneamente Cliente, Fornitore, Dipendente, a seconda dei Ruoli associati.

**Ruoli**: Definiscono la relazione tra l'azienda e il Soggetto. I ruoli base sono Cliente, Fornitore, Prospect, Partner.

**Indirizzi**: Localizzazioni geografiche associate ai Soggetti. Ogni Soggetto può avere più indirizzi (sede legale, operativa, magazzino).

**Contatti**: Canali di comunicazione (email, telefono, fax) associati ai Soggetti.

**Perché è importante**: L'anagrafica unificata evita duplicazioni e garantisce che ogni informazione di contatto sia sempre aggiornata. Se cambio indirizzo a un Fornitore, questa informazione è disponibile per tutti i moduli che la usano.

### Prodotti

Gestisce il catalogo prodotti e servizi dell'azienda.

**Funzionalità:**
- Scheda prodotto con anagrafica completa
- Codici multipli (SKU, barcode, codice fornitore)
- Categorie e sottocategorie
- Listini prezzi
- Varianti (taglia, colore, ecc.)

**Integrazioni**: Il modulo Prodotti si integra con Magazzino per la gestione delle giacenze e con Vendite/Acquisti per ordini e fatture.

### Vendite

Gestisce l'intero ciclo di vendita, dalla preventivazione alla fatturazione.

**Funzionalità:**
- Preventivi e configurazioni
- Ordini cliente
- Note di credito
- Statistiche vendite
- Dashboard commerciale

**Flusso tipico**: Preventivo → Ordine → Consegna/DDT → Fattura

### Acquisti

Gestisce il ciclo di approvvigionamento.

**Funzionalità:**
- Richieste di acquisto
- Ordini fornitore
- Ricevimenti merce
- Comparazione fornitori

### Magazzino

Gestisce inventari e movimentazioni.

**Funzionalità:**
- Giacenze per ubicazione
- Movimenti di carico e scarico
- Inventario
- Attrezzature (con scadenze e manutenzioni)
- Tracking lotti e seriali

---

## Moduli in Sviluppo

### Contabilità

Il modulo contabile è in fase di sviluppo avanzato. Coprirà:

- Piano dei conti
- Prima nota (registrazione movimenti)
- Partitario clienti/fornitori
- Bilancio
- Fatturazione elettronica (integrazione SDI italiana)

**Stato attuale**: 70% completato

### Risorse Umane (HR)

Gestione del personale dipendente.

**Funzionalità implementate:**
- Anagrafica dipendenti
- Dipartimenti/Unità organizzative
- Presenze e festività
- Richieste ferie

**In sviluppo:**
- Calcolo stipendi
- Contratti e gestione giuridica
- Dashboard HR

**Stato attuale**: 50% completato

---

## Attivare e Configurare i Moduli

### Attivazione

Per attivare un modulo:

1. Accedi come amministratore
2. Vai su **Amministrazione → Moduli**
3. Trova il modulo che ti serve
4. Clicca **Attiva**

Il sistema installa automaticamente eventuali dipendenze e crea le tabelle necessarie.

### Configurazione

Ogni modulo ha impostazioni specifiche accessibili dalla scheda del modulo:

- Parametri generali
- Numerazioni documenti
- Workflow di approvazione
- Integrazioni con altri moduli

### Disattivazione

Puoi disattivare moduli che non usi. Attenzione: la disattivazione非 nasconde solo il menu. I dati rimangono nel database.

---

## Integrazione tra Moduli

I moduli di FlaskERP comunicano automaticamente tra loro attraverso l'EventBus.

**Esempio - Ciclo di vendita completo:**

1. Un commerciale crea un **Ordine** (modulo Vendite)
2. Il sistema verifica la disponibilità in **Magazzino**
3. Se confermato, genera il documento di trasporto
4. Successivamente, la **Contabilità** registra la fattura

Tutte queste operazioni avvengono automaticamente una volta configurate, senza intervento manuale.

---

## Creare Moduli Custom

Oltre ai moduli builtin, puoi creare moduli entirely custom usando il Builder. Un modulo custom può:

- Avere entità proprietarie
- Integrarsi con moduli esistenti
- Avere workflow specifici
- Esporre API dedicate

I moduli custom che crei possono essere condivisi nel Marketplace per la comunità.

---

## Roadmap dei Moduli

Prossimi moduli in sviluppo:

| Modulo | Descrizione | Previsto |
|--------|-------------|----------|
| Produzione | Distinte basi, cicli, commesse | Q2 2026 |
| CRM | Pipeline commerciali, campagne | Q2 2026 |
| Progetti | Gestione progetti e task | Q3 2026 |
| Documentale | Archiviazione documenti | Q3 2026 |
| Helpdesk | Ticket e assistenza | Q4 2026 |

---

*Documento aggiornato: Febbraio 2026*
