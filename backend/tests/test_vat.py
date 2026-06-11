"""Test per il modulo IVA (VAT Register, Liquidation, Intrastat).

Verifica CRUD registri IVA, liquidazione IVA e dichiarazioni Intrastat.
"""


def test_create_vat_entry(client, auth_headers):
    payload = {
        "register_type": "sales",
        "entry_date": "2026-01-15",
        "document_number": "FAT-001",
        "soggetto_name": "Test Client",
        "taxable_amount": 1000.0,
        "vat_amount": 220.0,
        "vat_rate": 22.0,
    }
    resp = client.post("/api/v1/vat/register", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["entry_number"] == 1
    assert data["register_type"] == "sales"


def test_list_vat_entries(client, auth_headers):
    client.post("/api/v1/vat/register", json={
        "register_type": "sales", "entry_date": "2026-01-15",
        "taxable_amount": 500, "vat_amount": 110, "vat_rate": 22.0,
    }, headers=auth_headers)
    resp = client.get("/api/v1/vat/register?register_type=sales&period=2026-01", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 1


def test_get_vat_entry(client, auth_headers):
    create = client.post("/api/v1/vat/register", json={
        "register_type": "purchases", "entry_date": "2026-02-10",
        "document_number": "FAT-002",
        "taxable_amount": 800, "vat_amount": 176, "vat_rate": 22.0,
    }, headers=auth_headers)
    eid = create.get_json()["id"]
    resp = client.get(f"/api/v1/vat/register/{eid}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["id"] == eid


def test_update_vat_entry(client, auth_headers):
    create = client.post("/api/v1/vat/register", json={
        "register_type": "sales", "entry_date": "2026-03-01",
        "taxable_amount": 300, "vat_amount": 66, "vat_rate": 22.0,
    }, headers=auth_headers)
    eid = create.get_json()["id"]
    resp = client.put(f"/api/v1/vat/register/{eid}", json={
        "taxable_amount": 400, "vat_amount": 88,
    }, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["taxable_amount"] == 400


def test_delete_vat_entry(client, auth_headers):
    create = client.post("/api/v1/vat/register", json={
        "register_type": "sales", "entry_date": "2026-01-01",
        "taxable_amount": 100, "vat_amount": 22, "vat_rate": 22.0,
    }, headers=auth_headers)
    eid = create.get_json()["id"]
    resp = client.delete(f"/api/v1/vat/register/{eid}", headers=auth_headers)
    assert resp.status_code == 204


def test_vat_entry_validation(client, auth_headers):
    resp = client.post("/api/v1/vat/register", json={}, headers=auth_headers)
    assert resp.status_code == 400


def test_create_vat_liquidation(client, auth_headers):
    client.post("/api/v1/vat/register", json={
        "register_type": "sales", "entry_date": "2026-04-01",
        "period": "2026-04", "fiscal_year": 2026,
        "taxable_amount": 1000.0, "vat_amount": 220.0, "vat_rate": 22.0,
    }, headers=auth_headers)
    resp = client.post("/api/v1/vat/liquidations", json={
        "period": "2026-04", "fiscal_year": 2026, "type": "monthly",
    }, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["sales_taxable"] == 1000.0
    assert data["sales_vat"] == 220.0
    assert data["net_vat"] == 220.0


def test_list_vat_liquidations(client, auth_headers):
    resp = client.get("/api/v1/vat/liquidations", headers=auth_headers)
    assert resp.status_code == 200


def test_create_intrastat(client, auth_headers):
    payload = {
        "fiscal_year": 2026, "period": "2026-01",
        "type": "sales", "soggetto_id": 1,
        "amount": 5000.0, "vat_amount": 1100.0,
        "nature": "BE",
    }
    resp = client.post("/api/v1/vat/intrastat", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["fiscal_year"] == 2026


def test_list_intrastat(client, auth_headers):
    client.post("/api/v1/vat/intrastat", json={
        "fiscal_year": 2026, "period": "2026-02",
        "type": "purchases", "soggetto_id": 1,
        "amount": 3000.0, "vat_amount": 660.0,
        "nature": "BE",
    }, headers=auth_headers)
    resp = client.get("/api/v1/vat/intrastat?fiscal_year=2026", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.get_json()) == 1


def test_submit_intrastat(client, auth_headers):
    create = client.post("/api/v1/vat/intrastat", json={
        "fiscal_year": 2026, "period": "2026-03",
        "type": "sales", "soggetto_id": 1,
        "amount": 2000.0, "vat_amount": 440.0,
        "nature": "BE",
    }, headers=auth_headers)
    did = create.get_json()["id"]
    resp = client.post(f"/api/v1/vat/intrastat/{did}/submit", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "submitted"


def test_vat_register_generate_no_invoices(client, auth_headers):
    resp = client.post("/api/v1/vat/register/generate", json={
        "period": "2026-01", "register_type": "sales",
    }, headers=auth_headers)
    assert resp.status_code == 400
