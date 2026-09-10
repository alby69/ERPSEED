import datetime
import pytest
from backend.models.product import Product, StockValuationLayer
from backend.models.sales import SalesOrder
from backend.models.purchase import PurchaseOrder
from backend.models.logistics import Incoterm, Carrier
from backend.models.crm import Lead
from backend.modules.crm.services import calculate_lead_score


def test_product_enhanced_fields_and_valuation_layer():
    product = Product(
        tenant_id=1,
        name="Test Product",
        code="PROD001",
        unit_price=100.0,
        reorder_point=15.0,
        abc_classification="A",
        costing_method="FIFO"
    )
    assert product.reorder_point == 15.0
    assert product.abc_classification == "A"
    assert product.costing_method == "FIFO"

    valuation_layer = StockValuationLayer(
        tenant_id=1,
        product_id=10,
        quantity=5.0,
        unit_cost=20.0,
        total_value=100.0,
        accounting_date=datetime.date.today()
    )
    assert valuation_layer.quantity == 5.0
    assert valuation_layer.unit_cost == 20.0
    assert valuation_layer.total_value == 100.0


def test_logistics_and_order_fields():
    incoterm = Incoterm(tenant_id=1, code="FOB", name="Free on Board")
    carrier = Carrier(tenant_id=1, name="DHL Express")

    sales_order = SalesOrder(
        tenant_id=1,
        number="SO001",
        customer_id=1,
        incoterm_id=1,
        carrier_id=1,
        tracking_number="TRACK123",
        analytic_account_id=5
    )
    assert sales_order.tracking_number == "TRACK123"
    assert sales_order.analytic_account_id == 5

    purchase_order = PurchaseOrder(
        tenant_id=1,
        number="PO001",
        supplier_id=1,
        incoterm_id=1,
        carrier_id=1,
        tracking_number="TRACK456",
        analytic_account_id=5
    )
    assert purchase_order.tracking_number == "TRACK456"


def test_crm_lead_scoring():
    lead_data = {
        "email": "test@example.com",
        "company": "Acme Corp",
        "source": "website"
    }
    score = calculate_lead_score(lead_data)
    assert score == 60

    lead = Lead(
        tenant_id=1,
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        company="TechInc",
        source="referral",
        lead_score=30
    )
    calculated = calculate_lead_score(lead)
    assert calculated == 30
