# API Reference - ERPSEED

## Base URL

```
Development: http://localhost:5002
Production: https://api.your-domain.com
```

## Autenticazione

Tutti gli endpoint (eccetto `/auth/*`) richiedono JWT Bearer token:

```
Authorization: Bearer <access_token>
```

### Headers Richiesti

| Header | Valore | Note |
|--------|--------|------|
| `Authorization` | `Bearer <token>` | Obbligatorio |
| `Content-Type` | `application/json` | Per POST/PUT |
| `X-Tenant-ID` | `tenant_id` | Obbligatorio per multi-tenant |

---

## Autenticazione (`/api/v1/auth`)

### Register - Creazione Account

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "admin@company.com",
  "password": "SecurePass123!",
  "first_name": "Mario",
  "last_name": "Rossi",
  "tenant_name": "Azienda Demo",
  "tenant_slug": "demo"
}
```

**Risposta (201):**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "user": {
    "id": 1,
    "email": "admin@company.com",
    "first_name": "Mario",
    "last_name": "Rossi",
    "tenant_id": 1
  },
  "tenant": {
    "id": 1,
    "name": "Azienda Demo",
    "slug": "demo"
  }
}
```

### Login

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "admin@company.com",
  "password": "SecurePass123!"
}
```

### Refresh Token

```http
POST /api/v1/auth/refresh
Authorization: Bearer <refresh_token>
```

### User Info

```http
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

### Change Password

```http
PUT /api/v1/auth/me/password
Authorization: Bearer <access_token>

{
  "current_password": "OldPass",
  "new_password": "NewPass123!"
}
```

### Password Reset Request

```http
POST /api/v1/auth/password/reset

{
  "email": "user@example.com"
}
```

---

## Users (`/users`)

### List Users

```http
GET /users?page=1&per_page=20
Authorization: Bearer <token>
```

**Headers Risposta:**
```
X-Total-Count: 45
X-Pages: 3
X-Current-Page: 1
X-Per-Page: 20
```

### Get User

```http
GET /users/{id}
Authorization: Bearer <token>
```

### Create User

```http
POST /users
Authorization: Bearer <token>

{
  "email": "newuser@company.com",
  "first_name": "Luca",
  "last_name": "Verdi",
  "role": "operator",
  "password": "TempPass123"
}
```

### Update User

```http
PUT /users/{id}
Authorization: Bearer <token>

{
  "first_name": "Marco",
  "role": "admin"
}
```

### Delete User

```http
DELETE /users/{id}
Authorization: Bearer <token>
```

---

## Projects (`/projects`)

### List Projects

```http
GET /projects
Authorization: Bearer <token>
```

### Get Project

```http
GET /projects/{id}
Authorization: Bearer <token>
```

### Create Project

```http
POST /projects
Authorization: Bearer <token>

{
  "name": "My Project",
  "description": "Project description"
}
```

### Update Project

```http
PUT /projects/{id}
Authorization: Bearer <token>

{
  "name": "Updated Name"
}
```

### Project Models

```http
GET /projects/{id}/models
POST /projects/{id}/models
```

### Project Members

```http
GET /projects/{id}/members
POST /projects/{id}/members
```

---

## Dynamic API (`/projects/{project_id}/data/{model_name}`)

API per gestire i modelli creati dinamicamente con il Builder.

### List Records

```http
GET /projects/{project_id}/data/{model_name}?page=1&per_page=20&sort=created_at&order=desc
Authorization: Bearer <token>
```

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `page` | int | 1 | Page number |
| `per_page` | int | 10 | Items per page (max 100) |
| `sort` | string | - | Field to sort by |
| `order` | string | asc | Sort order (asc/desc) |
| `filter[field]` | string | - | Filter by field value |

### Get Record

```http
GET /projects/{project_id}/data/{model_name}/{id}
Authorization: Bearer <token>
```

### Create Record

```http
POST /projects/{project_id}/data/{model_name}
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Record 1",
  "description": "Description",
  "status": "active"
}
```

### Update Record

```http
PUT /projects/{project_id}/data/{model_name}/{id}
Authorization: Bearer <token>

{
  "name": "Updated Name"
}
```

### Delete Record

```http
DELETE /projects/{project_id}/data/{model_name}/{id}
Authorization: Bearer <token>
```

### Bulk Delete

