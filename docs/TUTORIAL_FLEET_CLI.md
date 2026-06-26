# Tutorial Fleet Management da CLI

Questo tutorial mostra come creare il progetto **Fleet Management** interamente via riga di comando usando `curl` contro l'API REST sulla porta 5000.

## Prerequisiti

- ERPSeed in esecuzione (backend su `http://localhost:5000`)
- `curl` e `jq` installati (opzionale: `python3` per parsing JSON)

## 1. Login e ottenimento token JWT

```bash
# Login come admin
TOKEN=$(curl -s -X POST http://localhost:5000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@erpseed.it","password":"admin123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token'))")

echo "Token: $TOKEN"
```

Salva il token in una variabile — va usato in tutte le chiamate successive come header `Authorization: Bearer $TOKEN`.

## 2. Creare un progetto

```bash
curl -s -X POST http://localhost:5000/api/v1/projects \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "fleet_management",
    "title": "Fleet Management",
    "description": "Gestione flotta veicoli aziendali"
  }'
```

Risposta (progetto creato):
```json
{
  "id": 1,
  "name": "fleet_management",
  "title": "Fleet Management",
  ...
}
```

Annota l'`id` del progetto (es. `1`).

## 3. Creare un modello (Vehicle)

```bash
curl -s -X POST http://localhost:5000/api/v1/sys-models \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "projectId": 1,
    "name": "vehicle",
    "title": "Vehicle"
  }'
```

Risposta (estratto):
```json
{ "id": 1, "name": "vehicle", ... }
```

Annota l'`id` del modello (es. `1`).

## 4. Aggiungere campi a un modello

```bash
# Stringa (plate, required, unique)
curl -s -X POST http://localhost:5000/api/v1/sys-fields \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "modelId": 1,
    "name": "plate",
    "type": "string",
    "required": true,
    "is_unique": true
  }'

# Stringa (model, required)
curl -s -X POST http://localhost:5000/api/v1/sys-fields \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "modelId": 1,
    "name": "model",
    "type": "string",
    "required": true
  }'

# Select (brand)
curl -s -X POST http://localhost:5000/api/v1/sys-fields \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "modelId": 1,
    "name": "brand",
    "type": "select",
    "options": "[\"Fiat\", \"Ford\", \"Tesla\", \"Volkswagen\", \"Mercedes\"]"
  }'

# Date (purchase_date)
curl -s -X POST http://localhost:5000/api/v1/sys-fields \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "modelId": 1,
    "name": "purchase_date",
    "type": "date"
  }'

# Integer (mileage)
curl -s -X POST http://localhost:5000/api/v1/sys-fields \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "modelId": 1,
    "name": "mileage",
    "type": "integer"
  }'
```

## 5. Generare la tabella DB (Vehicle)

```bash
curl -s -X POST http://localhost:5000/api/v1/sys-models/1/generate-table \
  -H "Authorization: Bearer $TOKEN"
```

Risposta: `{ "message": "Schema synced successfully." }`

## 6. Creare il modello Maintenance

```bash
curl -s -X POST http://localhost:5000/api/v1/sys-models \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "projectId": 1,
    "name": "maintenance",
    "title": "Maintenance"
  }'
```

Annota l'`id` del modello (es. `2`).

## 7. Aggiungere campi a Maintenance

```bash
# Text (description)
curl -s -X POST http://localhost:5000/api/v1/sys-fields \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "modelId": 2,
    "name": "description",
    "type": "text"
  }'

# Date (date, required)
curl -s -X POST http://localhost:5000/api/v1/sys-fields \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "modelId": 2,
    "name": "date",
    "type": "date",
    "required": true
  }'

# Numeric (cost) — usa type "decimal"
curl -s -X POST http://localhost:5000/api/v1/sys-fields \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "modelId": 2,
    "name": "cost",
    "type": "decimal"
  }'

# Relazione (vehicle → Vehicle)
curl -s -X POST http://localhost:5000/api/v1/sys-fields \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "modelId": 2,
    "name": "vehicle",
    "type": "relation",
    "required": true,
    "options": "{\"target_table\": \"vehicle\", \"label_field\": \"plate\"}"
  }'
```

## 8. Generare la tabella DB (Maintenance)

```bash
curl -s -X POST http://localhost:5000/api/v1/sys-models/2/generate-table \
  -H "Authorization: Bearer $TOKEN"
```

## 9. Aggiungere campo Master-Detail (lines) su Vehicle

```bash
curl -s -X POST http://localhost:5000/api/v1/sys-fields \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "modelId": 1,
    "name": "maintenance_history",
    "type": "lines",
    "options": "{\"target_table\": \"maintenance\", \"foreign_key\": \"vehicle\"}"
  }'

# Rigenera la tabella di Vehicle (per sincronizzare)
curl -s -X POST http://localhost:5000/api/v1/sys-models/1/generate-table \
  -H "Authorization: Bearer $TOKEN"
```

## 10. CRUD sulle entità dinamiche

### Inserire un veicolo

```bash
curl -s -X POST "http://localhost:5000/api/v1/projects/1/data/vehicle" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "plate": "AB123CD",
    "brand": "Ford",
    "model": "Transit",
    "purchase_date": "2023-06-15",
    "mileage": 15000
  }'
```

### Inserire una manutenzione

```bash
curl -s -X POST "http://localhost:5000/api/v1/projects/1/data/maintenance" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "description": "Cambio olio",
    "date": "2024-04-15",
    "cost": 120.5,
    "vehicle": 1
  }'
```

Il campo `vehicle` riceve l'**ID numerico** del record Vehicle (non la targa).

### Listare tutti i veicoli

```bash
curl -s "http://localhost:5000/api/v1/projects/1/data/vehicle" \
  -H "Authorization: Bearer $TOKEN" | jq
```

### Ottenere un singolo veicolo (con manutenzioni collegate)

```bash
curl -s "http://localhost:5000/api/v1/projects/1/data/vehicle/1" \
  -H "Authorization: Bearer $TOKEN" | jq
```

### Aggiornare un veicolo

```bash
curl -s -X PUT "http://localhost:5000/api/v1/projects/1/data/vehicle/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"mileage": 16000}'
```

### Eliminare un veicolo

```bash
curl -s -X DELETE "http://localhost:5000/api/v1/projects/1/data/vehicle/1" \
  -H "Authorization: Bearer $TOKEN"
```

## Riepilogo dei comandi

| Azione | Metodo | Endpoint |
|--------|--------|----------|
| Login | `POST` | `/api/v1/auth/login` |
| Crea progetto | `POST` | `/api/v1/projects` |
| Crea modello | `POST` | `/api/v1/sys-models` |
| Aggiungi campo | `POST` | `/api/v1/sys-fields` |
| Genera tabella | `POST` | `/api/v1/sys-models/{id}/generate-table` |
| Crea record | `POST` | `/api/v1/projects/{pid}/data/{model}` |
| Lista record | `GET` | `/api/v1/projects/{pid}/data/{model}` |
| Dettaglio record | `GET` | `/api/v1/projects/{pid}/data/{model}/{id}` |
| Modifica record | `PUT` | `/api/v1/projects/{pid}/data/{model}/{id}` |
| Elimina record | `DELETE` | `/api/v1/projects/{pid}/data/{model}/{id}` |
