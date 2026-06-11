"""Test per il modulo Report Designer.

Verifica CRUD report, discovery sorgenti dati,
esecuzione report e storico esecuzioni.
"""
import json


def test_get_sources(client, auth_headers):
    resp = client.get("/api/v1/report-designer/sources", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1
    keys = [s["key"] for s in data]
    assert "products" in keys
    assert "sales_orders" in keys


def test_create_report(client, auth_headers):
    config = {"source": "products", "columns": ["id", "name", "code"]}
    payload = {
        "code": "RPT-001",
        "name": "Elenco Prodotti",
        "description": "Report di prova",
        "category": "inventory",
        "report_type": "table",
        "config": config,
    }
    resp = client.post("/api/v1/report-designer/reports", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["code"] == "RPT-001"
    assert data["report_type"] == "table"
    return data


def test_list_reports(client, auth_headers):
    _create_report(client, auth_headers)
    resp = client.get("/api/v1/report-designer/reports", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.get_json()) >= 1


def test_get_report(client, auth_headers):
    rpt = _create_report(client, auth_headers)
    resp = client.get(f"/api/v1/report-designer/reports/{rpt['id']}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["id"] == rpt["id"]


def test_update_report(client, auth_headers):
    rpt = _create_report(client, auth_headers)
    resp = client.put(f"/api/v1/report-designer/reports/{rpt['id']}", json={"name": "Report Modificato"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "Report Modificato"


def test_delete_report(client, auth_headers):
    rpt = _create_report(client, auth_headers)
    resp = client.delete(f"/api/v1/report-designer/reports/{rpt['id']}", headers=auth_headers)
    assert resp.status_code == 204


def test_report_by_category(client, auth_headers):
    _create_report(client, auth_headers, "RPT-CAT", "sales")
    resp = client.get("/api/v1/report-designer/reports?category=sales", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.get_json()) >= 1


def test_create_report_validation(client, auth_headers):
    resp = client.post("/api/v1/report-designer/reports", json={"description": "Missing code"}, headers=auth_headers)
    assert resp.status_code == 400


def test_execute_report(client, auth_headers):
    rpt = _create_report(client, auth_headers)
    resp = client.post(f"/api/v1/report-designer/reports/{rpt['id']}/execute", json={}, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert "data" in data
    assert "row_count" in data
    assert "execution_time_ms" in data


def test_execute_report_with_filters(client, auth_headers):
    rpt = _create_report(client, auth_headers)
    resp = client.post(f"/api/v1/report-designer/reports/{rpt['id']}/execute", json={
        "filters": [{"field": "id", "operator": "eq", "value": 1}],
    }, headers=auth_headers)
    assert resp.status_code == 200


def test_execution_history(client, auth_headers):
    rpt = _create_report(client, auth_headers)
    client.post(f"/api/v1/report-designer/reports/{rpt['id']}/execute", json={}, headers=auth_headers)
    resp = client.get(f"/api/v1/report-designer/reports/{rpt['id']}/history", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)


def _create_report(client, auth_headers, code="RPT-TEST", category="inventory"):
    config = {"source": "products", "columns": ["id", "name", "code"]}
    resp = client.post("/api/v1/report-designer/reports", json={
        "code": code, "name": f"Report {code}", "category": category,
        "report_type": "table", "config": config,
    }, headers=auth_headers)
    assert resp.status_code == 201
    return resp.get_json()
