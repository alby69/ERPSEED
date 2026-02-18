# MakeERP - The ERP Engine

MakeERP is an open-source "Low-Code" engine designed to build, run, and deploy complex management systems. It's not just an ERP, but a platform to create *your* ERP (e.g., Fleet Management, CRM, WMS) through dynamic data definition.

## Project Vision

The goal is to create a flexible and powerful open-source alternative to traditional monolithic ERPs, following modern development principles:

- **Extreme Modularity**: Each business function (Accounting, Sales, Warehouse) is a separate module that can be enabled or disabled.
- **Decoupling**: Modules communicate via well-defined internal APIs, reducing dependencies and facilitating parallel development.
- **Engine vs Blueprint**: The engine (MakeERP) is separate from the business logic (Blueprint). You can export your "Car Fleet" project to a JSON file and deploy it anywhere.
- **Multi-Project**: The engine is designed to handle multiple independent projects (e.g., one instance per client), each with its own models and data, ensuring isolation.
- **Professional UI/UX**: A fast, intuitive, and responsive web interface (Single Page Application).
- **Cloud-Native**: Designed to be deployed, scaled, and managed on cloud platforms.

---
## Project Management and Multi-Tenancy

FlaskERP is built on a powerful project management system that allows for complete data and configuration isolation, making it an ideal solution for multi-tenancy.

- **Projects as Containers**: Each project (e.g., "Logistics", "CRM Client Alpha", "WMS for Central Warehouse") acts as an autonomous container for its own data models, configurations, members, and permissions.

- **Data Isolation via Schema**: To ensure data security and isolation, FlaskERP creates a dedicated PostgreSQL schema for each project (e.g., `project_1`, `project_2`). This means that one client's data will never mix with another's, even if they share the same infrastructure.

- **Member Management**: Add users to specific projects with distinct roles (e.g., Administrator, Editor, Viewer). Permissions are applied at the project level, ensuring that users only see and modify what they are allowed to.

- **Project Templates (Import/Export)**:
  - **Export**: Export the entire architecture of a project—including all its models, fields, and configurations—into a JSON template file. This is perfect for backing up your applications or sharing "ready-to-use solutions" with others.
  - **Import**: Create new projects from a template with a single click. The system can create a new project or update an existing one (upsert), intelligently managing changes to models and fields. This drastically speeds up implementation times for new clients or environments.

## 🏛️ Architecture

We propose a "Modular Monolith" architecture with a separate SPA frontend.

1.  **Backend (Flask)**:
    - **Modular Structure**: The code resides in the `backend/` folder. Each domain (e.g., `users`, `projects`, `sales`) is an isolated module with its own routes, models, and schemas.
    - **API-Driven**: The backend exclusively exposes REST/JSON APIs. It does not render HTML.
    - **Inter-Module Communication**: Modules communicate via well-documented internal APIs (OpenAPI standard), ensuring decoupling.

2.  **Frontend (React/SPA)**:
    - The UI is a completely separate JavaScript application that lives in the browser.
    - It communicates with the Flask backend exclusively through REST APIs.
    - This ensures a smooth and fast user experience, without page reloads.

3.  **Database (PostgreSQL)**:
    - A single PostgreSQL database serves as the "source of truth".
    - SQLAlchemy maps tables to Python objects, simplifying queries and ensuring consistency.

### 🏗️ ERP Builder (No-Code Engine) - *Active*

The heart of the project is the **Builder**, a system for extending the ERP directly from the web interface, without writing code.

#### 1. Dynamic Model Management
The backend now supports model definition via API, allowing for the dynamic creation of:
- **Projects**: Logical containers for grouping models and configurations (e.g., "Fleet Management", "CRM Client X").
- **Tables** (Entities) via the `SysModel` model.
- **Fields** (`SysField`) with a wide range of types: `string`, `integer`, `boolean`, `date`, `select`, `file`, `image`, `calculated` (frontend).
- **Relations** (via the `relation` type), **Backend Calculated Fields** (`formula`), **Summary Fields** (`summary`), and **Lookup Fields** (`lookup`).

