"""Test per il modulo Aliquote IVA (TaxRate).

Verifica il ciclo CRUD completo e le validazioni base.
"""


def test_create_tax_rate(client, auth_headers):
    payload = {
        "code": "IVA22",
        "name": "IVA 22%",
        "rate": 22.0,
        "is_active": True,
    }
    resp = client.post("/api/v1/tax-rates", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["code"] == "IVA22"
    assert data["rate"] == 22.0
    assert data["is_active"] is True
    return data["id"]


def test_list_tax_rates(client, auth_headers):
    test_create_tax_rate(client, auth_headers)
    resp = client.get("/api/v1/tax-rates", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data.get("items", data if isinstance(data, list) else [])) >= 1


def test_get_tax_rate(client, auth_headers):
    created = _create_tax_rate(client, auth_headers)
    resp = client.get(f"/api/v1/tax-rates/{created['id']}", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["code"] == "IVA10"


def test_update_tax_rate(client, auth_headers):
    created = _create_tax_rate(client, auth_headers)
    resp = client.put(f"/api/v1/tax-rates/{created['id']}", json={"rate": 12.0}, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["rate"] == 12.0


def test_delete_tax_rate(client, auth_headers):
    created = _create_tax_rate(client, auth_headers)
    resp = client.delete(f"/api/v1/tax-rates/{created['id']}", headers=auth_headers)
    assert resp.status_code == 204


def test_create_tax_rate_validation(client, auth_headers):
    resp = client.post("/api/v1/tax-rates", json={"name": "No Code"}, headers=auth_headers)
    assert resp.status_code == 400


def _create_tax_rate(client, auth_headers):
    payload = {
        "code": "IVA10",
        "name": "IVA 10%",
        "rate": 10.0,
        "is_active": True,
    }
    resp = client.post("/api/v1/tax-rates", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    return resp.get_json()
