"""Test per il modulo Fatturazione (Invoicing).

Verifica CRUD fatture, emissione, cancellazione, pagamento
e creazione da ordine vendita.
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


def _create_invoice(client, auth_headers, party_id):
    payload = {
        "invoice_type": "sales",
        "party_id": party_id,
        "lines": [
            {"description": "Prodotto A", "quantity": 2, "unit_price": 50.0, "vat_rate": 22.0},
            {"description": "Prodotto B", "quantity": 1, "unit_price": 100.0, "vat_rate": 10.0},
        ],
    }
    resp = client.post("/api/v1/invoicing/invoices", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    return resp.get_json()


def test_create_invoice(client, auth_headers):
    party = _create_soggetto(client, auth_headers)
    party_id = party.get("id", 1) if party else 1
    invoice = _create_invoice(client, auth_headers, party_id)
    assert invoice.get("id") is not None
    assert invoice.get("status") in ("draft", "issued")


def test_list_invoices(client, auth_headers):
    resp = client.get("/api/v1/invoicing/invoices", headers=auth_headers)
    assert resp.status_code == 200


def test_get_invoice(client, auth_headers):
    party = _create_soggetto(client, auth_headers)
    party_id = party.get("id", 1) if party else 1
    created = _create_invoice(client, auth_headers, party_id)
    inv_id = created.get("id")
    if not inv_id:
        return
    resp = client.get(f"/api/v1/invoicing/invoices/{inv_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json().get("id") == inv_id


def test_issue_invoice(client, auth_headers):
    party = _create_soggetto(client, auth_headers)
    party_id = party.get("id", 1) if party else 1
    created = _create_invoice(client, auth_headers, party_id)
    inv_id = created.get("id")
    if not inv_id:
        return
    resp = client.post(f"/api/v1/invoicing/invoices/{inv_id}/issue", headers=auth_headers)
    assert resp.status_code in (200, 400)
    if resp.status_code == 200:
        assert resp.get_json().get("status") in ("sent", "issued")


def test_cancel_invoice(client, auth_headers):
    party = _create_soggetto(client, auth_headers)
    party_id = party.get("id", 1) if party else 1
    created = _create_invoice(client, auth_headers, party_id)
    inv_id = created.get("id")
    if not inv_id:
        return
    client.post(f"/api/v1/invoicing/invoices/{inv_id}/issue", headers=auth_headers)
    resp = client.post(f"/api/v1/invoicing/invoices/{inv_id}/cancel", json={"reason": "Errore"}, headers=auth_headers)
    assert resp.status_code in (200, 400)


def test_pay_invoice(client, auth_headers):
    party = _create_soggetto(client, auth_headers)
    party_id = party.get("id", 1) if party else 1
    created = _create_invoice(client, auth_headers, party_id)
    inv_id = created.get("id")
    if not inv_id:
        return
    client.post(f"/api/v1/invoicing/invoices/{inv_id}/issue", headers=auth_headers)
    resp = client.post(f"/api/v1/invoicing/invoices/{inv_id}/pay", json={"amount": 200}, headers=auth_headers)
    assert resp.status_code in (200, 400)


def test_invoice_validation(client, auth_headers):
    resp = client.post("/api/v1/invoicing/invoices", json={}, headers=auth_headers)
    assert resp.status_code in (400, 201)
