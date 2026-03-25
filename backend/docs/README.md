# ERPSEED Backend Documentation

Benvenuto nella documentazione del backend ERPSEED.

## 📚 Documentazione

| Documento | Descrizione |
|-----------|-------------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Architettura del sistema, pattern, struttura |
| [API.md](API.md) | Endpoint API, autenticazione, formato risposte |
| [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) | Guida per sviluppatori, setup, testing |
| [ROADMAP.md](ROADMAP.md) | Piani di sviluppo futuri e miglioramenti |

## 🚀 Quick Start

```bash
# 1. Installa dipendenze
pip install -r requirements.txt

# 2. Configura ambiente
cp .env.example .env  # se presente

# 3. Avvia server di sviluppo
python run.py
```

## 🏗️ Panoramica

ERPSEED è un sistema ERP modulare con:

- **Builder No-Code**: Crea modelli dati dinamici via API
- **Multi-Tenancy**: Isolamento per tenant/client
- **Workflow Engine**: Automazione processi
- **Webhook System**: Integrazioni event-driven
- **AI Assistant**: Assistenza intelligente

## 📁 Struttura Progetto

```
backend/
├── core/              # Autenticazione, tenant, permessi
├── services/          # Logica di business
├── builder/           # Sistema no-code builder
├── entities/          # Entità di dominio
├── webhook_*/         # Sistema webhooks
├── workflow_*/        # Motore workflow
├── docs/             # Questa documentazione
└── ...
```

## 🔗 Link Utili

- [Frontend Repository](../frontend/)
- [Docker Setup](../docker-compose.yml)
- [Issue Tracker](https://github.com/alby69/ERPSEED/issues)

---

Ultimo aggiornamento: 2026-03-18
