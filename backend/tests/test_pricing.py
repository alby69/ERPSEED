"""Test per il modulo Listini Prezzo (PriceList + PriceListItem).

Verifica CRUD listini e gestione voci di listino.
"""
from backend.extensions import db
from backend.models import Product


def _create_product(app):
    with app.app_context():
        p = Product(tenant_id=1, code="PROD-TEST", name="Test Product", unit_price=10.0)
        db.session.add(p)
        db.session.commit()
        return p.id


def test_create_price_list(client, auth_headers, app):
    payload = {"code": "LISTA1", "name": "Listino Base", "currency": "EUR"}
    resp = client.post("/api/v1/price-lists", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["code"] == "LISTA1"
    assert data["name"] == "Listino Base"
    return data["id"]


def test_list_price_lists(client, auth_headers, app):
    _create_price_list(client, auth_headers)
    resp = client.get("/api/v1/price-lists", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) >= 1


def test_get_price_list(client, auth_headers, app):
    created = _create_price_list(client, auth_headers)
    resp = client.get(f"/api/v1/price-lists/{created['id']}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["code"] == "PL-ONE"


def test_update_price_list(client, auth_headers, app):
    created = _create_price_list(client, auth_headers)
    resp = client.put(f"/api/v1/price-lists/{created['id']}", json={"name": "Listino Aggiornato"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "Listino Aggiornato"


def test_delete_price_list(client, auth_headers, app):
    created = _create_price_list(client, auth_headers)
    resp = client.delete(f"/api/v1/price-lists/{created['id']}", headers=auth_headers)
    assert resp.status_code == 204


def test_price_list_items_crud(client, auth_headers, app):
    pl = _create_price_list(client, auth_headers)
    product_id = _create_product(app)

    item_payload = {"product_id": product_id, "price": 15.50}
    resp = client.post(f"/api/v1/price-lists/{pl['id']}/items", json=item_payload, headers=auth_headers)
    assert resp.status_code == 201
    item = resp.get_json()
    assert item["price"] == 15.50

    resp = client.get(f"/api/v1/price-lists/{pl['id']}/items", headers=auth_headers)
    items = resp.get_json()
    assert len(items) == 1

    resp = client.put(f"/api/v1/price-lists/{pl['id']}/items/{item['id']}", json={"price": 12.00}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["price"] == 12.00

    resp = client.delete(f"/api/v1/price-lists/{pl['id']}/items/{item['id']}", headers=auth_headers)
    assert resp.status_code == 204


def test_create_price_list_validation(client, auth_headers, app):
    resp = client.post("/api/v1/price-lists", json={"name": "No Code"}, headers=auth_headers)
    assert resp.status_code == 400


def _create_price_list(client, auth_headers):
    payload = {"code": "PL-ONE", "name": "Price List One", "currency": "EUR"}
    resp = client.post("/api/v1/price-lists", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    return resp.get_json()
