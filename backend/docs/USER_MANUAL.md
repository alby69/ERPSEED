# ERPSeed User Manual

## Introduction
ERPSeed is a modular, AI-first Low-Code platform designed to build complex business management systems quickly and efficiently.

---

## Core Concepts

### Tenants
A **Tenant** is a top-level organizational unit (e.g., a Company). All data, users, and projects are strictly isolated within a tenant.

### Projects
A **Project** is a specific application within a tenant (e.g., CRM, Inventory, HR). Each project has its own data models, views, and settings.

### Models
Models define the structure of your data.
- **System Models**: Built-in entities like Users or Projects.
- **Dynamic Models**: Created by you using the Builder.

### Fields
Fields are the properties of a model. ERPSeed supports many types:
- **Basic**: Text, Integer, Decimal, Date, Boolean.
- **Advanced**: Select (dropdowns), Relation (links to other models), File/Image uploads.
- **Dynamic**: Computed (formulas), Summary (aggregates).

---

## Using the Platform

### Dashboard
The main dashboard provides an overview of your projects and key performance indicators (KPIs).

### The Builder
The Builder is where you design your application.
1. **Model Builder**: Create tables and columns.
2. **View Builder**: Design lists, forms, and kanban boards using a drag-and-drop interface.
3. **Workflow Builder**: Automate tasks based on events (e.g., "when a record is updated").

### AI Assistant
The AI Assistant can help you build your application using natural language. You can ask it to:
- "Create a customer model with name and email."
- "Show me a list of all pending orders."
- "Create a dashboard showing monthly sales."

---

## Advanced Features

### Data Import/Export
Every dynamic model automatically supports CSV import and export. Look for the "Import" and "CSV" buttons in any list view.

### GDO Reconciliation
A specialized tool for matching large datasets (e.g., bank statements vs. invoices) using advanced algorithms like Greedy Subset Sum.

### Webhooks
Integrate ERPSeed with external systems by setting up webhooks that trigger on CRUD operations.

---

## Administration

### User Management
Manage users and their roles (Admin vs. User). Admins can access the Builder, while Users can only use the generated applications.

### Multi-Tenancy
Access different tenants via subdomains (e.g., `company1.erpseed.com`) or by providing the `X-Tenant-ID` header in API requests.

---

## Support
For more help, consult the [Tutorials](./TUTORIAL_FLEET.md) or contact your system administrator.
