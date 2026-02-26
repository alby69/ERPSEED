# Roadmap - Stato dello Sviluppo

## Stato Attuale

FlaskERP è un progetto in continua evoluzione. Questa pagina documenta lo stato attuale delle funzionalità e la roadmap per gli sviluppi futuri.

---

## Funzionalità Completate

### Core System ✅

| Componente | Stato | Note |
|-----------|-------|------|
| Autenticazione JWT | ✅ Completo | Login, logout, refresh token |
| Multi-Progetto | ✅ Completo | Isolamento dati completo |
| Gestione Utenti | ✅ Completo | Ruoli, permessi |
| Modulo Sistema | ✅ Completo | Plugin, eventi |

### Builder ✅

| Componente | Stato | Note |
|-----------|-------|------|
| Creazione Modelli | ✅ Completo | CRUD completo |
| Tipi Campo Base | ✅ Completo | String, number, date, etc |
| Tipi Campo Avanzati | ✅ Completo | Relation, calculated, summary |
| Viste Kanban | ✅ Completo | Drag & drop |
| Relazioni | ✅ Completo | 1:N, N:N |
| Validazioni | ✅ Completo | Required, unique, regex |

### Marketplace ✅

| Componente | Stato | Note |
|-----------|-------|------|
| Pubblicazione Blocchi | ✅ Completo | Con workflow approvazione |
| Installazione | ✅ Completo | Con un click |
| Certificazione | ✅ Completo | Quality score >= 80% |
| Recensioni | ✅ Completo | Rating e commenti |

### Testing ✅

| Componente | Stato | Note |
|-----------|-------|------|
| Test Runner UI | ✅ Completo | Interfaccia web |
| Generazione Auto | ✅ Completo | Suite CRUD |
| Esecuzione Test | ✅ Completo | Con risultati |
| Quality Score | ✅ Completo | Calcolo automatico |

---

## In Sviluppo

### Contabilità 🟡

**Stato**: 70% completo

- [x] Piano dei conti
- [x] Prima nota
- [x] Partitario
- [ ] Bilancio
- [ ] Fatturazione elettronica (SDI)

### Risorse Umane 🟡

**Stato**: 50% completo

- [x] Anagrafica dipendenti
- [x] Dipartimenti
- [x] Presenze
- [x] Richieste ferie
- [ ] Calcolo stipendi
- [ ] Contratti

### AI Assistant 🟡

**Stato**: 80% completo

- [x] Architettura base
- [x] Integrazione LLM (OpenRouter)
- [x] Generazione modelli da linguaggio naturale
- [x] Interfaccia chat frontend
- [x] Preview JSON modificabile
- [ ] Applicazione configurazione al database

---

## Roadmap 2026

### Q1 2026 ✅ (Completato)

- [x] Sistema Builder avanzato
- [x] Marketplace con certificazione
- [x] Test Runner integrato
- [x] Refactoring documentazione

### Q2 2026

- [ ] Completamento Contabilità
  - Bilancio
  - Chiusure esercizio
  - Integrazione SDI (Italiane)

- [ ] AI Assistant v1
  - Integrazione Gemini/Claude
  - Generazione modelli da linguaggio naturale
  - Suggerimenti automatici

- [ ] CRM Module
  - Pipeline commerciali
  - Campagne
  - Lead scoring

- [ ] Produzione Module
  - Distinte basi
  - Cicli di lavorazione

### Q3 2026

- [ ] Progetti e Task
  - Gantt integrato
  - Allocazione risorse
  - Timeline

- [ ] Documentale
  - Archiviazione
  - Versioning
  - Ricerca

- [ ] Integrazioni avanzate
  - E-commerce connectors
  - Marketplace sync

### Q4 2026

- [ ] Helpdesk
  - Ticket
  - Knowledge base
  - SLA

- [ ] Multi-company
  - Consolidamento
  - Reporting cross-company

- [ ] Reporting avanzato
  - Designer grafico
  - Dashboard custom

---

## Come Contribuire

Se vuoi contribuire allo sviluppo:

1. **Segnala bug**: Apri un issue su GitHub
2. **Proponi funzionalità**: Discuti nel forum
3. **Contribuisci codice**: Pull request benvenuti
4. **Supporta**: Star il progetto, diffondi

---

## TODO - Prossima Sessione

### AI Assistant - Completamento

1. **Collegare pulsante "Applica al Progetto"** al backend
   - Creare endpoint API per salvare il modello generato nel database
   - Integrare con il sistema di creazione modelli esistente

2. **Ripristinare autenticazione JWT** sull'endpoint `/api/ai/generate`
   - Attualmente disabilitato per testing

3. **Testare flow completo**: generazione → edit JSON → applica → modello creato

---

## Note sulla Versione

FlaskERP usa versioning semantico:

- **Major**: Cambiamenti non retrocompatibili
- **Minor**: Nuove funzionalità retrocompatibili
- **Patch**: Bug fix

La versione attuale è **0.x** - in questa fase le API possono cambiare.

---

## Prossimi Obiettivi Strategici

### Short-term (3-6 mesi)

1. Stabilizzare il core
2. Completare Contabilità
3. Lannciare AI Assistant
4. Far crescere il Marketplace

### Medium-term (6-12 mesi)

1. Raggiungere parità con ERP commerciali per PMI
2. Creare community attiva
3. Supporto enterprise (SLA)

### Long-term (1-2 anni)

1. Leader nel mercato ERP open-source
2. Marketplace fiorente
3. Integrazioni AI avanzate

---

*Ultimo aggiornamento: Febbraio 2026*
