# ERPSeed - Technical Project Analysis

## Executive Summary

ERPSeed is a modular, low-code ERP platform built with Flask and React. Its core value proposition is enabling organizations to model and evolve their business management system without being constrained by pre-defined processes or requiring extensive custom development.

---

## 1. System Overview

### 1.1 Problem Statement

Traditional ERP systems impose rigid structures that force businesses to adapt their processes to the software. This creates:

- High customization costs
- Vendor lock-in
- Limited flexibility for evolving business needs
- Long implementation timelines

### 1.2 Solution Approach

ERPSeed inverts this paradigm: **the software adapts to the business**. Through a low-code builder, users define their own entities, relationships, and workflows while the platform handles:

- Database schema generation
- REST API exposure
- UI component rendering
- Authentication and authorization

Additionally, FlaskERP includes an **AI Assistant** that generates configurations from natural language, accelerating the modeling process and making ERP customization accessible to non-technical users.

---

## 2. Architectural Concepts

### 2.1 Core Abstractions

The system is built on four fundamental abstractions:

#### SysModel (Entity)

Represents a business entity. Corresponds to a database table.

```python
# Example: Defining a SysModel
class SysModel:
    name: str              # Display name
    table_name: str        # Database table
    fields: List[SysField]  # Schema definition
    components: List[Component]  # UI representation
```

#### SysField (Field)

Defines an attribute of a SysModel with type and validation.

| Type         | Database    | Use Case                  |
| ------------ | ----------- | ------------------------- |
| `string`     | VARCHAR     | Short text (codes, names) |
| `text`       | TEXT        | Long descriptions         |
| `integer`    | INTEGER     | Quantities, counts        |
| `decimal`    | NUMERIC     | Money, measurements       |
| `boolean`    | BOOLEAN     | Flags, binary states      |
| `date`       | DATE        | Calendar dates            |
| `datetime`   | TIMESTAMP   | Timestamps                |
| `select`     | ENUM        | Fixed choices             |
| `relation`   | FOREIGN KEY | Entity relationships      |
| `summary`    | VIRTUAL     | Aggregated data           |
| `calculated` | VIRTUAL     | Derived values            |

#### Block (UI Collection)

A Block groups one or more Components with relationships between them. It's the minimum publishable unit in the Marketplace.

```python
class Block:
    name: str
    components: List[Component]
    # Relationships define how components interact
    # e.g., selecting a customer shows their orders
```

#### Module (Functional Unit)

The complete package combining:

- **SysModel**: Data entities
- **Block**: User interfaces
- **Hook**: Business logic (synchronous)
- **API**: Exposed endpoints

```
┌─────────────────────────────────────┐
│              MODULE                 │
│  ┌─────────┐ ┌───────┐ ┌─────────┐  │
│  │ SysModel│ │ Block │ │  Hook  │  │
│  │ (Data)  │ │ (UI)  │ │(Logic)  │  │
│  └─────────┘ └───────┘ └─────────┘  │
│  ┌─────────────────────────────────┐ │
│  │            API                 │ │
│  │      REST Endpoints           │ │
│  └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

### 2.2 Multi-Tenancy Model

FlaskERP implements **project-based isolation**:

```
┌─────────────────────────────────────────────────────────┐
│                   FLASKERP INSTANCE                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│   ┌──────────────┐   ┌──────────────┐   ┌───────────┐  │
│   │   PROJECT A  │   │  PROJECT B   │   │ PROJECT C │  │
│   │  (Client 1) │   │ (Client 2)   │   │ (Internal)│  │
│   ├──────────────┤   ├──────────────┤   ├───────────┤  │
│   │ - Schema     │   │ - Schema     │   │ - Schema  │  │
│   │ - Users      │   │ - Users      │   │ - Users   │  │
│   │ - Modules    │   │ - Modules    │   │ - Modules │  │
│   │ - Data       │   │ - Data       │   │ - Data    │  │
│   └──────────────┘   └──────────────┘   └───────────┘  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

Each project has isolated:

- Database schema (separate tables or database)
- User authentication and session
- Module installations
- Data records

Projects can share **templates** for reusable configurations.

---

## 3. Automation & Communication

### 3.1 Hook System

Synchronous handlers executed within the same transaction as the CRUD operation.

```python
# Validation hook
@hook("order.before_create", priority=5)
def validate_order(order):
    if order.total > 10000 and not order.approved_by:
        raise ValidationError("Orders over 10000 require approval")

# Calculation hook
@hook("invoice_line.after_create", priority=10)
def recalculate_total(line):
    invoice = line.invoice
    invoice.total = sum(l.amount for l in invoice.lines)
    db.session.commit()
```

**Available Hooks:**
| Event | Timing | Use Case |
|-------|--------|----------|
| `before_validate` | Before field validation | Pre-process data |
| `after_validate` | After validation | Custom validation |
| `before_create` | Before INSERT | Validate, set defaults |
| `after_create` | After INSERT | Post-creation logic |
| `before_update` | Before UPDATE | Audit, restrictions |
| `after_update` | After UPDATE | Cascading updates |
| `before_delete` | Before DELETE | Cleanup, restrictions |
| `after_delete` | After DELETE | Cascade deletion |

