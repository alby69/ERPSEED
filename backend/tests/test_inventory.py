"""Test per il modulo Magazzino (Inventory).

Verifica CRUD ubicazioni, giacenze, movimenti, e conteggi inventario.
"""


def test_list_locations(client, auth_headers):
    resp = client.get("/inventory/locations", headers=auth_headers)
    assert resp.status_code == 200


def test_create_location(client, auth_headers):
    payload = {"name": "Magazzino Centrale", "code": "WH-01"}
    resp = client.post("/inventory/locations", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["name"] == "Magazzino Centrale"


def test_get_location(client, auth_headers):
    create = client.post("/inventory/locations", json={
        "name": "Magazzino Nord", "code": "WH-02"
    }, headers=auth_headers)
    lid = create.get_json()["id"]
    resp = client.get(f"/inventory/locations/{lid}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["id"] == lid


def test_list_stock(client, auth_headers):
    resp = client.get("/inventory/stock", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)


def test_list_movements(client, auth_headers):
    resp = client.get("/inventory/movements", headers=auth_headers)
    assert resp.status_code == 200


def test_list_inventory_counts(client, auth_headers):
    resp = client.get("/inventory/counts", headers=auth_headers)
    assert resp.status_code == 200


def test_stock_summary_report(client, auth_headers):
    resp = client.get("/inventory/reports/stock-summary", headers=auth_headers)
    assert resp.status_code == 200


def test_low_stock_report(client, auth_headers):
    resp = client.get("/inventory/reports/low-stock", headers=auth_headers)
    assert resp.status_code == 200
