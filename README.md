# FlaskERP - Low-Code ERP Platform

FlaskERP is an open-source, modular ERP platform that enables organizations to build and customize their business management system through a low-code approach. Unlike traditional ERP solutions that impose rigid processes, FlaskERP allows complete flexibility in modeling data, workflows, and user interfaces.

---

## Key Differentiators

### Low-Code Builder

A built-in visual builder lets you define entities, fields, relationships, and views directly from the browser—no coding required. The system automatically generates:
- Database tables with proper indexes and foreign keys
- REST APIs for each entity
- UI forms and tables with sorting, filtering, and pagination

### Multi-Project Architecture

FlaskERP natively supports multiple isolated projects within a single installation. Each project has its own:
- Database schema
- Users and permissions
- Modules and configurations

This makes it ideal for consulting firms serving multiple clients, or enterprises with independent business units.

### Marketplace Ecosystem

A community-driven marketplace allows sharing and installing blocks (UI components) and modules (full-featured packages). Users can publish their creations for free or at a price, with a revenue-sharing model (70/30).

### AI Assistant with Embedded Tool Calling

An AI-powered assistant that generates ERP configurations from natural language. Simply describe what you need, and the AI creates entities, fields, relationships, and applies them directly to the database. Features:
- Natural language → JSON configuration
- RAG-based context injection (knows your project schema)
- **Embedded Tool Calling** - AI can operate directly on your data
- **Multi-LLM Support** - OpenRouter (DeepSeek) or Anthropic Claude
- **Business Logic Automation** - Workflows, Hooks, Scheduled Tasks
- **AI Test Generator** - Automatic test suite generation
- Tool Registry automatically generates CRUD tools from your dynamic models
- Preview and edit before applying
- Feedback loop for continuous learning

---

## Use Cases

### Consulting Firms & System Integrators
- Create customized ERP configurations for each client
- Reuse templates across similar implementations
- Reduce implementation time through modular components

### Small & Medium Enterprises
- Avoid the rigidity of off-the-shelf ERP systems
- Start with essential modules and expand as needed
- Customize workflows without vendor dependencies

### Software Development Teams
- Accelerate MVP development for business applications
- Leverage a solid foundation with auth, permissions, and API layer
- Focus business logic rather than infrastructure

---

## Architecture Highlights

| Layer | Description |
|-------|-------------|
| **Data** | SysModel + SysField = Custom entities with relations |
| **UI** | Block = Collection of Components (table, form, kanban, chart) |
| **Business Logic** | Hooks = Synchronous handlers (validation, calculations) |
| **Integration** | Event Bus + REST API + Webhooks |
| **AI** | Natural language → Auto-generated configurations |

### Technology Stack

- **Backend**: Flask 3.x + SQLAlchemy + PostgreSQL 14+
- **API**: Flask-smorest with OpenAPI/Swagger
- **Frontend**: React 19 + Ant Design
- **Auth**: JWT with refresh tokens
- **AI**: OpenRouter (DeepSeek) or Anthropic Claude + Tool Registry
- **Container**: Docker

---

## Getting Started

```bash
# Clone the repository
git clone https://github.com/your-repo/flaskERP.git

# Start with Docker
docker-compose up -d

# Access the web interface
open http://localhost:8080
```

---

## Documentation Structure

| Document | Description |
|----------|-------------|
| [docs/01_ARCHITETTURA.md](docs/01_ARCHITETTURA.md) | Core concepts: SysModel, Block, Module |
| [docs/02_BUILDER.md](docs/02_BUILDER.md) | Creating entities, fields, relations |
| [docs/03_MODULI.md](docs/03_MODULI.md) | Available modules and lifecycle |
| [docs/04_AMMINISTRAZIONE.md](docs/04_AMMINISTRAZIONE.md) | Users, permissions, backups |
| [docs/05_MARKETPLACE.md](docs/05_MARKETPLACE.md) | Publishing and installing |
| [docs/06_AUTOMAZIONE.md](docs/06_AUTOMAZIONE.md) | Hooks, Events, Workflows |
| [docs/07_INTEGRAZIONI.md](docs/07_INTEGRAZIONI.md) | API, Webhooks, Registry |
| [docs/10_AI_ASSISTANT.md](docs/10_AI_ASSISTANT.md) | AI Assistant for auto-configuration |
| [docs/PROJECT_ANALYSIS.md](docs/PROJECT_ANALYSIS.md) | Technical deep-dive |
| [docs/ERPSEED_PLATFORM.md](docs/ERPSEED_PLATFORM.md) | Open source infrastructure (Nextcloud) |

---

## Target Audience

- **Technical Consultants**: Need flexible, replicable configurations
- **SMBs**: Want customization without expensive development
- **Dev Teams**: Need a head-start on business applications

---

## License

MIT License - See LICENSE file for details

---

## About ERPSeed

FlaskERP is developed by **ERPSeed**, an open ecosystem that combines technology, education, and community to create opportunities for young people and small businesses.

For more information about the ERPSeed project, community nodes, and how to join, see [docs/ERPSEED.md](docs/ERPSEED.md).

---

**FlaskERP: Build your ERP. Your way.**
