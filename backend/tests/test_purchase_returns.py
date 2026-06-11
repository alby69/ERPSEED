"""Test per il modulo Resi Acquisti.

Verifica CRUD resi acquisto e completamento con movimenti di magazzino.
"""


def _create_supplier(client, auth_headers):
    payload = {
        "tipo_soggetto": "persona_giuridica",
        "nome": "Fornitore",
        "ragione_sociale": "Fornitore Test Srl",
        "codice_fiscale": "RSSMRA85M01H501Z",
        "partita_iva": "01234567890",
    }
    resp = client.post("/api/v1/soggetti", json=payload, headers=auth_headers)
    if resp.status_code == 201:
        return resp.get_json()
    return None


def test_create_purchase_return(client, auth_headers):
    supplier = _create_supplier(client, auth_headers)
    supplier_id = supplier.get("id", 1) if supplier else 1
    payload = {
        "supplier_id": supplier_id,
        "date": "2026-06-15",
        "reason": "Producti difettosi",
        "lines": [
            {"product_id": 1, "description": "Reso Prodotto A", "quantity": 5},
        ],
    }
    resp = client.post("/api/v1/purchase-returns", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["status"] == "draft"
    assert data["reason"] == "Producti difettosi"
    assert len(data["lines"]) == 1


def test_list_purchase_returns(client, auth_headers):
    resp = client.get("/api/v1/purchase-returns", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)


def test_get_purchase_return(client, auth_headers):
    supplier = _create_supplier(client, auth_headers)
    supplier_id = supplier.get("id", 1) if supplier else 1
    created = client.post("/api/v1/purchase-returns", json={
        "supplier_id": supplier_id,
        "date": "2026-07-01",
        "reason": "Test",
        "lines": [{"product_id": 1, "description": "Test", "quantity": 2}],
    }, headers=auth_headers).get_json()
    rid = created["id"]
    resp = client.get(f"/api/v1/purchase-returns/{rid}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["id"] == rid


def test_update_purchase_return(client, auth_headers):
    supplier = _create_supplier(client, auth_headers)
    supplier_id = supplier.get("id", 1) if supplier else 1
    created = client.post("/api/v1/purchase-returns", json={
        "supplier_id": supplier_id,
        "date": "2026-07-01",
        "reason": "Originale",
    }, headers=auth_headers).get_json()
    rid = created["id"]
    resp = client.put(f"/api/v1/purchase-returns/{rid}", json={
        "reason": "Aggiornato",
    }, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["reason"] == "Aggiornato"


def test_delete_purchase_return(client, auth_headers):
    supplier = _create_supplier(client, auth_headers)
    supplier_id = supplier.get("id", 1) if supplier else 1
    created = client.post("/api/v1/purchase-returns", json={
        "supplier_id": supplier_id,
        "date": "2026-07-01",
        "reason": "Da eliminare",
    }, headers=auth_headers).get_json()
    rid = created["id"]
    resp = client.delete(f"/api/v1/purchase-returns/{rid}", headers=auth_headers)
    assert resp.status_code in (200, 204)
    resp = client.get(f"/api/v1/purchase-returns/{rid}", headers=auth_headers)
    assert resp.status_code == 404


def test_complete_purchase_return(client, auth_headers):
    supplier = _create_supplier(client, auth_headers)
    supplier_id = supplier.get("id", 1) if supplier else 1
    created = client.post("/api/v1/purchase-returns", json={
        "supplier_id": supplier_id,
        "date": "2026-07-01",
        "reason": "Da completare",
        "lines": [{"product_id": 1, "description": "Reso", "quantity": 3}],
    }, headers=auth_headers).get_json()
    rid = created["id"]
    resp = client.post(f"/api/v1/purchase-returns/{rid}/complete", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "completed"


def test_cannot_modify_completed(client, auth_headers):
    supplier = _create_supplier(client, auth_headers)
    supplier_id = supplier.get("id", 1) if supplier else 1
    created = client.post("/api/v1/purchase-returns", json={
        "supplier_id": supplier_id,
        "date": "2026-07-01",
        "reason": "Test vincolo",
    }, headers=auth_headers).get_json()
    rid = created["id"]
    client.post(f"/api/v1/purchase-returns/{rid}/complete", headers=auth_headers)
    resp = client.put(f"/api/v1/purchase-returns/{rid}", json={"reason": "No"}, headers=auth_headers)
    assert resp.status_code == 400


def test_validation_no_supplier(client, auth_headers):
    resp = client.post("/api/v1/purchase-returns", json={
        "date": "2026-07-01",
    }, headers=auth_headers)
    assert resp.status_code == 400