#### 2. Dynamic Runtime
The backend will include an engine capable of:
- Saving model definitions in system tables (`sys_models`, `sys_fields`) within a **Project**.
- Generating/Updating the PostgreSQL database schema for each project in an isolated manner (`CREATE SCHEMA project_x`).
- Automatically exposing CRUD APIs for new models, contextualized by project (e.g., `/projects/<id>/data/<model_name>`).

#### 3. Frontend Automation (`GenericCrudPage.jsx`)
The frontend is equipped with **Metadata-Driven** components:
- **`GenericCrudPage`**: Renders tables and forms based on a JSON configuration.
- The Builder will link backend metadata directly to this component, allowing new tables to be displayed instantly.

**Key Components:**
- **`GenericCrudPage`**: Manages state, data fetching, modals, forms, backend error validation, and file uploads.
- **`DataTable`**: Pure table rendering with support for custom actions.
- **`SearchBar` / `Pagination`**: Reusable UI components.
- **`Layout`**: Wrapper for the application structure (Sidebar, Navbar).

---

## 🗂️ Data Model (ER) - Initial Concept

The data model is designed to be flexible and scalable.

- **`User`**: Manages digital identity. Contains email, password hash, status (active/inactive). It is the actor that *uses* the system.
- **`Role` / `Permission`**: Define roles (e.g., "Administrator", "Warehouseman") and granular permissions ("can create sales order", "can see stock levels").
- **`Party` / `Contact`**: Generic master data for any legal entity or person. A `type` attribute distinguishes between `Customer`, `Supplier`, `Subsidiary`, `Individual`, etc.
- **`Address`**: Reusable addresses, linked to master data.
- **`Product`**: Product/service master data.
- **Module-Specific Tables**: `SalesOrder`, `PurchaseOrder`, `InventoryMovement`, `GlEntry` (accounting entry), etc.

This approach avoids complex inheritance and allows an entity to have multiple roles (e.g., a company can be both a customer and a supplier).

---

## 🚀 Phased Development Plan

1.  **Phase 0: Foundations and Setup (Completed)**
    - [x] Definition of the architecture and development plan.
    - [x] Creation of the project structure.
    - [x] Setup of the virtual environment (managed via Docker).
    - [x] Installation of initial dependencies (Flask, SQLAlchemy, etc.).
    - [x] Basic configuration of the Flask application and DB connection.
    - [x] Creation of the first data model with SQLAlchemy and Alembic (`User`).

2.  **Phase 1: User and Access Management (IAM) (Completed)**
    - [x] `User` model.
    - [x] API endpoint for user registration.
    - [x] API endpoint for login (with JWT).
    - [x] Protected test endpoint (`/me`).
    - [x] Decorators to protect endpoints based on roles/permissions.
    - [x] Creation of the basic UI (React SPA) for login and user management.
    - [x] Implementation of Generic Frontend (`GenericCrudPage`) for rapid development.

3.  **Phase 2: Basic Master Data (Completed)**
    - [x] `Party` (Customers/Suppliers) and `Product` models.
    - [x] CRUD (Create, Read, Update, Delete) APIs with filtering and pagination.
    - [x] UI for managing basic master data.

4.  **Phase 3: First Functional Module (Sales) (Completed)**
    - [x] `SalesOrder` and `SalesOrderLine` models.
    - [x] API for creating and managing orders.
    - [x] Advanced UI for order management (Master-Detail).
    - [x] PDF generation for orders.

5.  **Phase 4: Inventory & Purchases (Completed)**
    - [x] Inventory module (Locations, Stock, Movements, Counts).
    - [x] Purchases module (Purchase Orders).
    - [x] API and UI for inventory management.

6.  **Phase 5: Accounting (In Progress)**
    - [x] Chart of Accounts (`ChartOfAccounts`).
    - [x] Journal Entries (Double-entry bookkeeping).
    - [x] Invoices (Active/Passive).
    - [x] Trial Balance report.
    - [ ] PDF generation for invoices.
    - [ ] SDI integration (Italian electronic invoicing).

