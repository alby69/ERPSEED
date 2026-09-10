"""
Tests for Sales & Purchases Data Model Enhancements.
"""
from datetime import date
from backend.extensions import db
from backend.modules.sales.domain.models import SalesOrder, SalesOrderLine
from backend.modules.purchases.domain.models import PurchaseOrder, PurchaseOrderLine
from backend.modules.sales.infrastructure.repository import SalesOrderRepository
from backend.modules.purchases.infrastructure.repository import PurchaseOrderRepository


def test_sales_order_line_discount_calculation():
    line = SalesOrderLine(
        product_id=1,
        quantity=10.0,
        unit_price=100.0,
        discount_percent=15.0,
        tax_id=1,
        uom_id=2,
    )
    total = line.calculate_total()
    assert total == 850.0
    assert line.total_price == 850.0


def test_sales_order_domain_enhancements():
    order = SalesOrder(
        number="SO-2026-001",
        customer_id=10,
        pricelist_id=2,
        currency_id="USD",
        payment_term_id=3,
        billing_address_id=4,
        shipping_address_id=5,
        salesperson_id=6,
        customer_reference="PO-CLIENT-999",
        warehouse_id=1,
        lines=[
            SalesOrderLine(product_id=1, quantity=2, unit_price=50, discount_percent=10)
        ]
    )
    order.calculate_total()
    assert order.total_amount == 90.0

    d = order.to_dict()
    assert d["pricelist_id"] == 2
    assert d["currency_id"] == "USD"
    assert d["customer_reference"] == "PO-CLIENT-999"
    assert d["lines"][0]["discount_percent"] == 10.0
    assert d["lines"][0]["total_price"] == 90.0

    restored = SalesOrder.from_dict(d)
    assert restored.currency_id == "USD"
    assert restored.customer_reference == "PO-CLIENT-999"
    assert restored.lines[0].discount_percent == 10.0


def test_purchase_order_line_discount_calculation():
    line = PurchaseOrderLine(
        product_id=1,
        quantity=5.0,
        unit_price=200.0,
        discount_percent=20.0,
        expected_delivery_date=date(2026, 12, 1)
    )
    total = line.calculate_total()
    assert total == 800.0
    assert line.expected_delivery_date == date(2026, 12, 1)


def test_purchase_order_domain_enhancements():
    order = PurchaseOrder(
        number="PO-2026-001",
        supplier_id=20,
        currency_id="EUR",
        payment_term_id=1,
        buyer_id=2,
        supplier_reference="SUP-REF-123",
        landing_costs=50.0,
        lines=[
            PurchaseOrderLine(product_id=1, quantity=1, unit_price=100, discount_percent=10)
        ]
    )
    order.calculate_total()
    # 90 + 50 landing costs = 140
    assert order.total_amount == 140.0

    d = order.to_dict()
    assert d["buyer_id"] == 2
    assert d["supplier_reference"] == "SUP-REF-123"
    assert d["landing_costs"] == 50.0

    restored = PurchaseOrder.from_dict(d)
    assert restored.supplier_reference == "SUP-REF-123"
    assert restored.landing_costs == 50.0


def test_sales_repository_enhancements(app):
    with app.app_context():
        repo = SalesOrderRepository(db)
        data = {
            "tenant_id": 1,
            "number": "SO-TEST-001",
            "customer_id": 1,
            "pricelist_id": 5,
            "currency_id": "USD",
            "payment_term_id": 2,
            "customer_reference": "REF-TEST",
            "lines": [
                {"product_id": 1, "description": "Item 1", "quantity": 10, "unit_price": 10, "discount_percent": 10}
            ]
        }
        res = repo.create(data)
        assert res["currency_id"] == "USD"
        assert res["customer_reference"] == "REF-TEST"
        assert res["lines"][0]["discount_percent"] == 10.0
        assert res["lines"][0]["total_price"] == 90.0
        assert res["total_amount"] == 90.0


def test_purchase_repository_enhancements(app):
    with app.app_context():
        repo = PurchaseOrderRepository(db)
        data = {
            "tenant_id": 1,
            "number": "PO-TEST-001",
            "supplier_id": 1,
            "buyer_id": 3,
            "supplier_reference": "REF-SUPPLIER",
            "landing_costs": 25.0,
            "lines": [
                {"product_id": 1, "description": "Raw Material", "quantity": 2, "unit_price": 50, "discount_percent": 5}
            ]
        }
        res = repo.create(data)
        assert res["buyer_id"] == 3
        assert res["supplier_reference"] == "REF-SUPPLIER"
        assert res["landing_costs"] == 25.0
        # line total = 2 * 50 * 0.95 = 95.0. total_amount = 95 + 25 = 120.0
        assert res["lines"][0]["total_price"] == 95.0
        assert res["total_amount"] == 120.0
