"""Test per Progetti e Modelli Dinamici (pre-esistente, aggiornato)."""
from backend.extensions import db
from backend.models import SysModel


def test_project_crud(client, auth_headers):
    resp = client.post("/api/v1/projects", json={
        "name": "test_project",
        "title": "Test Project",
        "description": "Description",
    }, headers=auth_headers)
    assert resp.status_code == 201
    project_id = resp.get_json()["id"]

    resp = client.get("/api/v1/projects", headers=auth_headers)
    assert resp.status_code == 200
    assert any(p["id"] == project_id for p in resp.get_json())

    resp = client.get(f"/api/v1/projects/{project_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "test_project"


def test_dynamic_model_creation(client, auth_headers, app):
    resp = client.post("/api/v1/projects", json={
        "name": "builder_proj",
        "title": "Builder Project",
    }, headers=auth_headers)
    project_id = resp.get_json()["id"]

    model_resp = client.post(f"/api/v1/projects/{project_id}/models", json={
        "projectId": project_id,
        "name": "crm_leads",
        "title": "Leads",
        "technical_name": "crm_leads",
        "table_name": "crm_leads"
    }, headers=auth_headers)
    assert model_resp.status_code == 201
    model_id = model_resp.get_json()["id"]

    with app.app_context():
        sm = db.session.get(SysModel, model_id)
        assert sm.name == "crm_leads"
        assert sm.projectId == project_id
