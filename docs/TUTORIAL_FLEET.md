# Tutorial: Building your first project with ERPSeed (Fleet Management)

Welcome to ERPSeed! This tutorial will guide you through creating a complete **Fleet Management** system from scratch.

---

## 📌 In questo tutorial

Puoi seguire il tutorial attraverso due modalità:
1. **[Percorso GUI / Visual Builder](#step-1-create-a-new-project)** — Utilizza l'interfaccia grafica e l'AI Assistant nel browser.
2. **[Percorso CLI / API REST](#prerequisiti-cli)** — Esegui i comandi `curl` direttamente da terminale contro l'API REST.

---

## Prerequisiti

- ERPSeed in esecuzione (Backend su porta 5000, Frontend su porta 5173).
- Utente amministratore registrato.

### Prerequisiti CLI

Se segui il percorso via CLI, ottieni prima il token JWT di autenticazione:

```bash
# Login come admin e salvataggio del token JWT
TOKEN=$(curl -s -X POST http://localhost:5000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@erpseed.org","password":"admin123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token'))")

echo "Token: $TOKEN"
```

---

## Step 1: Create a New Project

### Via GUI
1. Go to the **Projects** page.
2. Click **New Project**.
3. Fill in the details:
   - **Name**: `fleet_management`
   - **Title**: `Fleet Management`
   - **Description**: `System to manage company vehicles and maintenance.`
4. Click **Create**.
5. Select the newly created project to enter the **Project Dashboard**.

### Via CLI
```bash
curl -s -X POST http://localhost:5000/api/v1/projects \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "fleet_management",
    "title": "Fleet Management",
    "description": "System to manage company vehicles and maintenance."
  }'
```
*Annota l'`id` del progetto restituito (es. `1`).*

---

## Step 2: Define your first Model (Vehicle)

### Via GUI - Option A: Using the Visual Builder (Manual)
1. In the Project Dashboard, go to **Models**.
2. Click **New Model**.
3. Fill in **Name**: `vehicle` (lowercase), **Title**: `Vehicle`.
4. Add fields with **Add New Field**:
   - `plate` / `Plate` (String, Required, Unique)
   - `model` / `Model` (String, Required)
   - `brand` / `Brand` (Select — options: Fiat, Ford, Tesla, Volkswagen, Mercedes)
   - `purchase_date` / `Purchase Date` (Date)
   - `mileage` / `Mileage` (Integer)
5. Click **Generate/Update DB Table** to sync schema with the database and publish the model.

### Via GUI - Option B: Using the AI Assistant
1. Open the **AI Assistant** panel.
2. Prompt: `"Create a model for Vehicles with fields: plate (unique), brand, model, purchase date, and mileage."`
3. Review execution plan and click **Apply Changes**.

### Via CLI
```bash
# 1. Crea modello Vehicle (es. projectId = 1)
curl -s -X POST http://localhost:5000/api/v1/sys-models \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{ "projectId": 1, "name": "vehicle", "title": "Vehicle" }'

# Annota l'id del modello Vehicle (es. 1)

# 2. Aggiungi campi al modello Vehicle (modelId = 1)
curl -s -X POST http://localhost:5000/api/v1/sys-fields \
  -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" \
  -d '{ "modelId": 1, "name": "plate", "type": "string", "required": true, "is_unique": true }'

curl -s -X POST http://localhost:5000/api/v1/sys-fields \
  -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" \
  -d '{ "modelId": 1, "name": "model", "type": "string", "required": true }'

curl -s -X POST http://localhost:5000/api/v1/sys-fields \
  -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" \
  -d '{ "modelId": 1, "name": "brand", "type": "select", "options": "[\"Fiat\", \"Ford\", \"Tesla\", \"Volkswagen\", \"Mercedes\"]" }'

curl -s -X POST http://localhost:5000/api/v1/sys-fields \
  -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" \
  -d '{ "modelId": 1, "name": "purchase_date", "type": "date" }'

curl -s -X POST http://localhost:5000/api/v1/sys-fields \
  -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" \
  -d '{ "modelId": 1, "name": "mileage", "type": "integer" }'

# 3. Sincronizza tabella DB per Vehicle
curl -s -X POST http://localhost:5000/api/v1/sys-models/1/generate-table \
  -H "Authorization: Bearer $TOKEN"
```

---

## Step 3: Create a Maintenance Model (Relational Data)

### Via GUI
1. Create new model: `maintenance` / `Maintenance`.
2. Add fields:
   - `description` / `Description` (Text)
   - `date` / `Date` (Date, Required)
   - `cost` / `Cost` (Decimal/Currency)
3. Add a **Relation** field to link Vehicle:
   - **Field Name**: `vehicle`
   - **Type**: `Relation`
   - **Target Table**: `vehicle`
   - **Label Field**: `plate`
   - **Required**: checked
4. Save fields and click **Generate Table**.

### Via CLI
```bash
# 1. Crea modello Maintenance (projectId = 1)
curl -s -X POST http://localhost:5000/api/v1/sys-models \
  -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" \
  -d '{ "projectId": 1, "name": "maintenance", "title": "Maintenance" }'

# Annota l'id del modello Maintenance (es. 2)

# 2. Aggiungi campi (modelId = 2)
curl -s -X POST http://localhost:5000/api/v1/sys-fields \
  -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" \
  -d '{ "modelId": 2, "name": "description", "type": "text" }'

curl -s -X POST http://localhost:5000/api/v1/sys-fields \
  -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" \
  -d '{ "modelId": 2, "name": "date", "type": "date", "required": true }'

curl -s -X POST http://localhost:5000/api/v1/sys-fields \
  -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" \
  -d '{ "modelId": 2, "name": "cost", "type": "decimal" }'

curl -s -X POST http://localhost:5000/api/v1/sys-fields \
  -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" \
  -d '{ "modelId": 2, "name": "vehicle", "type": "relation", "required": true, "options": "{\"target_table\": \"vehicle\", \"label_field\": \"plate\"}" }'

# 3. Genera tabella Maintenance
curl -s -X POST http://localhost:5000/api/v1/sys-models/2/generate-table \
  -H "Authorization: Bearer $TOKEN"
```

---

## Step 3b: Aggiungere un campo Lines (Master-Detail) su Vehicle

### Via GUI
1. Go to **Models → Vehicle**.
2. Click **Add New Field**:
   - **Field Name**: `maintenance_history`
   - **Type**: `Master-Detail` (`lines`)
   - **Target Table**: `maintenance`
   - **Foreign Key Field**: `vehicle`
3. Click **Save Field**, then **Generate Table**.

### Via CLI
```bash
curl -s -X POST http://localhost:5000/api/v1/sys-fields \
  -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" \
  -d '{
    "modelId": 1,
    "name": "maintenance_history",
    "type": "lines",
    "options": "{\"target_table\": \"maintenance\", \"foreign_key\": \"vehicle\"}"
  }'

# Rigenera tabella Vehicle
curl -s -X POST http://localhost:5000/api/v1/sys-models/1/generate-table \
  -H "Authorization: Bearer $TOKEN"
```

---

## Step 3c: Aggiungere un campo Lookup su Maintenance (evitare la duplicazione dei dati)

Obiettivo: mostrare che invece di ri-digitare la targa del veicolo su ogni riga di manutenzione, si "pesca" automaticamente da `vehicle.plate` tramite il campo `relation` già creato allo Step 3.

### Via GUI
1. Vai su **Models → Maintenance**.
2. Click **Add New Field**.
3. Compila:
   - **Field Name**: `vehicle_plate`
   - **Type**: `Lookup`
   - **Target Table**: `vehicle`
   - **Local Relation Field** (`local_key`): `vehicle`
   - **Field to Display** (`remote_field`): `plate`
4. Salva e rigenera la tabella.
5. Il campo `vehicle_plate` apparirà **in sola lettura** nelle liste e nel form di Maintenance, sempre allineato al veicolo collegato, senza occupare una colonna fisica duplicata nel database.

### Via CLI
```bash
curl -s -X POST http://localhost:5000/api/v1/sys-fields \
  -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" \
  -d '{
    "modelId": 2,
    "name": "vehicle_plate",
    "type": "lookup",
    "title": "Targa Veicolo",
    "ui_readonly": true,
    "options": "{\"target_table\": \"vehicle\", \"local_key\": \"vehicle\", \"remote_key\": \"id\", \"remote_field\": \"plate\"}"
  }'
```

**Verifica:**
```bash
curl -s "http://localhost:5000/api/v1/projects/1/data/maintenance" -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
# Ogni riga di manutenzione conterrà "vehicle_plate": "AB123CD" senza che il campo sia stato scritto manualmente.
```

---

## Step 3d: Aggiungere un campo Summary su Vehicle (totale spese di manutenzione)

Obiettivo: mostrare l'aggregazione dei record figli, complementare al Master-Detail dello Step 3b.

### Via GUI
1. Vai su **Models → Vehicle**.
2. Click **Add New Field**.
3. Compila:
   - **Field Name**: `total_maintenance_cost`
   - **Type**: `Summary`
   - **Target Table**: `maintenance`
   - **Foreign Key Field**: `vehicle`
   - **Aggregation Function**: `SUM`
   - **Column**: `cost`
4. Salva, verifica che il campo generato (`summary_expression`) sia `SUM(cost)`, poi rigenera la tabella.

### Via CLI
```bash
curl -s -X POST http://localhost:5000/api/v1/sys-fields \
  -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" \
  -d '{
    "modelId": 1,
    "name": "total_maintenance_cost",
    "type": "summary",
    "title": "Totale Spese Manutenzione",
    "summary_expression": "SUM(cost)",
    "options": "{\"target_table\": \"maintenance\", \"foreign_key\": \"vehicle\"}"
  }'
```

**Verifica:**
```bash
curl -s "http://localhost:5000/api/v1/projects/1/data/vehicle/1" -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
# Conterrà "total_maintenance_cost": 120.5 dopo l'inserimento della manutenzione dello Step 4.
```

---

## Step 4: Test your Application (Data CRUD)

### Via GUI
1. Open **Application** view.
2. Select **Vehicle** and add a record:
   - Plate: `AB123CD`, Brand: `Ford`, Model: `Transit`, Purchase Date: `2023-06-15`, Mileage: `15000`.
3. Open **Maintenance** or add maintenance history directly inside the Vehicle form inline lines table.

### Via CLI
```bash
# Inserimento veicolo (projectId = 1)
curl -s -X POST "http://localhost:5000/api/v1/projects/1/data/vehicle" \
  -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" \
  -d '{
    "plate": "AB123CD",
    "brand": "Ford",
    "model": "Transit",
    "purchase_date": "2023-06-15",
    "mileage": 15000
  }'

# Inserimento manutenzione collegata al veicolo (ID veicolo = 1)
curl -s -X POST "http://localhost:5000/api/v1/projects/1/data/maintenance" \
  -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" \
  -d '{
    "description": "Cambio olio",
    "date": "2024-04-15",
    "cost": 120.5,
    "vehicle": 1
  }'

# Lista veicoli
curl -s "http://localhost:5000/api/v1/projects/1/data/vehicle" \
  -H "Authorization: Bearer $TOKEN"

# Dettaglio veicolo con manutenzioni collegate
curl -s "http://localhost:5000/api/v1/projects/1/data/vehicle/1" \
  -H "Authorization: Bearer $TOKEN"

# Aggiornamento veicolo
curl -s -X PUT "http://localhost:5000/api/v1/projects/1/data/vehicle/1" \
  -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" \
  -d '{"mileage": 16000}'

# Eliminazione veicolo
curl -s -X DELETE "http://localhost:5000/api/v1/projects/1/data/vehicle/1" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Step 5: Add Automation (Optional)

1. Go to **Workflows**.
2. Create **New Workflow**: `High Maintenance Alert`.
3. **Trigger**: `On Record Created` for model `maintenance`.
4. **Condition**: `{{record.cost}} > 1000`.
5. **Action**: `Send Email` or `System Notification`.
6. Save and Enable.

---

## Summary

Complimenti! Hai creato un'applicazione relazionale completa con supporto GUI e CLI per la gestione della flotta aziendale.

### Confronto dei Tipi Relazionali

| Tipo campo | Dove si mette | Cosa fa | Scrive dati fisici? |
|---|---|---|---|
| `relation` | Sul modello "figlio"/dettaglio | Crea la FK verso il record padre | Sì (colonna INTEGER con FK) |
| `lookup` | Sul modello che ha già un `relation` | Mostra un campo del record collegato (sola lettura) | No |
| `summary` | Sul modello "padre" | Aggrega (SUM/COUNT/AVG/MIN/MAX) i record figli | No |
| `lines` | Sul modello "padre" | Mostra/gestisce inline la lista dei record figli (Master-Detail) | No (usa la FK del figlio) |

### Risorse utili:
- [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) per personalizzazioni lato codice.
- [GETTING_STARTED.md](GETTING_STARTED.md) per opzioni di deploy e configurazione ambiente.

---

*Per la cronologia completa delle modifiche di questo documento, consulta la cronologia Git del repository.*
