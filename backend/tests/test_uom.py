"""Test per il modulo Unità di Misura (UnitOfMeasure).

Verifica CRUD completo e validazione campi obbligatori.
"""


def test_create_uom(client, auth_headers):
    payload = {"code": "KG", "name": "Chilogrammo", "symbol": "kg"}
    resp = client.post("/api/v1/units-of-measure", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["code"] == "KG"
    assert data["name"] == "Chilogrammo"
    assert data["symbol"] == "kg"
    return data["id"]


def test_list_uoms(client, auth_headers):
    _create_uom(client, auth_headers, "LT", "Litri")
    _create_uom(client, auth_headers, "MT", "Metri")
    resp = client.get("/api/v1/units-of-measure", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) >= 2


def test_get_uom(client, auth_headers):
    created = _create_uom(client, auth_headers)
    resp = client.get(f"/api/v1/units-of-measure/{created['id']}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["code"] == "NR"


def test_update_uom(client, auth_headers):
    created = _create_uom(client, auth_headers)
    resp = client.put(f"/api/v1/units-of-measure/{created['id']}", json={"name": "Numero"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "Numero"


def test_delete_uom(client, auth_headers):
    created = _create_uom(client, auth_headers)
    resp = client.delete(f"/api/v1/units-of-measure/{created['id']}", headers=auth_headers)
    assert resp.status_code == 204


def test_create_uom_validation(client, auth_headers):
    resp = client.post("/api/v1/units-of-measure", json={"symbol": "x"}, headers=auth_headers)
    assert resp.status_code == 400


def test_create_duplicate_uom(client, auth_headers):
    _create_uom(client, auth_headers)
    resp = client.post("/api/v1/units-of-measure", json={"code": "NR", "name": "Duplicato"}, headers=auth_headers)
    assert resp.status_code == 400


def _create_uom(client, auth_headers, code="NR", name="Numero"):
    payload = {"code": code, "name": name, "symbol": name[:2]}
    resp = client.post("/api/v1/units-of-measure", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    return resp.get_json()
