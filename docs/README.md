# Documentazione FlaskERP

Benvenuto nella documentazione di FlaskERP. Qui trovi tutto quello che ti serve per capire, configurare e usare il sistema.

## Struttura dei Manuali Operativi

| File | Titolo | Descrizione |
|------|--------|-------------|
| [01_ARCHITETTURA.md](01_ARCHITETTURA.md) | Architettura | Concetti base, SysModel, Block, Module |
| [02_BUILDER.md](02_BUILDER.md) | Builder | Creare entità, campi, Block |
| [03_MODULI.md](03_MODULI.md) | Moduli | Module = SysModel + Block + Hook + API |
| [04_AMMINISTRAZIONE.md](04_AMMINISTRAZIONE.md) | Amministrazione | Progetti, utenti, permessi, backup |
| [05_MARKETPLACE.md](05_MARKETPLACE.md) | Marketplace | Pubblicare Block e Module |
| [06_AUTOMAZIONE.md](06_AUTOMAZIONE.md) | Automazione | Hook, Eventi, Workflow |
| [07_INTEGRAZIONI.md](07_INTEGRAZIONI.md) | Integrazioni | API, Webhooks, ModuleRegistry |
| [08_TESTING.md](08_TESTING.md) | Testing | Test Runner, qualità |
| [09_DEPLOYMENT.md](09_DEPLOYMENT.md) | Deployment | Docker, produzione |
| [10_AI_ASSISTANT.md](10_AI_ASSISTANT.md) | AI Assistant | Guida all'agente AI |
| [11_TODO.md](11_TODO.md) | Roadmap Breve | Stato e prossime attività |
| [12_ROADMAP.md](12_ROADMAP.md) | Roadmap Completa | Implementazioni per componente |
| [13_ARCHITETTURA_DISTRIBUITA.md](13_ARCHITETTURA_DISTRIBUITA.md) | Futuro Distribuito | Analisi P2P e DAO |

## 📚 Biblioteca del Progetto (Planner)

Documenti strategici e manuali approfonditi per stakeholder e sviluppatori.

| File | Titolo | Descrizione |
|------|--------|-------------|
| [01_PROGETTO_ISTITUZIONALE.md](planner/01_PROGETTO_ISTITUZIONALE.md) | Biglietto da Visita | Visione, Missione e Impatto Sociale |
| [02_PITCH_INVESTITORI.md](planner/02_PITCH_INVESTITORI.md) | Pitch & Business | Business model, scalabilità e investimenti |
| [03_MANUALE_UTENTE_DISCORSIVO.md](planner/03_MANUALE_UTENTE_DISCORSIVO.md) | Manuale Utente | Guida ai processi aziendali (non tecnica) |
| [04_MANUALE_TECNICO_SVILUPPATORE.md](planner/04_MANUALE_TECNICO_SVILUPPATORE.md) | Manuale Tecnico | Guida per sviluppatori con esempi di codice |
| [05_ECOSISTEMA_ERPSEED.md](planner/05_ECOSISTEMA_ERPSEED.md) | ERPSeed Ecosystem | Nodi locali, governance e impatto sociale |

## Ordine di Lettura Consigliato

### Per nuovi utenti

1. **01_ARCHITETTURA** - Capire come funziona FlaskERP
2. **02_BUILDER** - Creare le prime entità
3. **04_AMMINISTRAZIONE** - Gestire utenti e progetti

### Per amministratori

1. **04_AMMINISTRAZIONE** - Configurazione sistema
2. **03_MODULI** - Moduli disponibili

### Per sviluppatori

1. **01_ARCHITETTURA** - Architettura
2. **02_BUILDER** - Creare entità custom
3. **06_AUTOMAZIONE** - Hook, Eventi, Workflow

### Per chi vuole l'AI

1. **10_AI_ASSISTANT** - Guida all'AI
2. **02_BUILDER** - Come l'AI genera configurazioni

## Concetti Chiave

```
SysModel → Block → Module
   │          │         │
   v          v         v
  Dati    Interfaccia  Funzionalità
                  (Hook + API)
```

## Nuova Architettura (2026)

FlaskERP ha completato un refactoring architetturale con:

- **Ports & Adapters**: Per astrazione provider LLM
- **CQRS**: Per separazione command/query nei servizi
- **Repository Pattern**: Per astrazione dati
- **Event-Driven**: Per comunicazione decoupled
- **Dependency Injection**: Per gestione servizi
- **Plugin System**: Per estensibilità

Vedi [12_ROADMAP.md](12_ROADMAP.md) per dettagli completi.

## Link Rapidi

- [README Principale](../README.md) - Panoramica del progetto
- [11_TODO.md](11_TODO.md) - Cosa stiamo costruendo

---

*Documento aggiornato: Marzo 2026*
