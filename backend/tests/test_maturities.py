"""Test per il modulo Scadenzario (Maturities).

Verifica CRUD scadenze e generazione da fatture emesse.
"""


def _create_soggetto(client, auth_headers):
    payload = {
        "tipo_soggetto": "persona_giuridica",
        "nome": "Cliente",
        "ragione_sociale": "Cliente Test Srl",
        "codice_fiscale": "RSSMRA85M01H501Z",
        "partita_iva": "01234567890",
    }
    resp = client.post("/api/v1/soggetti", json=payload, headers=auth_headers)
    if resp.status_code == 201:
        return resp.get_json()
    return None


def test_create_maturity(client, auth_headers):
    party = _create_soggetto(client, auth_headers)
    party_id = party.get("id", 1) if party else 1
    payload = {
        "party_id": party_id,
        "due_date": "2026-07-15",
        "amount": 1500.00,
        "description": "Fattura 2026-001",
    }
    resp = client.post("/api/v1/maturities", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["amount"] == 1500.00
    assert data["balance"] == 1500.00
    assert data["status"] == "open"


def test_list_maturities(client, auth_headers):
    resp = client.get("/api/v1/maturities", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)


def test_get_maturity(client, auth_headers):
    party = _create_soggetto(client, auth_headers)
    party_id = party.get("id", 1) if party else 1
    created = client.post("/api/v1/maturities", json={
        "party_id": party_id,
        "due_date": "2026-08-01",
        "amount": 500.00,
    }, headers=auth_headers).get_json()
    mid = created["id"]
    resp = client.get(f"/api/v1/maturities/{mid}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["id"] == mid


def test_update_maturity(client, auth_headers):
    party = _create_soggetto(client, auth_headers)
    party_id = party.get("id", 1) if party else 1
    created = client.post("/api/v1/maturities", json={
        "party_id": party_id,
        "due_date": "2026-09-01",
        "amount": 1000.00,
    }, headers=auth_headers).get_json()
    mid = created["id"]
    resp = client.put(f"/api/v1/maturities/{mid}", json={
        "paid_amount": 400.00,
    }, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["paid_amount"] == 400.0
    assert data["balance"] == 600.0
    assert data["status"] == "partial"


def test_delete_maturity(client, auth_headers):
    party = _create_soggetto(client, auth_headers)
    party_id = party.get("id", 1) if party else 1
    created = client.post("/api/v1/maturities", json={
        "party_id": party_id,
        "due_date": "2026-10-01",
        "amount": 300.00,
    }, headers=auth_headers).get_json()
    mid = created["id"]
    resp = client.delete(f"/api/v1/maturities/{mid}", headers=auth_headers)
    assert resp.status_code in (200, 204)
    resp = client.get(f"/api/v1/maturities/{mid}", headers=auth_headers)
    assert resp.status_code == 404


def test_maturity_summary(client, auth_headers):
    resp = client.get("/api/v1/maturities/summary", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    for key in ("total_open", "total_overdue", "total_paid", "due_next_30_days"):
        assert key in data


def test_from_invoices(client, auth_headers):
    party = _create_soggetto(client, auth_headers)
    party_id = party.get("id", 1) if party else 1
    payload = {
        "invoice_type": "sales",
        "party_id": party_id,
        "lines": [
            {"description": "Consulenza", "quantity": 1, "unit_price": 2000.0, "vat_rate": 22.0},
        ],
    }
    resp = client.post("/api/v1/invoicing/invoices", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    inv = resp.get_json()
    inv_id = inv["id"]

    client.post(f"/api/v1/invoicing/invoices/{inv_id}/issue", headers=auth_headers)

    resp = client.post("/api/v1/maturities/from-invoices", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert "maturities created" in data["message"]

    mat_resp = client.get("/api/v1/maturities", headers=auth_headers)
    maturities = mat_resp.get_json()
    matched = [m for m in maturities if m.get("reference_type") == "invoice" and m.get("reference_id") == inv_id]
    assert len(matched) >= 1 # Allow for other maturities to exist


def test_from_invoices_no_duplicates(client, auth_headers):
    party = _create_soggetto(client, auth_headers)
    party_id = party.get("id", 1) if party else 1
    payload = {
        "invoice_type": "sales",
        "party_id": party_id,
        "lines": [
            {"description": "Sviluppo", "quantity": 1, "unit_price": 5000.0, "vat_rate": 22.0},
        ],
    }
    resp = client.post("/api/v1/invoicing/invoices", json=payload, headers=auth_headers)
    inv = resp.get_json()
    inv_id = inv["id"]
    client.post(f"/api/v1/invoicing/invoices/{inv_id}/issue", headers=auth_headers)

    r1 = client.post("/api/v1/maturities/from-invoices", headers=auth_headers)
    assert r1.status_code == 200
    c1 = int(r1.get_json()["message"].split()[0])
    assert c1 >= 1

    r2 = client.post("/api/v1/maturities/from-invoices", headers=auth_headers)
    assert r2.status_code == 200
    c2 = int(r2.get_json()["message"].split()[0])
    assert c2 == 0