7.  **Phase 6: ERP Builder (No-Code) (Completed)**
    - [x] System models (`SysModel`, `SysField`) to define tables and fields.
    - [x] DB schema generation and update engine (`CREATE/ALTER TABLE`) per project.
    - [x] Dynamic Runtime API (`/projects/<id>/data/<model>`) complete (CRUD, relations, files, formulas).
    - [x] Administration UI for the Builder (model, field, ACL permission management).
    - [x] Dynamic Frontend (`GenericCrudPage`) for using the created applications.
    - [x] Advanced Features: Regex Validation, Frontend Calculated Fields, Dashboard Widgets.
    - [x] **Project Management and Multi-Tenancy**:
        - [x] Added `Project` model to group configurations.
        - [x] Member management per project (Owner/Admin).
        - [x] Data isolation per project (schema-based multi-tenancy).
        - [x] API to create, read, update, and delete Projects.
        - [x] Import/Export functionality for an entire Project as a JSON template.
        - [x] Project Versioning and Automatic Backups.

8.  **Phase 7: Module System (Completed)**
    - [x] Centralized module management (`ModuleDefinition`, `TenantModule`).
    - [x] Module enable/disable per tenant.
    - [x] Module licensing system (plans: starter, professional, enterprise).
    - [x] Frontend module management UI.
    - [x] Dynamic menu based on enabled modules.

9.  **Phase 8: HR Module (In Progress)**
    - [x] Departments.
    - [x] Employees.
    - [x] Attendance tracking.
    - [x] Leave requests.
    - [ ] Dashboard HR.
    - [ ] Payroll calculation.
        
---

## 🔧 Debugging and Troubleshooting

If you encounter problems with the APIs or the Frontend, follow this guide to isolate the issue.

### 1. Routing Issues (404 Not Found)
- **Static APIs**: Check `app/crud.py`. Routes are generated automatically. Verify that the model is registered in the blueprint.
- **Dynamic APIs**: Check `backend/dynamic_api.py`. These routes respond to `/projects/<project_id>/data/<model_name>`.
  - Verify that `model_name` exists in the `sys_models` table and is associated with the correct `project_id`.
  - Verify that the physical table exists in the DB (use `Generate Table` from the UI).

### 2. Database Issues (SQLAlchemy)
- If you modify a Python model (`app/models/`), you must generate a migration:
  ```bash
  flask db migrate -m "description"
  flask db upgrade
  ```
- If you modify a Dynamic model (from the Builder), you must click **"Generate/Update DB Table"** on the model detail page.

### 3. Frontend (React)
- **White Screen / Crash**: Often due to circular imports or double exports (e.g., `SysModelDetail`). Check the browser console (F12).
- **Fields not visible**: Verify that the metadata (`sys_fields`) is aligned with the `/data/<model>/meta` API response.

### 4. Complete Database Reset (Docker Environment)

If the database gets corrupted, the schema is no longer synchronized, or you simply want to start from scratch, you can use the reset script. **Warning: this operation will delete all data.**

1.  **Make sure the containers are running**:
    ```bash
    docker compose up -d
    ```

2.  **Run the reset script inside the `web` container**:
    ```bash
    docker compose exec web python -m backend.reset_db
    ```
    This command will execute the `reset_db.py` script, which handles deleting the database, recreating all tables according to the SQLAlchemy models, and inserting seed data (administrator, KPIs, etc.).

3.  **Restart the web service to apply the changes**:
    ```bash
    docker compose restart web
    ```

### 🏗️ Code Architecture (Refactoring in progress)

We are migrating towards a cleaner architecture (KISS/DRY):
- **`app/crud.py`**: Manages "Hard-coded" models (User, Party).
- **`backend/dynamic_api.py`**: Manages "No-Code" models. *Note: In the future, these two logics will be unified into a single `QueryBuilder`.*

---

## 📖 Builder User Manual

The **Builder** is the "Low-Code" heart of FlaskERP. It allows administrators to create, modify, and extend the application's functionalities directly from the web interface.

For a detailed guide on how to create projects, models, fields, and use advanced features, consult the **Builder Manual**.

## ✨ Advanced Builder Features

In addition to the basic creation of tables and fields, the Builder supports advanced features to create complex logic without code.

