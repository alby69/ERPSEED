# flaskERP Project Structure Analysis

This document provides a detailed analysis of the flaskERP project structure, its modules, and their interconnections.

## High-Level Overview

The project is a "modular monolith" with a decoupled frontend. It is organized into several key directories:

- **`app/`**: Contains the core, "static" part of the Flask application. This includes foundational models like Users and Parties, standard CRUD logic, and application configuration. It seems to be the older part of the application or the foundation on which the dynamic builder is built.
- **`backend/`**: Contains the newer, dynamic "No-Code/Low-Code Builder" logic. This is the heart of the project, managing dynamic projects, models, fields, and generating APIs on the fly.
- **`frontend/`**: A modern React-based Single Page Application (SPA) that consumes the APIs provided by the Flask backend.
- **`migrations/`**: Contains the Alembic database migration scripts for the static models.
- **Root Directory**: Contains orchestration files (`docker-compose.yml`, `Dockerfile`), the main entry point (`run.py`), and project documentation.

## Technology Stack

- **Backend**: Flask, PostgreSQL, SQLAlchemy (ORM), Alembic (Migrations), Flask-Smorest (API), Marshmallow (Serialization), JWT (Auth), Socket.IO (Real-time).
- **Frontend**: React, Vite, React Router, Ant Design & Bootstrap (UI), Chart.js (Charts), dnd-kit (Drag and Drop), Socket.IO (Real-time).
- **DevOps**: Docker.

---

## Detailed Directory Analysis

### `/app` - The Static Core Application

This directory contains the foundational Flask application. It defines the "static" or "hard-coded" parts of the system, primarily the core user management and basic business entities that are not meant to be dynamically modified by the end-user through the builder.

#### Key Files in `/app`:

- **`__init__.py`**: Contains the application factory `create_app`. This function is responsible for:
    - Initializing the Flask app.
    - Loading the configuration from `config.py`.
    - Initializing all Flask extensions (like `db`, `jwt`, `migrate`).
    - Registering the API blueprints for the static resources.
    - Defining a basic root endpoint (`/`) and a route to serve uploaded files (`/uploads/...`).

- **`config.py`**: Defines a `Config` class that holds all configuration variables for the application. This includes database URIs, JWT settings, API documentation settings (for Swagger), and mail server settings. It loads sensitive values from environment variables.

- **`extensions.py`**: Follows a common Flask pattern where extension objects (`SQLAlchemy`, `Migrate`, `JWTManager`, `Mail`) are instantiated globally. They are then initialized within the `create_app` factory to avoid circular dependencies.

- **`decorators.py`**: (Content inferred) Likely contains custom decorators, such as `@admin_required`, to protect specific API endpoints and enforce role-based access control (RBAC).

#### Subdirectories in `/app`:

- **`/app/models`**: Contains the SQLAlchemy data models for the static part of the application.
    - **`user.py`**: Defines the `User` model, including columns for email, hashed password, role, and status flags. It includes a `check_password` method for secure authentication.
    - **`party.py`**: (Inferred) Defines parties, which are likely generic entities for customers, suppliers, etc.
    - **`product.py`**: (Inferred) Defines the product catalog.
    - **`sales.py`**: (Inferred) Defines sales-related models like `SalesOrder` and `SalesOrderLine`.

- **`/app/resources`**: Contains the API endpoint definitions using `flask-smorest` Blueprints. Each file typically corresponds to a model.
    - **`user.py`**: Defines all API endpoints for user management, including registration, login, profile updates, and admin-only CRUD operations. It uses `MethodView` classes and schemas for validation and serialization.

- **`/app/schemas.py`**: Contains all the Marshmallow schemas used for serialization (Python objects to JSON) and deserialization (JSON to Python objects). These schemas are used by `flask-smorest` in the resource files to validate incoming data and format outgoing responses. This enforces a strict data contract for the API.

### `/backend` - The Dynamic Low-Code Engine

This is the most innovative part of the project. It contains the logic for the "Low-Code Builder," which allows users to define, create, and interact with custom data models through the UI.

#### Core Concepts:

1.  **Metadata-Driven:** The engine works by storing the definition of applications (models, fields, relations) in its own set of database tables (`sys_models`, `sys_fields`).
2.  **DDL Generation:** It can translate this metadata into Data Definition Language (DDL) SQL commands (`CREATE TABLE`, `ALTER TABLE`) to physically create or modify tables within a project-specific database schema.
3.  **Runtime API:** It provides a generic, dynamic REST API that can perform full CRUD operations on the data within these user-created tables, all by interpreting the metadata at runtime.

#### Key Files in `/backend`:

- **`models.py`**: Defines the SQLAlchemy models that form the schema for the builder itself.
    - **`Project`**: The top-level container for a user-created application. It's the foundation for multi-tenancy, as each project gets its own PostgreSQL schema.
    - **`SysModel`**: Represents the definition of a dynamic table. It belongs to a `Project`.
    - **`SysField`**: Represents the definition of a column within a `SysModel`. This model contains fields for advanced features like `formula`, `summary_expression`, and `validation_regex`.
    - **`AuditLog`**: A crucial model for tracking all significant changes in the system.
    - ***Note***: This file also contains duplicate definitions for `User`, `Party`, `Product`, etc. This is a major violation of the DRY principle and needs to be resolved. The definitions here appear to be the more current and complete ones.

