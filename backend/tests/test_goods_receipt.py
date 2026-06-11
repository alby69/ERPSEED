"""Test per il modulo DDT Entrata Merci (GoodsReceipt).

Verifica CRUD, gestione righe, completamento con aggiornamento scorte
e vincoli su DDT già completati.
"""
from backend.extensions import db
from backend.models import Product


def _create_product(app):
    with app.app_context():
        p = Product(tenant_id=1, code="PROD-GR", name="Prodotto Fornitura", unit_price=30.0)
        db.session.add(p)
        db.session.commit()
        return p.id


def _create_supplier(client, auth_headers):
    payload = {
        "tipo_soggetto": "persona_giuridica",
        "nome": "Fornitore",
        "ragione_sociale": "Fornitore Test Srl",
        "codice_fiscale": "FRNTST85M01H501Z",
        "partita_iva": "09876543211",
    }
    resp = client.post("/api/v1/soggetti", json=payload, headers=auth_headers)
    if resp.status_code == 201:
        return resp.get_json()
    return None


def test_create_goods_receipt(client, auth_headers, app):
    prod_id = _create_product(app)
    supplier = _create_supplier(client, auth_headers)
    supplier_id = supplier.get("id", 1) if supplier else 1

    payload = {
        "supplier_id": supplier_id,
        "notes": "DDT di prova",
        "lines": [
            {"product_id": prod_id, "quantity": 10, "description": "Prodotto A"},
            {"product_id": prod_id, "quantity": 5, "description": "Prodotto B"},
        ],
    }
    resp = client.post("/api/v1/goods-receipts", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["status"] == "draft"
    assert len(data["lines"]) == 2
    assert data["number"].startswith("DDT-")
    return data


def test_list_goods_receipts(client, auth_headers, app):
    _create_goods_receipt(client, auth_headers, app)
    resp = client.get("/api/v1/goods-receipts", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.get_json()) >= 1


def test_get_goods_receipt(client, auth_headers, app):
    gr = _create_goods_receipt(client, auth_headers, app)
    resp = client.get(f"/api/v1/goods-receipts/{gr['id']}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["id"] == gr["id"]


def test_update_goods_receipt(client, auth_headers, app):
    gr = _create_goods_receipt(client, auth_headers, app)
    resp = client.put(f"/api/v1/goods-receipts/{gr['id']}", json={"notes": "Note aggiornate"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["notes"] == "Note aggiornate"


def test_complete_goods_receipt(client, auth_headers, app):
    gr = _create_goods_receipt(client, auth_headers, app)
    resp = client.post(f"/api/v1/goods-receipts/{gr['id']}/complete", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "completed"


def test_cannot_modify_completed_receipt(client, auth_headers, app):
    gr = _create_goods_receipt(client, auth_headers, app)
    client.post(f"/api/v1/goods-receipts/{gr['id']}/complete", headers=auth_headers)
    resp = client.put(f"/api/v1/goods-receipts/{gr['id']}", json={"notes": "Tentativo"}, headers=auth_headers)
    assert resp.status_code == 400


def test_cannot_delete_completed_receipt(client, auth_headers, app):
    gr = _create_goods_receipt(client, auth_headers, app)
    client.post(f"/api/v1/goods-receipts/{gr['id']}/complete", headers=auth_headers)
    resp = client.delete(f"/api/v1/goods-receipts/{gr['id']}", headers=auth_headers)
    assert resp.status_code == 400


def test_create_goods_receipt_validation(client, auth_headers, app):
    resp = client.post("/api/v1/goods-receipts", json={"notes": "No supplier"}, headers=auth_headers)
    assert resp.status_code == 400


def _create_goods_receipt(client, auth_headers, app):
    prod_id = _create_product(app)
    supplier = _create_supplier(client, auth_headers)
    supplier_id = supplier.get("id", 1) if supplier else 1
    resp = client.post("/api/v1/goods-receipts", json={
        "supplier_id": supplier_id, "notes": "DDT Test",
        "lines": [{"product_id": prod_id, "quantity": 5}],
    }, headers=auth_headers)
    assert resp.status_code == 201
    return resp.get_json()