### 3.2 Event Bus

Asynchronous pub/sub system for inter-module communication.

```python
# Publisher
EventBus.publish("order.created", {
    "order_id": 123,
    "customer": "Acme Corp",
    "total": 15000.00
})

# Subscriber
def notify_sales_manager(data):
    send_email("manager@company.com", "New Order", data)

EventBus.subscribe("order.created", notify_sales_manager)
```

### 3.3 Workflow Engine

Declarative automation sequences configured via UI.

```json
{
  "name": "Order Approval Flow",
  "trigger": "order.created",
  "steps": [
    {
      "type": "condition",
      "config": { "field": "total", "operator": ">", "value": "10000" },
      "on_true": [
        { "type": "notification", "to": "manager@company.com" },
        { "type": "action", "field": "status", "value": "pending_approval" }
      ],
      "on_false": [{ "type": "action", "field": "status", "value": "approved" }]
    }
  ]
}
```

---

## 3.4 AI Assistant

The AI Assistant is a natural language interface that generates ERP configurations automatically. It's the "fourth pillar" of FlaskERP: **Self-Modifying Code**.

### How It Works

```
User describes need → AI analyzes → AI generates config → System applies → Result
```

Users describe what they need in plain language, and the AI creates:

- SysModel entities with fields
- Relationships between models
- API endpoints
- UI components

### Example

**User Input:**

> "Create a module to manage vehicles with drivers and maintenance"

**AI Output:**

- Model `Veicolo` (targa, marca, modello, anno, km, stato)
- Model `Conducente` (nome, cognome, patente)
- Model `Manutenzione` (veicolo, tipo, date, costo)
- Model `Assegnazione` (veicolo, conducente, date)

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    AI ASSISTANT                         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │   Chat UI   │───►│ LLM (RAG)   │───►│  Tool Call │ │
│  │  (React)    │    │ DeepSeek V3 │    │  (JSON)    │ │
│  └─────────────┘    └─────────────┘    └──────┬──────┘ │
│                                                │         │
│                                                ▼         │
│                                    ┌─────────────────────┐ │
│                                    │   Apply Config     │ │
│                                    │  (Create Tables)   │ │
│                                    └─────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Key Features

| Feature                    | Description                               |
| -------------------------- | ----------------------------------------- |
| **Natural Language Input** | Describe needs in Italian or English      |
| **RAG Context Injection**  | AI knows your existing project schema     |
| **JSON Preview**           | Review and edit before applying           |
| **Auto-Application**       | Creates tables and fields in database     |
| **Feedback Loop**          | Learns from conversations for improvement |

### Implementation

| Component    | Technology                  |
| ------------ | --------------------------- |
| LLM          | OpenRouter (DeepSeek V3)    |
| Context      | RAG with project schema     |
| Tool Calling | generate_json, apply_config |
| Storage      | AIConversation model        |

### API Endpoints

| Endpoint                | Method | Description                           |
| ----------------------- | ------ | ------------------------------------- |
| `/api/ai/generate`      | POST   | Generate config from natural language |
| `/api/ai/apply`         | POST   | Apply config to database              |
| `/api/ai/feedback`      | POST   | Save feedback for learning            |
| `/api/ai/conversations` | GET    | List conversation history             |

### Status

| Component                    | Status      |
| ---------------------------- | ----------- |
| Architecture                 | ✅ Complete |
| LLM Integration (OpenRouter) | ✅ Complete |
| RAG Context Injection        | ✅ Complete |
| Tool Calling                 | ✅ Complete |
| Chat Interface               | ✅ Complete |
| Auto-apply to DB             | ✅ Complete |
| Feedback Loop                | ✅ Complete |

---

## 4. API Architecture

### 4.1 REST API Layer

Built with Flask-smorest with automatic OpenAPI documentation.

**Base Endpoints:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/projects` | List projects |
| POST | `/api/v1/projects` | Create project |
| GET | `/api/v1/projects/{id}` | Get project |
| GET | `/api/v1/modules` | List modules |
| POST | `/api/v1/modules/{id}/install` | Install module |

**Dynamic Module Endpoints:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/modules/{module}/{model}` | List records |
| POST | `/api/modules/{module}/{model}` | Create record |
| GET | `/api/modules/{module}/{model}/{id}` | Get record |
| PUT | `/api/modules/{module}/{model}/{id}` | Update record |
| DELETE | `/api/modules/{module}/{model}/{id}` | Delete record |

### 4.2 Authentication

JWT-based with refresh token flow:

```
┌─────────┐     ┌─────────┐     ┌─────────┐
│  Client │────►│  Auth   │────►│  JWT    │
│         │     │ Service │     │ Token   │
└─────────┘     └─────────┘     └─────────┘
                                     │
                                     ▼
                               ┌─────────┐
                               │  Validate│
                               │  & Claims│
                               └─────────┘
```

---