- **`projects.py`**: Contains the API blueprint for managing `Project` entities.
    - It handles CRUD for projects, including managing project members.
    - **Crucially**, it executes `CREATE SCHEMA` when a project is created and `DROP SCHEMA ... CASCADE` when one is deleted, managing the data isolation layer.
    - It also contains the powerful **Import/Export** API endpoints that allow an entire project's architecture to be exported to and imported from a JSON "blueprint" file.

- **`builder.py`**: The "compiler" part of the engine. This blueprint manages the `SysModel` and `SysField` metadata.
    - It provides CRUD APIs for defining the dynamic models and fields.
    - It contains the key endpoint **`/sys-models/<id>/generate-table`**, which triggers the schema synchronization logic. This compares the model definition with the live database and generates/executes `ALTER TABLE` statements.
    - It includes a safety-focused **`/reset-table`** endpoint (admin-only) that first backs up table data to a CSV before dropping and recreating the table.

- **`dynamic_api.py`**: The "runtime" part of the engine. This is a single, powerful blueprint that provides a generic REST API for the data in the user-created tables.
    - The API is accessed via `/projects/<project_id>/data/<model_name>`.
    - It dynamically reflects the target table using SQLAlchemy.
    - It enforces permissions based on the `SysModel`'s ACL definition.
    - It performs complex, dynamic queries that can handle relations (`JOIN`), lookups, summaries (subqueries), full-text search, and sorting.
    - It processes the results into nested JSON and evaluates `formula` fields on the fly.
    - It handles data validation, file uploads, and nested writes (for master-detail forms).

- **`utils.py`**: The engine room. Contains the helper functions that make the builder possible.
    - **`generate_schema_diff_sql`**: The most critical function. It uses SQLAlchemy's `inspect` feature to compare a `SysModel`'s definition to the live database and generate the necessary `ALTER TABLE` SQL commands to synchronize them.
    - **`generate_create_table_sql`**: Generates `CREATE TABLE` statements from metadata.
    - **`get_table_object`**: Reflects a live database table into a SQLAlchemy `Table` object for use in dynamic queries.
    - Other helpers for pagination, serialization, and auditing.

### `/frontend` - The Dynamic React UI

The frontend is a modern Single Page Application (SPA) built with React and Vite. It is completely decoupled from the backend and interacts with it exclusively through the REST APIs.

#### Key Files and Structure:

- **`src/main.jsx`**: The application's entry point. It sets up the root of the React application and wraps the main `<App />` component with global context providers:
    - **`AuthProvider`**: Manages user authentication state (JWT, user data) across the app.
    - **`NotificationProvider`**: Provides a global system for displaying notifications.
    - **`ErrorBoundary`**: Catches rendering errors to prevent the entire app from crashing.

- **`src/App.jsx`**: Defines the application's entire routing structure using `react-router-dom`.
    - It implements `PublicRoute` and `ProtectedRoute` wrapper components to handle authentication and role-based access control (RBAC) for different pages.
    - It defines a clear, project-centric routing structure, with most user-facing pages nested under `/projects/:projectId`.
    - It uses a `ProjectLayout` component to provide a consistent sidebar/navigation experience when inside a project.

- **`src/pages/DynamicModelPage.jsx`**: This component acts as a "translator" or "controller" for the dynamic pages.
    - It fetches the `SysModel` metadata from the `/meta` API endpoint.
    - It translates this metadata into configuration props (`columns`, `formFields`, `kanbanConfig`) suitable for the generic UI components.
    - It handles the complexity of fetching nested metadata for master-detail (`lines`) fields.

- **`src/components/GenericCrudPage.jsx`**: This is the powerhouse of the frontend UI. It is a single, reusable component that provides a complete CRUD interface.
    - It uses a custom hook, **`useCrudData`**, to handle all API interactions (fetching, creating, updating, deleting), cleanly separating data logic from UI presentation.
    - It renders data in multiple formats: a `DataTable`, a card grid, and a `KanbanView`.
    - It provides a feature-rich interface with searching, sorting, pagination, date filters, bulk actions, cloning, and CSV import/export.
    - Its core feature is a highly dynamic modal form that is generated from the `formFields` prop. The form supports client-side validation, conditional field visibility/requirements, cascading selects, file uploads, and real-time evaluation of calculated fields.

- **`src/hooks/useCrudData.js`**: (Inferred) A custom React hook that encapsulates all the logic for communicating with a CRUD API endpoint. It likely manages the state for data, loading, errors, pagination, sorting, and filtering, and exposes functions to `create`, `update`, and `delete` items. This is a key part of making the `GenericCrudPage` clean and reusable.
