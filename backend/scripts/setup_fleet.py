#!/usr/bin/env python3
"""Script to create the fleet_management project via API calls."""

import json
import sys
import requests

BASE = "http://localhost:5000/api/v1"

def main():
    s = requests.Session()

    # 1. Login
    print("=== Login ===")
    r = s.post(f"{BASE}/auth/login", json={
        "email": "admin@erpseed.it",
        "password": "admin123"
    })
    if not r.ok:
        print(f"Login failed: {r.status_code} {r.text}")
        sys.exit(1)
    token = r.json().get("access_token")
    if not token:
        # sometimes it's nested
        token = r.json().get("data", {}).get("access_token")
    s.headers.update({"Authorization": f"Bearer {token}"})
    print("Login OK")

    # 2. Create project
    print("=== Create Project ===")
    r = s.post(f"{BASE}/projects", json={
        "name": "fleet_management",
        "title": "Fleet Management",
        "description": "Gestione flotta veicoli aziendali"
    })
    if r.status_code == 409:
        print("Project already exists")
        # get project id
        r2 = s.get(f"{BASE}/projects")
        projects = r2.json()
        if isinstance(projects, dict):
            projects = projects.get("data", [])
        project_id = None
        for p in projects:
            if p.get("name") == "fleet_management":
                project_id = p["id"]
                break
        print(f"Using existing project id={project_id}")
    elif r.ok:
        data = r.json()
        if isinstance(data, dict):
            project_id = data.get("id") or data.get("data", {}).get("id")
        else:
            project_id = data["id"]
        print(f"Project created id={project_id}")
    else:
        print(f"Create project failed: {r.status_code} {r.text}")
        sys.exit(1)

    if not project_id:
        print("Could not get project id")
        sys.exit(1)

    # 3. Create Vehicle model
    print("=== Create Vehicle model ===")
    r = s.post(f"{BASE}/sys-models", json={
        "projectId": project_id,
        "name": "vehicle",
        "title": "Vehicle"
    })
    if r.status_code == 409:
        print("Vehicle model already exists")
        r2 = s.get(f"{BASE}/sys-models?projectId={project_id}")
        models = r2.json()
        if isinstance(models, dict):
            models = models.get("data", [])
        vehicle_id = None
        for m in models:
            if m.get("name") == "vehicle":
                vehicle_id = m["id"]
                break
    elif r.ok:
        data = r.json()
        vehicle_id = data.get("id") or data.get("data", {}).get("id")
        print(f"Vehicle model created id={vehicle_id}")
    else:
        print(f"Create vehicle model failed: {r.status_code} {r.text}")
        # try to get existing
        r2 = s.get(f"{BASE}/sys-models?projectId={project_id}")
        if r2.ok:
            models = r2.json()
            if isinstance(models, dict):
                models = models.get("data", [])
            for m in models:
                if m.get("name") == "vehicle":
                    vehicle_id = m["id"]
                    break
        if not vehicle_id:
            sys.exit(1)
        print(f"Using existing vehicle model id={vehicle_id}")

    def add_field(model_id, name, field_type, **kwargs):
        print(f"  Adding field '{name}' ({field_type})...")
        data = {"modelId": model_id, "name": name, "type": field_type, **kwargs}
        r = s.post(f"{BASE}/sys-fields", json=data)
        if r.status_code == 409:
            print(f"  Field '{name}' already exists, skipping")
            return
        if not r.ok:
            print(f"  Failed: {r.status_code} {r.text}")
            return
        print(f"  OK")

    # 4. Add fields to Vehicle
    print("=== Add Vehicle fields ===")
    add_field(vehicle_id, "plate", "string", required=True, is_unique=True)
    add_field(vehicle_id, "model", "string", required=True)
    add_field(vehicle_id, "brand", "select",
              options=json.dumps(["Fiat", "Ford", "Tesla", "Volkswagen", "Mercedes", "BMW", "Toyota"]))
    add_field(vehicle_id, "purchase_date", "date")
    add_field(vehicle_id, "mileage", "integer")

    # 5. Generate table for Vehicle
    print("=== Generate Vehicle table ===")
    r = s.post(f"{BASE}/sys-models/{vehicle_id}/generate-table")
    print(f"  {r.status_code}: {r.text}")

    # 6. Create Maintenance model
    print("=== Create Maintenance model ===")
    r = s.post(f"{BASE}/sys-models", json={
        "projectId": project_id,
        "name": "maintenance",
        "title": "Maintenance"
    })
    if r.status_code == 409:
        print("Maintenance model already exists")
        r2 = s.get(f"{BASE}/sys-models?projectId={project_id}")
        models = r2.json()
        if isinstance(models, dict):
            models = models.get("data", [])
        maintenance_id = None
        for m in models:
            if m.get("name") == "maintenance":
                maintenance_id = m["id"]
                break
    elif r.ok:
        data = r.json()
        maintenance_id = data.get("id") or data.get("data", {}).get("id")
        print(f"Maintenance model created id={maintenance_id}")
    else:
        print(f"Create maintenance model failed: {r.status_code} {r.text}")
        r2 = s.get(f"{BASE}/sys-models?projectId={project_id}")
        if r2.ok:
            models = r2.json()
            if isinstance(models, dict):
                models = models.get("data", [])
            for m in models:
                if m.get("name") == "maintenance":
                    maintenance_id = m["id"]
                    break
        if not maintenance_id:
            sys.exit(1)
        print(f"Using existing maintenance model id={maintenance_id}")

    # 7. Add fields to Maintenance
    print("=== Add Maintenance fields ===")
    add_field(maintenance_id, "description", "text")
    add_field(maintenance_id, "date", "date", required=True)
    add_field(maintenance_id, "cost", "decimal")
    add_field(maintenance_id, "vehicle", "relation",
              options=json.dumps({"target_table": "vehicle", "label_field": "plate"}),
              required=True)

    # 8. Generate table for Maintenance
    print("=== Generate Maintenance table ===")
    r = s.post(f"{BASE}/sys-models/{maintenance_id}/generate-table")
    print(f"  {r.status_code}: {r.text}")

    # 9. Add master-detail field to Vehicle
    print("=== Add Master-Detail field to Vehicle ===")
    add_field(vehicle_id, "maintenance_history", "lines",
              options=json.dumps({"target_table": "maintenance", "foreign_key": "vehicle"}))

    # 10. Generate table for Vehicle again
    print("=== Re-generate Vehicle table ===")
    r = s.post(f"{BASE}/sys-models/{vehicle_id}/generate-table")
    print(f"  {r.status_code}: {r.text}")

    print("\n=== DONE ===")
    print(f"Project: {BASE.replace('/api/v1', '')}/projects/{project_id}")
    print("Go to Application to start using the Fleet Management system.")


if __name__ == "__main__":
    main()
