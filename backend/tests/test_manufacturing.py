"""Test per il modulo Produzione (Manufacturing).

Verifica CRUD Distinte Base (BOM), Cicli di Lavoro e Ordini di Produzione
con transizioni di stato.
"""
from backend.extensions import db
from backend.models import Product


def _create_product(app):
    with app.app_context():
        p = Product(tenant_id=1, code="PROD-MFG", name="Prodotto Finito", unit_price=100.0)
        db.session.add(p)
        db.session.commit()
        return p.id


def _create_component(app):
    with app.app_context():
        p = Product(tenant_id=1, code="COMP-MFG", name="Componente", unit_price=20.0)
        db.session.add(p)
        db.session.commit()
        return p.id


# ========== BOM ==========

def test_create_bom(client, auth_headers, app):
    prod_id = _create_product(app)
    comp_id = _create_component(app)
    payload = {
        "product_id": prod_id,
        "code": "BOM-001",
        "name": "Distinta Prodotto",
        "total_quantity": 1,
        "lines": [{"product_id": comp_id, "quantity": 2}],
    }
    resp = client.post("/api/v1/manufacturing/bom", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["code"] == "BOM-001"
    assert len(data["lines"]) == 1

    resp = client.get("/api/v1/manufacturing/bom", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.get_json()) >= 1


def test_get_bom(client, auth_headers, app):
    bom = _create_bom(client, auth_headers, app)
    resp = client.get(f"/api/v1/manufacturing/bom/{bom['id']}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["code"] == bom["code"]


def test_delete_bom(client, auth_headers, app):
    bom = _create_bom(client, auth_headers, app)
    resp = client.delete(f"/api/v1/manufacturing/bom/{bom['id']}", headers=auth_headers)
    assert resp.status_code == 204


# ========== Work Cycles ==========

def test_create_work_cycle(client, auth_headers, app):
    payload = {
        "code": "CICLO-001",
        "name": "Ciclo Assemblaggio",
        "phases": [
            {"phase_number": 10, "name": "Taglio", "setup_time": 10, "run_time": 30},
            {"phase_number": 20, "name": "Assemblaggio", "setup_time": 5, "run_time": 45},
        ],
    }
    resp = client.post("/api/v1/manufacturing/work-cycles", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["code"] == "CICLO-001"
    assert len(data["phases"]) == 2


def test_get_work_cycle(client, auth_headers, app):
    wc = _create_work_cycle(client, auth_headers)
    resp = client.get(f"/api/v1/manufacturing/work-cycles/{wc['id']}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["code"] == wc["code"]


# ========== Production Orders ==========

def test_create_production_order(client, auth_headers, app):
    prod_id = _create_product(app)
    payload = {"product_id": prod_id, "quantity": 10}
    resp = client.post("/api/v1/manufacturing/production-orders", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["quantity"] == 10
    assert data["status"] == "planned"


def test_production_order_status_transitions(client, auth_headers, app):
    po = _create_production_order(client, auth_headers, app)
    po_id = po["id"]

    resp = client.post(f"/api/v1/manufacturing/production-orders/{po_id}/release", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "released"

    resp = client.post(f"/api/v1/manufacturing/production-orders/{po_id}/start", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "in_progress"

    resp = client.post(f"/api/v1/manufacturing/production-orders/{po_id}/complete", json={"quantity_produced": 8}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "completed"


def test_get_production_order(client, auth_headers, app):
    po = _create_production_order(client, auth_headers, app)
    resp = client.get(f"/api/v1/manufacturing/production-orders/{po['id']}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["id"] == po["id"]


# ========== Helpers ==========

def _create_bom(client, auth_headers, app):
    prod_id = _create_product(app)
    comp_id = _create_component(app)
    resp = client.post("/api/v1/manufacturing/bom", json={
        "product_id": prod_id, "code": "BOM-TEST", "name": "BOM Test",
        "total_quantity": 1,
        "lines": [{"product_id": comp_id, "quantity": 2}],
    }, headers=auth_headers)
    assert resp.status_code == 201
    return resp.get_json()


def _create_work_cycle(client, auth_headers):
    resp = client.post("/api/v1/manufacturing/work-cycles", json={
        "code": "WC-TEST", "name": "WC Test",
        "phases": [{"phase_number": 10, "name": "Fase 1", "run_time": 30}],
    }, headers=auth_headers)
    assert resp.status_code == 201
    return resp.get_json()


def _create_production_order(client, auth_headers, app):
    prod_id = _create_product(app)
    resp = client.post("/api/v1/manufacturing/production-orders", json={
        "product_id": prod_id, "quantity": 5,
    }, headers=auth_headers)
    assert resp.status_code == 201
    return resp.get_json()