### 1. Calculated and Summary Fields
-   **Formula (Backend)**: Performs server-side mathematical calculations using the values of other fields. Example: `{quantity} * {price}`.
-   **Calculated (Frontend)**: Performs client-side calculations (JavaScript) for immediate display logic. Example: `{firstName} + ' ' + {lastName}`.
-   **Summary**: Aggregates data from a "child" table (1-to-N relationship). Useful for calculating totals, averages, or counts. Example: `SUM(total)` from the lines of an invoice.
-   **Lookup**: Retrieves and displays a value from a related table, avoiding complex joins in the frontend.

### 2. Conditional Logic
-   **Conditional Visibility**: Show or hide a field in the form based on the value of another field. Example: show the "Reason" field only if the status is "Rejected".
-   **Conditional Requirement**: Make a field mandatory only if another field has a certain value.

### 3. Custom Views (Kanban)
The Builder allows defining alternative data views besides the classic table.
-   **Kanban View**: Displays records as cards in columns representing a state (e.g., To Do, In Progress, Done).
-   **Configuration**:
    1.  In the model, define a `Select` type field for the status (e.g., "order_status").
    2.  In the model settings, set the **Default View** to `kanban`.
    3.  Select the status field in the new **Kanban Status Field** dropdown menu.
-   The system will automatically generate an interactive board with drag-and-drop to change the status of records.

### 4. Model Management
- **Clone**: Clone an existing model with a single click, duplicating all its fields and configurations. Useful for quickly creating new variants of complex models.
- **Schema Synchronization**: Safely apply changes to the model definition (adding fields, changing types) to the underlying database table (`ALTER TABLE`), preserving existing data.

### 5. Security and Data Maintenance
- **Reset Table**: Functionality to recreate the physical table schema (DROP/CREATE) in case of critical misalignment.
- **Automatic Backup**: Before each destructive operation (Reset), the system automatically creates a CSV backup of the data.
- **Download Backup**: Administrators can view the list of backups and download them directly from the interface.
- **Audit Log**: All significant builder actions (creation, modification, deletion of models/fields) are recorded in an audit log, providing a complete trail of changes.

## ⚙️ Development Environment Setup

The project is configured to work with **Docker**, which manages both the application and the database.

**Prerequisites**:
- Docker Desktop (or Docker Engine + Compose) installed.
- (Recommended) **Container Tools** extension (formerly Docker) for VS Code to manage containers visually.

**Steps**:

1.  **Clone the repository (if it exists)**
    ```bash
    cd flaskERP
    ```

2.  **Start the environment with Docker Compose**
    ```bash
    docker compose up --build
    ```
    This will download the images, build the app container, and start PostgreSQL.

3.  **Run the database migrations (in another terminal)**
    Since the DB is new and lives inside Docker, we need to run the migrations *inside* the `web` container:
    ```bash
    docker compose exec web flask db upgrade
    ```

4.  **Access the application**
    - API/Swagger: http://localhost:5000/swagger-ui
    - The local code is mounted in the container: any change to `.py` files will automatically restart the server.
---

## 📊 BI and Data Analysis

For data analysis, we will integrate a BI module based on **Dash by Plotly**.

- **Advantages**:
  - **Pure Python**: Dashboards are written entirely in Python.
  - **Perfect Integration**: It can be run as part of the Flask application, directly accessing SQLAlchemy models.
  - **Interactivity**: Create interactive charts and tables, drill-downs, dynamic filters.
- **Alternatives**: Although data can be exported for Power BI, the integrated solution reduces complexity and keeps all data within the application ecosystem, improving security and real-time analytics.

---

## ☁️ Cloud and Deployment Strategy

The architecture is designed for the cloud.

- **Containerization**: The Flask application and the React SPA will be containerized with **Docker**.
- **Orchestration**: It is recommended to use **Kubernetes** to manage containers in production, ensuring scalability, self-healing, and rolling updates.
- **PaaS**: Platforms like Heroku, Google App Engine, or AWS Elastic Beanstalk can be simpler alternatives for a quick start.
- **Managed Database**: Use services like Amazon RDS, Google Cloud SQL, or Azure Database for PostgreSQL to reliably manage the database.

---

## 🧩 Service Layer

Architecture for separating business logic from the API layer.

**Structure:**
```
backend/services/
├── base.py              # BaseService with common methods
├── user_service.py      # User logic
├── project_service.py   # Project logic
├── builder_service.py   # Builder logic
└── dynamic_api_service.py  # Dynamic API logic
```

