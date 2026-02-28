# Marketplace

## Cos'è il Marketplace

Il Marketplace è lo spazio dove puoi condividere e installare **Block** e **Module** creati dalla comunità.

Può essere configurato per girare:
- **Integrato**: Come parte di FlaskERP
- **Separato**: Come server autonomo (futuro)

---

## Block vs Module

È importante capire la differenza:

| Elemento | Cosa include | Uso |
|----------|-------------|-----|
| **Block** | Solo interfaccia UI (Component + relazioni) | Widget, dashboard, viste |
| **Module** | Dati + UI + Logica (SysModel + Block + Hook + API) | Funzionalità complete |

### Quando pubblicare un Block

- Un widget UI specifico (es: "Card Cliente con statistiche")
- Una dashboard completa
- Una vista kanban preconfigurata
- Un componente riutilizzabile

### Quando pubblicare un Module

- Una funzionalità completa (es: "Gestione Preventivi")
- Un modulo con entità dati proprie
- Qualcosa con logica di business (Hook)
- API esposte

---

## Navigare il Marketplace

### Browse

1. Accedi al Marketplace dal menu
2. Esplora le categorie:
   - Anagrafica
   - Vendite
   - Acquisti
   - Magazzino
   - Contabilità
   - Produzione
   - UI Components
   - Altro
3. Usa filtri:
   - Categoria
   - Prezzo (gratis/pagamento)
   - Rating
   - Autore
4. Leggi schede con screenshot, descrizione, recensioni

### Installare

1. Trova ciò che ti serve
2. Leggi descrizione e recensioni
3. Se a pagamento, effettua pagamento
4. Clicca **Installa**
5. Il Block/Module viene aggiunto al progetto

Dopo installazione trovi il nuovo contenuto nel menu.

---

## Pubblicare

### Prerequisiti

Per pubblicare devi avere:
- Account verificato
- Block o Module completo nel tuo progetto
- Documentazione
- Test passati (minimo 80% quality score)

### Processo

1. **Prepara**
   - Assicurati che sia funzionante
   - Scrivi descrizione chiara
   - Prepara screenshot

2. **Testa**
   - Usa Test Runner
   - Ottieni quality score ≥ 80%

3. **Invia per Revisione**
   - Clicca **Pubblica**
   - Compila informazioni (nome, descrizione, prezzo)
   - Scegli tipo: Block o Module

4. **Revisione**
   - Il team verifica
   - Potrebbero richiedere modifiche
   - Una volta approvato, disponibile

### Certificazione

Blocchi con quality score ≥ 80% possono essere **certificati** con badge di qualità.

---

## Gestione Contenuti Pubblicati

### Dashboard Autore

In "I Tuoi Contenuti" trovi:
- Contenuti pubblicati
- Download e statistiche
- Recensioni
- Guadagni

### Aggiornare

1. Apri nel tuo progetto
2. Fai modifiche
3. Esegui test
4. Pubblica nuova versione

Gli utenti ricevono notifica.

---

## Sistema di Pagamenti

### Prezzi

Puoi impostare qualsiasi prezzo, anche zero.

### Guadagni

- Ricevi 70% del prezzo
- 30% sostiene FlaskERP
- Pagamenti tramite Stripe/PayPal

### Acquisti

- Garanzia rimborso 30 giorni
- Transazioni sicure
- Ricevuta per ogni acquisto

---

## Recensioni

### Lasciare una Recensione

1. Scheda contenuto
2. **Lascia Recensione**
3. Assegna rating (1-5 stelle)
4. Scrivi commento

### Rispondere

Autori possono rispondere per:
- Chiarire dubbi
- Ringraziare
- Indicare soluzioni

---

## Best Practices

### Per Utenti

- Leggi recensioni prima di installare
- Verifica compatibilità versione
- Testa in ambiente di test

### Per Autori

- Documenta bene
- Rispondi alle domande
- Aggiorna regolarmente
- Ascolta feedback

---

## Architettura Futura

Il Marketplace può essere separato:

```
┌─────────────────┐     ┌─────────────────┐
│  FlaskERP      │────►│  Marketplace    │
│  (Progetto)    │     │  (Server)       │
└─────────────────┘     └─────────────────┘
       │                        │
       │    Installazione       │
       └────────────────────────┘
```

Questo permette:
- Marketplace condiviso tra più installazioni FlaskERP
- Gestione indipendente
- Scalabilità

---

*Documento aggiornato: Febbraio 2026*
