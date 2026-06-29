import pytest
from datetime import date
from backend.extensions import cache
from backend.models import VatRegisterEntry

def test_vat_register_caching(client, auth_headers, app):
    # Setup: Ensure cache is clear
    with app.app_context():
        cache.clear()

        # Create a test entry
        entry = VatRegisterEntry(
            tenant_id=1,
            register_type="sales",
            entry_number=1,
            entry_date=date(2026, 1, 1),
            fiscal_year=2026,
            period="2026-01",
            taxable_amount=100.0,
            vat_amount=22.0
        )
        from backend.extensions import db
        db.session.add(entry)
        db.session.commit()

    # First request - should populate cache
    resp1 = client.get("/api/v1/vat/register?register_type=sales&fiscal_year=2026", headers=auth_headers)
    assert resp1.status_code == 200
    data1 = resp1.get_json()
    assert len(data1) >= 1

    # Modify database directly without clearing cache
    with app.app_context():
        entry = VatRegisterEntry.query.filter_by(fiscal_year=2026, entry_number=1).first()
        entry.notes = "Updated notes"
        from backend.extensions import db
        db.session.commit()

    # Second request - should still return cached data (old notes)
    resp2 = client.get("/api/v1/vat/register?register_type=sales&fiscal_year=2026", headers=auth_headers)
    assert resp2.status_code == 200
    data2 = resp2.get_json()
    # If notes was None, it should still be None or old value
    assert data2[0].get("notes") != "Updated notes"
    assert data2 == data1

    # Clear cache and request again
    with app.app_context():
        cache.clear()

    resp3 = client.get("/api/v1/vat/register?register_type=sales&fiscal_year=2026", headers=auth_headers)
    assert resp3.status_code == 200
    data3 = resp3.get_json()
    assert data3[0].get("notes") == "Updated notes"
    assert data3 != data1
