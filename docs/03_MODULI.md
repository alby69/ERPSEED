# Moduli ERP

## Cos'è un Modulo

Un **Modulo** in FlaskERP è l'unità funzionale completa che combina:

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

### Pubblicare un Modulo

Per pubblicare nel Marketplace:
1. Porta il modulo in stato "testing"
2. Esegui i test (quality score ≥ 80%)
3. Clicca **Pubblica**
4. Compila le informazioni (nome, descrizione, prezzo)

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