```http
DELETE /projects/{project_id}/data/{model_name}
Authorization: Bearer <token>

{
  "ids": [1, 2, 3, 4, 5]
}
```

### Clone Record

```http
POST /projects/{project_id}/data/{model_name}/{id}/clone
Authorization: Bearer <token>
```

### Import CSV

```http
POST /projects/{project_id}/data/{model_name}/import
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <csv_file>
```

### Model Metadata

```http
GET /projects/{project_id}/data/{model_name}/meta
Authorization: Bearer <token>
```

**Risposta:**
```json
{
  "name": "clients",
  "fields": [
    {"name": "id", "type": "integer", "primary_key": true},
    {"name": "name", "type": "string", "required": true, "max_length": 200},
    {"name": "email", "type": "string", "max_length": 255},
    {"name": "status", "type": "select", "options": ["active", "inactive"]},
    {"name": "created_at", "type": "datetime", "readonly": true}
  ]
}
```

### Audit Logs

```http
GET /projects/{project_id}/audit-logs?page=1&per_page=50
Authorization: Bearer <token>
```

---

## Builder (`/builder`)

### List Archetypes

```http
GET /builder/archetypes
Authorization: Bearer <token>
```

### Create Model (Archetype)

```http
POST /builder/models
Authorization: Bearer <token>

{
  "name": "clients",
  "label": "Clienti",
  "project_id": 1
}
```

### Define Fields

```http
POST /builder/models/{model_id}/fields
Authorization: Bearer <token>

{
  "name": "name",
  "type": "string",
  "label": "Nome Cliente",
  "required": true,
  "max_length": 200
}
```

### Field Types

| Type | Description | Extra Options |
|------|-------------|---------------|
| `string` | Testo semplice | `max_length`, `min_length` |
| `text` | Testo lungo | `max_length` |
| `integer` | Numero intero | `min`, `max` |
| `float` | Numero decimale | `min`, `max` |
| `boolean` | Sì/No | - |
| `date` | Data | - |
| `datetime` | Data e ora | - |
| `select` | Menu a tendina | `options: []` |
| `multiselect` | Menu multiplo | `options: []` |
| `relation` | Relazione | `target_model`, `relation_type` |
| `file` | Upload file | `allowed_extensions: []` |
| `image` | Upload immagine | `max_size_mb` |
| `richtext` | Editor WYSIWYG | - |
| `currency` | Valuta Euro | - |
| `url` | URL web | - |
| `email` | Email | - |
| `phone` | Telefono | - |

### Relation Types

| Type | Description |
|------|-------------|
| `many_to_one` | Più record -> 1 altro record |
| `one_to_many` | 1 record -> Più record |
| `many_to_many` | Più record <-> Più record |

---

## Products (`/products`)

### List Products

```http
GET /products?page=1&per_page=20
Authorization: Bearer <token>
```

### Get Product

```http
GET /products/{id}
Authorization: Bearer <token>
```

### Create Product

```http
POST /products
Authorization: Bearer <token>

{
  "name": "Prodotto Demo",
  "sku": "DEMO-001",
  "price": 99.99,
  "cost": 49.99,
  "tax_rate": 22.0,
  "stock_quantity": 100,
  "description": "Descrizione prodotto"
}
```

### Update Product

```http
PUT /products/{id}
Authorization: Bearer <token>
```

### Delete Product

```http
DELETE /products/{id}
Authorization: Bearer <token>
```

### Product Variants

```http
GET /products/{id}/variants
POST /products/{id}/variants
```

---

## Sales Orders (`/sales-orders`)

### List Orders

```http
GET /sales-orders?status=draft&page=1
Authorization: Bearer <token>
```

### Get Order

```http
GET /sales-orders/{id}
Authorization: Bearer <token>
```

### Create Order

```http
POST /sales-orders
Authorization: Bearer <token>

{
  "customer_id": 1,
  "date": "2024-01-15",
  "lines": [
    {"product_id": 1, "quantity": 2, "unit_price": 99.99},
    {"product_id": 2, "quantity": 1, "unit_price": 49.99}
  ]
}
```

### Update Order

```http
PUT /sales-orders/{id}
Authorization: Bearer <token>
```

### Confirm Order

```http
POST /sales-orders/{id}/confirm
Authorization: Bearer <token>
```

### Cancel Order

```http
POST /sales-orders/{id}/cancel
Authorization: Bearer <token>
```

### Order Status Flow

