"""Test per il modulo Project Management.

Verifica CRUD BusinessProject, Timesheet con righe,
e transizioni di stato submit/approve.
Crea i dati necessari (clienti/dipendenti) via API entities.
"""


def _create_soggetto(client, auth_headers, tipo="persona_giuridica", nome=None, cognome=None, ragione_sociale=None):
    payload = {
        "tipo_soggetto": tipo,
        "nome": nome or ("Dipendente" if tipo == "persona_fisica" else "Cliente"),
    }
    if tipo == "persona_fisica":
        payload.update({
            "cognome": cognome or "Rossi",
            "codice_fiscale": "RSSMRA85M01H501Z",
        })
    else:
        payload.update({
            "ragione_sociale": ragione_sociale or "Cliente Test Srl",
            "codice_fiscale": "CLNTST85M01H501Z",
            "partita_iva": "01234567890",
        })
    resp = client.post("/api/v1/soggetti", json=payload, headers=auth_headers)
    assert resp.status_code == 201, f"Soggetto creation failed: {resp.get_json()}"
    return resp.get_json()


# ========== Projects ==========

def test_create_project(client, auth_headers):
    client_data = _create_soggetto(client, auth_headers)
    payload = {
        "code": "PROJ-001",
        "name": "Progetto Test",
        "description": "Descrizione progetto di prova",
        "client_id": client_data["id"],
        "status": "active",
        "estimated_hours": 100,
        "budget_amount": 5000.0,
    }
    resp = client.post("/api/v1/project-management/projects", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["code"] == "PROJ-001"
    assert data["status"] == "active"
    return data


def test_list_projects(client, auth_headers):
    _create_project(client, auth_headers)
    resp = client.get("/api/v1/project-management/projects", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.get_json()) >= 1


def test_get_project(client, auth_headers):
    proj = _create_project(client, auth_headers)
    resp = client.get(f"/api/v1/project-management/projects/{proj['id']}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["id"] == proj["id"]


def test_update_project(client, auth_headers):
    proj = _create_project(client, auth_headers)
    resp = client.put(f"/api/v1/project-management/projects/{proj['id']}", json={"name": "Progetto Modificato"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "Progetto Modificato"


def test_delete_project(client, auth_headers):
    proj = _create_project(client, auth_headers)
    resp = client.delete(f"/api/v1/project-management/projects/{proj['id']}", headers=auth_headers)
    assert resp.status_code == 204


# ========== Timesheets ==========

def test_create_timesheet(client, auth_headers):
    employee = _create_soggetto(client, auth_headers, tipo="persona_fisica")
    proj = _create_project(client, auth_headers)
    payload = {
        "employee_id": employee["id"],
        "date": "2026-06-10",
        "notes": "Timesheet settimanale",
        "lines": [
            {"project_id": proj["id"], "hours": 8, "description": "Analisi requisiti"},
            {"project_id": proj["id"], "hours": 4, "description": "Implementazione"},
        ],
    }
    resp = client.post("/api/v1/project-management/timesheets", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["status"] == "draft"
    assert len(data["lines"]) == 2


def test_timesheet_submit_approve(client, auth_headers):
    ts = _create_timesheet(client, auth_headers)
    ts_id = ts["id"]

    resp = client.post(f"/api/v1/project-management/timesheets/{ts_id}/submit", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "submitted"

    resp = client.post(f"/api/v1/project-management/timesheets/{ts_id}/approve", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "approved"


def test_list_timesheets(client, auth_headers):
    _create_timesheet(client, auth_headers)
    resp = client.get("/api/v1/project-management/timesheets", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.get_json()) >= 1


def test_get_timesheet(client, auth_headers):
    ts = _create_timesheet(client, auth_headers)
    resp = client.get(f"/api/v1/project-management/timesheets/{ts['id']}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["id"] == ts["id"]


def test_project_summary(client, auth_headers):
    resp = client.get("/api/v1/project-management/summary", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert "total_projects" in data
    assert "total_budget" in data


# ========== Helpers ==========

def _create_project(client, auth_headers):
    client_data = _create_soggetto(client, auth_headers)
    resp = client.post("/api/v1/project-management/projects", json={
        "code": "PROJ-TEST", "name": "Progetto Test", "client_id": client_data["id"],
        "status": "active", "estimated_hours": 100, "budget_amount": 5000.0,
    }, headers=auth_headers)
    assert resp.status_code == 201
    return resp.get_json()


def _create_timesheet(client, auth_headers):
    employee = _create_soggetto(client, auth_headers, tipo="persona_fisica")
    proj = _create_project(client, auth_headers)
    resp = client.post("/api/v1/project-management/timesheets", json={
        "employee_id": employee["id"], "date": "2026-06-10",
        "lines": [{"project_id": proj["id"], "hours": 8}],
    }, headers=auth_headers)
    assert resp.status_code == 201
    return resp.get_json()