**Advantages:**
- Clear separation between business logic and API routes
- Reusable code
- Greater testability
- Automatic integration with Webhooks and Workflows

---

## 🔌 Plugin System

Modular system for extending FlaskERP with additional functionalities.

**Integrated Plugins:**
- **Accounting**: Chart of Accounts, Journal Entries, Invoices
- **HR**: Employees, Departments, Attendance, Leave Requests

**Plugin API:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/hr/*` | Human Resources |
| GET | `/accounting/*` | Accounting |

**Create a New Plugin:**

1. Create the folder in `backend/plugins/my_plugin/`
2. Define the model that extends `BasePlugin`:
```python
# backend/plugins/my_plugin/plugin.py
from backend.plugins.base import BasePlugin

class MyPlugin(BasePlugin):
    name = "my_plugin"
    version = "1.0.0"
    
    def install(self):
        # Installation logic
        pass
    
    def uninstall(self):
        # Uninstallation logic
        pass
```

3. Register the plugin in `backend/__init__.py`:
```python
from .plugins.my_plugin.plugin import get_plugin as get_my_plugin
PluginRegistry.register(get_my_plugin())
PluginRegistry.enable('my_plugin', app=app, db=db, api=api)
```

**Extended Events:**
Plugins can trigger custom webhook events to integrate with Workflow Automation.

---

## 🔌 Extensions

### Webhooks

Event-driven integration system to connect FlaskERP to external services.

**Features:**
- Creation of configurable webhook endpoints
- Support for over 20 events (user.created, project.created, record.created, invoice.created, etc.)
- HMAC signature for payload authentication
- Automatic retry system (3 attempts with backoff)
- Delivery history with status and logs

**API Endpoints:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/webhooks` | List and create endpoints |
| GET/PUT/DELETE | `/webhooks/<id>` | Manage endpoints |
| POST | `/webhooks/<id>/test` | Test endpoint |
| GET | `/webhooks/deliveries` | Delivery history |
| GET | `/webhooks/events` | Available events |

**Available Events:**
- **User**: user.created, user.updated, user.deleted, user.login
- **Project**: project.created, project.updated, project.deleted
- **Model**: model.created, model.updated, model.deleted
- **Data**: record.created, record.updated, record.deleted
- **Accounting**: journal.created, journal.posted, invoice.created, invoice.paid
- **HR**: employee.created, employee.updated, leave.requested, leave.approved

**Usage:**
```python
# Webhooks are triggered automatically by triggers
# Example: when a user is created
from backend.webhook_triggers import on_user_created
on_user_created(user)
```

---

### Workflow Automation

Automation engine to create event-based workflows.

**Features:**
- Creation of workflows with event triggers
- 5 step types: condition, action, notification, delay, webhook
- Automatic execution when events occur
- Execution history with detailed logs
- Manual testing of workflows

**API Endpoints:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/workflows` | List and create workflows |
| GET/PUT/DELETE | `/workflows/<id>` | Manage workflows |
| POST | `/workflows/<id>/steps` | Add step |
| GET | `/workflows/<id>/executions` | Execution history |
| POST | `/workflows/<id>/test` | Test workflow |
| GET | `/workflows/triggers` | Trigger events |
| GET | `/workflows/step-types` | Step types |

**Step Types:**

1. **Condition** - Evaluates conditions on data
   - Operators: equals, not_equals, contains, greater_than, less_than, is_empty, is_not_empty

2. **Action** - Executes actions
   - set_field, update_record, create_record, send_email

3. **Notification** - Sends notifications
   - webhook, email

4. **Delay** - Timed pause
   - seconds, minutes, hours, days

5. **Webhook** - Calls external services
   - POST, PUT, PATCH with configurable headers

**Usage Example:**

1. Create a workflow from the UI (`/admin/workflows`)
2. Set the trigger (e.g., `record.created`)
3. Add automation steps
4. Activate the workflow

**Database Migration:**
```bash
flask db upgrade
# or if you use Docker:
docker compose exec web flask db upgrade
```

---

## 📋 Planned Next Extensions

- **Redis Caching**: Caching system to improve performance
- **Scheduled Tasks**: Periodic tasks for automations (cron-like)