```
draft → confirmed → shipped → delivered
   ↓
cancelled
```

---

## Webhooks (`/webhooks`)

### List Webhooks

```http
GET /webhooks
Authorization: Bearer <token>
```

### Create Webhook

```http
POST /webhooks
Authorization: Bearer <token>

{
  "name": "Slack Notification",
  "url": "https://hooks.slack.com/...",
  "events": ["order.created", "order.confirmed"],
  "secret": "optional-signing-secret"
}
```

### Update Webhook

```http
PUT /webhooks/{id}
Authorization: Bearer <token>
```

### Delete Webhook

```http
DELETE /webhooks/{id}
Authorization: Bearer <token>
```

### Test Webhook

```http
POST /webhooks/{id}/test
Authorization: Bearer <token>
```

### Regenerate Secret

```http
POST /webhooks/{id}/regenerate-secret
Authorization: Bearer <token>
```

### Webhook Events

| Event | Trigger |
|-------|---------|
| `order.created` | Nuovo ordine creato |
| `order.confirmed` | Ordine confermato |
| `order.cancelled` | Ordine annullato |
| `order.shipped` | Ordine spedito |
| `user.created` | Nuovo utente |
| `project.created` | Nuovo progetto |
| `record.created` | Record creato nel Builder |

### Webhook Payload

```json
{
  "event": "order.created",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "id": 123,
    "customer_id": 1,
    "total": 249.97
  }
}
```

### Signature Verification

```
X-Webhook-Signature: sha256=<hmac>
```

---

## Workflows (`/workflows`)

### List Workflows

```http
GET /workflows
Authorization: Bearer <token>
```

### Get Workflow

```http
GET /workflows/{id}
Authorization: Bearer <token>
```

### Create Workflow

```http
POST /workflows
Authorization: Bearer <token>

{
  "name": "Welcome Email",
  "trigger": {
    "type": "event",
    "event": "user.created"
  },
  "steps": [
    {
      "type": "delay",
      "duration": "1 hour"
    },
    {
      "type": "http_request",
      "method": "POST",
      "url": "https://api.sendgrid.com/send",
      "body": {"to": "{{user.email}}", "template": "welcome"}
    }
  ]
}
```

### Step Types

| Type | Description |
|------|-------------|
| `delay` | Attendi durata specificata |
| `http_request` | Chiamata HTTP |
| `condition` | Branch condizionale |
| `webhook` | Trigger webhook |
| `notification` | Invia notifica email/in-app |

### Execute Workflow

```http
POST /workflows/{id}/execute
Authorization: Bearer <token>

{
  "context": {
    "user_id": 123,
    "order_id": 456
  }
}
```

### Workflow Logs

```http
GET /workflows/{id}/executions
Authorization: Bearer <token>
```

---

## Dashboard (`/dashboard`)

### Get Dashboard

```http
GET /dashboard
Authorization: Bearer <token>
```

### Widget Types

```json
{
  "widgets": [
    {
      "type": "chart",
      "chart_type": "bar",
      "title": "Vendite Mensili",
      "data_source": "orders",
      "x_axis": "month",
      "y_axis": "total"
    },
    {
      "type": "kpi",
      "title": "Ordini Oggi",
      "value": 15,
      "trend": "+10%",
      "icon": "shopping-cart"
    }
  ]
}
```

---

## AI Assistant (`/ai`)

### Chat

```http
POST /ai/chat
Authorization: Bearer <token>

{
  "message": "Show me sales summary for January",
  "context": {
    "project_id": 1
  }
}
```

### Generate Report

```http
POST /ai/generate-report
Authorization: Bearer <token>

{
  "type": "sales_summary",
  "period": "2024-01"
}
```

---

## Errori

### Codici HTTP

| Code | Significato |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 204 | No Content (Delete) |
| 400 | Bad Request (Validation Error) |
| 401 | Unauthorized (Invalid/Missing Token) |
| 403 | Forbidden (No Permission) |
| 404 | Not Found |
| 409 | Conflict (Duplicate) |
| 500 | Internal Server Error |

### Formato Errori

```json
{
  "message": "Validation failed",
  "errors": {
    "email": ["Invalid email format"],
    "password": ["Must be at least 8 characters"]
  }
}
```

### Rate Limiting

```
429 Too Many Requests
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1705320000
```

---

*Swagger UI disponibile su `/swagger-ui`*