## 5. Available Modules

### Core (Always Available)

- **Auth**: User authentication and sessions
- **Projects**: Multi-project management
- **Builder**: Entity and UI definition

### Builtin (Included)

- **Anagrafica**: Parties, Roles, Addresses, Contacts
- **Prodotti**: Product catalog with variants
- **Vendite**: Sales cycle (Quote → Order → DDT → Invoice)
- **Acquisti**: Procurement cycle
- **Magazzino**: Inventory management with lot/serial tracking

### Roadmap

| Module      | Status  | Description                             |
| ----------- | ------- | --------------------------------------- |
| Contabilità | 70%     | Accounting, general ledger, e-invoicing |
| HR          | 50%     | Employee management, attendance         |
| Produzione  | Planned | Bill of materials, work orders          |
| CRM         | Planned | Sales pipelines, campaigns              |
| Progetti    | Planned | Task and milestone management           |
| Documentale | Planned | Document archival                       |
| Helpdesk    | Planned | Support ticketing                       |

---

## 6. Marketplace Model

### 6.1 Publishing Flow

```
Draft → Testing → Published → Deprecated
  │         │           │
  │         │           └── Available to all users
  │         │
  │         └── Quality checks (min 80% score)
  │
  └── Development in progress
```

### 6.2 Quality Requirements

| Test Type   | Description                             | Weight |
| ----------- | --------------------------------------- | ------ |
| CRUD        | Create, Read, Update, Delete operations | 40%    |
| Validation  | Required, unique, regex validation      | 30%    |
| Relation    | Foreign key integrity                   | 20%    |
| Performance | Query time < 1 second                   | 10%    |

### 6.3 Revenue Sharing

- **Author**: 70% of sale price
- **Platform**: 30% for maintenance and development

---

## 7. Technology Stack

| Layer      | Technology    | Version |
| ---------- | ------------- | ------- |
| Backend    | Flask         | 3.x     |
| API        | Flask-smorest | Latest  |
| ORM        | SQLAlchemy    | 2.x     |
| Database   | PostgreSQL    | 14+     |
| Frontend   | React         | 19      |
| UI Library | Ant Design    | 5.x     |
| Auth       | PyJWT         | Latest  |
| Container  | Docker        | Latest  |

---

## 8. Deployment

### 8.1 Development

```bash
# Start all services
docker-compose up -d

# Access
# Frontend: http://localhost:8080
# Backend API: http://localhost:5000
# Database: localhost:5432
```

### 8.2 Production Considerations

- PostgreSQL with connection pooling
- Reverse proxy (Nginx) for SSL termination
- Celery for async background tasks
- Redis for event bus and caching
- Automated backups with pg_dump

---

## 9. Security Model

### 9.1 Authentication

- JWT access tokens (short-lived)
- Refresh tokens (long-lived, stored securely)
- Optional MFA support

### 9.2 Authorization

- Role-based access control (RBAC)
- Granular permissions per entity:
  - Create
  - Read
  - Update
  - Delete
- Field-level visibility (future)

### 9.3 Audit

- Complete action logging
- User, timestamp, IP tracking
- Before/after state capture

---

## 10. Extension Points

### 10.1 Custom Hooks

```python
# In your module's hooks.py
@hook("custom_entity.before_create", priority=10)
def my_custom_logic(entity):
    # Your business logic
    pass
```

### 10.2 Custom API Endpoints

```python
# In your module's api.py
@api.route('/custom-endpoint')
class CustomEndpoint(Resource):
    @api.doc()
    def get(self):
        return {"message": "Custom response"}
```

### 10.3 Webhooks

Expose internal events to external systems:

```json
{
  "url": "https://external.system.com/webhook",
  "events": ["order.created", "order.updated"],
  "secret": "your-webhook-secret"
}
```

---

## 11. Strengths & Considerations

### Strengths

- **True flexibility**: No predefined structure forces
- **Multi-tenant**: Native support for multiple isolated projects
- **API-first**: Every entity automatically exposes REST endpoints
- **Extensible**: Hooks, events, and workflows for customization
- **Community**: Marketplace for sharing and monetization

### Considerations

- **Complexity**: High flexibility requires careful modeling
- **Testing**: Custom modules need thorough testing (quality score ≥80%)
- **Performance**: Dynamic schema vs. optimized static queries
- **Migration**: Schema evolution requires careful handling

---

## 12. Comparison with Alternatives

| Feature       | FlaskERP           | Odoo                | ERPNext            |
| ------------- | ------------------ | ------------------- | ------------------ |
| Architecture  | Modular + Low-code | Modular             | Modular            |
| Customization | Builder + Code     | Studio + Code       | Script + Framework |
| Multi-tenant  | Native             | Native (enterprise) | Via frappe_io      |
| Marketplace   | Community          | Official + Partners | Community          |
| Open Source   | Yes                | Yes (Community)     | Yes                |
| Tech Stack    | Flask + React      | Python + XML        | Frappe + React     |

---

_Document generated: February 2026_
_For technical documentation, see individual guides in `/docs`_
