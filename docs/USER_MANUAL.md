# ERPSeed User Manual

> **Language Policy Note**: Technical and architectural documentation is maintained in Italian (IT) as the primary project language. The User Manual is provided in English (EN) to support international business users and teams, aligned with ERPSeed's built-in multi-language (i18n EN/IT) capabilities.

---

## Introduction
ERPSeed is a modular, AI-first Low-Code platform designed to build complex business management systems quickly and efficiently, combining runtime dynamic models with pre-built vertical ERP modules.

---

## Core Concepts

### Tenants
A **Tenant** is a top-level organizational unit (e.g., a Company). All data, users, and projects are strictly isolated within a tenant using row-level security (`tenant_id`).

### Projects
A **Project** is a specific application workspace within a tenant (e.g., CRM, Inventory, HR). Each project has its own data models, views, workflows, and settings.

### Models
Models define the structure of your data.
- **System Models**: Built-in core entities like Users, Projects, and Audit Logs.
- **Dynamic Models**: Custom tables created by administrators using the No-Code Builder.

### Fields
Fields represent model attributes. ERPSeed supports many types:
- **Basic**: Text, Integer, Decimal, Date, DateTime, Boolean.
- **Advanced**: Select (dropdowns), MultiSelect, Relation (Foreign Key links), File/Image uploads, Currency.
- **Dynamic**: Computed (formulas), Summary (aggregates).

---

## Platform Tools & Low-Code Builder

### Dashboard & Analytics
The main dashboard provides real-time KPIs, visual charts (Bar, Line, Pie via Ant Design & ECharts), and shortcuts to primary applications.

### The Builder
1. **Model Builder**: Create custom tables, fields, and visual relationships (Entity-Relationship diagram via XYFlow).
2. **View Builder**: Design list views, forms, and kanban boards.
3. **Workflow Builder**: Automate business tasks based on triggers (e.g., status changes or scheduled events).

### AI Assistant
The AI Assistant helps build applications using natural language. You can prompt it to:
- "Create a customer feedback model with rating and comment fields."
- "Show me a list of all pending sales orders."
- "Generate a monthly revenue report."

---

## Core ERP Modules

### 1. Master Data (Anagrafiche)
- **Entities (Soggetti)**: Central registry for Customers, Suppliers, Employees, and Leads.
- **Roles & Contacts**: Assign roles (e.g., Client, Vendor) and attach multiple contacts (Email, Phone, PEC).
- **Addresses & Geography**: Manage physical addresses with localized Italian municipality lookup (`Comuni`) and street auto-completion (`Via` cache).

### 2. Purchases & Returns (Acquisti)
- **Purchase Requests & RFQs**: Draft internal purchase requisitions and Request for Quotations from suppliers.
- **Purchase Orders**: Manage supplier orders with item lines, tax rates, and delivery schedules.
- **Goods Receipt (DDT Entrata)**: Process inbound deliveries and automatically adjust warehouse stock levels.
- **Purchase Returns**: Issue purchase returns for defective goods and handle inventory deductions.

### 3. Sales & CRM (Vendite)
- **CRM Leads & Opportunities**: Manage pipeline sales stages with kanban views and deal tracking.
- **Quotations & Sales Orders**: Convert quotes to confirmed sales orders with automated pricing and discounts.
- **Delivery Notes (DDT Vendita)**: Generate outbound shipping documents and trigger stock deductions.
- **Contracts**: Track recurring customer contracts, renewal dates, and terms.

### 4. Inventory & Warehouse (Magazzino)
- **Stock Levels & Movements**: Monitor multi-location stock levels and real-time movement logs (carico/scarico).
- **Lots & Serials**: Track product lot batches, expiry dates, and serial numbers.
- **Physical Counts**: Conduct inventory audits and record stock adjustments.

### 5. Accounting & Finance (Contabilità)
- **Chart of Accounts & General Ledger**: Manage account plans and double-entry journal entries (Prima Nota).
- **Maturities & Receivables/Payables**: Track payment due dates, overdue notices, and record payments.
- **VAT Registers & Liquidations**: Generate periodic VAT registers (Acquisti/Vendite), calculate VAT liquidations, and process Intrastat declarations.
- **Banking & Ri.Ba.**: Create electronic bank collection batches (Ricevute Bancarie).
- **Electronic Invoicing**: Generate standard Italian `FatturaElettronicaPA 1.2` XML files directly from issued invoices.

### 6. Human Resources (HR)
- **Employees & Departments**: Maintain employee profiles, organizational hierarchies, and roles.
- **Attendance & Leaves**: Track daily check-in/out logs, leave requests, and manager approvals.
- **Payroll**: Manage monthly payroll periods and generate payslip records.
- **Training & Skills**: Track employee training courses, skill matrices, and certifications.

### 7. Production & Manufacturing (Produzione)
- **Bill of Materials (BOM)**: Define multi-level product structures and raw material quantities.
- **Work Cycles & Operations**: Map production phases, machine centers, and labor hours.
- **Production Orders & MRP**: Issue production orders, track execution status, and run Material Requirements Planning (MRP) calculations.

---

## Data Operations & Utilities

### Data Import & Export
Dynamic models and standard entities support batch CSV import and export. Use the **Import** and **Export CSV** buttons on list views.

### Column Customization
Click the **Colonne** button on any table header to customize column visibility, reorder columns, or reset table preferences (saved to local browser storage).

### GDO Reconciliation
Specialized matching engine for reconciling external data sources (e.g., bank statements vs. invoices) using subset-sum algorithms, exporting formatted Excel reports.

### Webhooks & API Integration
Configure automated outbound webhooks on key events (`order.created`, `user.created`, `record.created`) with signature verification and manual test deliveries.

---

## Administration & Security

### Multi-Tenancy & Roles
All requests are scoped to the active tenant via header `X-Tenant-ID`, subdomain, or user JWT context. User roles (Admin vs. Operator) dictate access to system settings and the No-Code Builder.

---

## Support & Resources
- **Developer Guide**: [DEVELOPER_GUIDE.md](./DEVELOPER_GUIDE.md)
- **API Reference**: [API.md](./API.md)
- **Fleet Tutorial**: [TUTORIAL_FLEET.md](./TUTORIAL_FLEET.md)
