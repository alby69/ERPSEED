# API Reference - ERPSEED

## Base URL

```
Development: http://localhost:5000
API Version: v1
Prefix: /api/v1
```

## Autenticazione

Quasi tutti gli endpoint richiedono un JWT Bearer token:

```
Authorization: Bearer <access_token>
```

### Headers Richiesti

| Header | Valore | Note |
|--------|--------|------|
| `Authorization` | `Bearer <token>` | Obbligatorio |
| `Content-Type` | `application/json` | Per POST/PUT |
| `X-Tenant-ID` | `tenant_id` | Obbligatorio per operazioni multi-tenant |

---

## Moduli API (`/api/v1/`)

Tutte le rotte sono ora centralizzate e standardizzate.

### 1. Autenticazione (`/auth`)
- `POST /login`: Autenticazione utente.
- `POST /register`: Registrazione nuovo utente e tenant.
- `POST /refresh`: Refresh del token JWT.
- `GET /me`: Informazioni sull'utente corrente.

### 2. Utenti (`/users`)
- `GET /users`: Lista utenti (Admin).
- `GET /users/{id}`: Dettagli utente.
- `POST /register`: Shortcut per registrazione (Admin).
- `PUT /users/{id}`: Aggiornamento utente.
- `DELETE /users/{id}`: Eliminazione utente.

### 3. Progetti (`/projects`)
- `GET /projects`: Lista progetti accessibili.
- `POST /projects`: Creazione nuovo progetto.
- `GET /projects/{id}/models`: Lista modelli dinamici del progetto.
- `GET /projects/{id}/members`: Membri del progetto.

### 4. Builder (`/builder`)
- `GET /builder/archetypes`: Lista archetipi di sistema.
- `POST /builder/models`: Creazione modello dinamico.
- `POST /builder/models/{id}/fields`: Definizione campi.
- `GET /builder/blocks/{id}`: Dettagli blocco UI.

### 5. AI Assistant (`/ai`)
- `POST /ai/generate`: Genera configurazione ERP da linguaggio naturale.
- `POST /ai/apply`: Applica la configurazione generata.
- `GET /ai/conversations`: Storico conversazioni.

### 6. Dynamic API (`/dynamic`)
Gestisce i dati per i modelli creati con il Builder.
- `GET /dynamic/projects/{pid}/data/{model}`: Lista record.
- `POST /dynamic/projects/{pid}/data/{model}`: Nuovo record.
- `PUT /dynamic/projects/{pid}/data/{model}/{id}`: Aggiorna record.
- `DELETE /dynamic/projects/{pid}/data/{model}/{id}`: Elimina record.

### 7. Prodotti, Vendite, Acquisti (`/products`, `/sales`, `/purchases`)
Endpoint standard per i moduli core dell'ERP, ora migrati a Command Handler.

### 8. Analytics (`/analytics`, `/dashboards`)
- `GET /analytics/chart-data/{id}`: Recupera dati aggregati (Usa il Read Model JSONB se disponibile).
- `GET /dashboards/sys-dashboards`: Lista dashboard.

---

## Paginazione e Filtri

Tutte le API che restituiscono liste supportano:
- `page`: Numero pagina (default 1).
- `per_page`: Record per pagina (default 10).
- `q`: Ricerca testuale globale.
- `sort_by`: Campo per ordinamento.
- `sort_order`: `asc` o `desc`.

**Headers di Risposta:**
- `X-Total-Count`: Numero totale record.
- `X-Pages`: Numero totale pagine.
- `Content-Range`: Range dei record restituiti.

---

## Errori

Il sistema restituisce risposte JSON standard per gli errori:

```json
{
  "code": 404,
  "name": "Not Found",
  "description": "Risorsa non trovata"
}
```

---

*La documentazione interattiva completa è disponibile su `/swagger-ui` dopo l'avvio del server.*
