"""
Unit tests for Scaffold CodeGenerator.
"""
import pytest
from backend.core.scaffold.generator import CodeGenerator


def test_generator_backend_rendering():
    gen = CodeGenerator()
    fields = [
        {"name": "order_number", "type": "string", "constraints": ["required", "unique"]},
        {"name": "total_amount", "type": "decimal", "ui": {"label": "Totale"}},
    ]
    relations = [
        {"name": "customer", "target": "entities.Subject", "type": "many_to_one"}
    ]

    files = gen.generate_backend(
        module_name="sales",
        entity_name="SalesOrder",
        fields=fields,
        relations=relations,
        metadata={"label": "Ordine di Vendita"},
    )

    assert "models.py" in files
    assert "class SalesOrder(BaseModel):" in files["models.py"]
    assert "order_number = db.Column(db.String(255), nullable=False, unique=True)" in files["models.py"]
    assert "customer_id = db.Column(db.Integer, db.ForeignKey(\"subject.id\"), nullable=True)" in files["models.py"]

    assert "schemas.py" in files
    assert "class SalesOrderSchema(Schema):" in files["schemas.py"]

    assert "rest_api.py" in files
    assert "url_prefix=\"/api/v1/sales/sales-order\"" in files["rest_api.py"]


def test_generator_frontend_rendering():
    gen = CodeGenerator()
    fields = [
        {"name": "order_number", "type": "string", "constraints": ["required"]},
        {"name": "total_amount", "type": "decimal"},
    ]
    files = gen.generate_frontend(
        module_name="sales",
        entity_name="SalesOrder",
        fields=fields,
        relations=[],
        metadata={"label": "Ordine di Vendita"},
    )

    assert "SalesOrderListPage.jsx" in files
    assert "SalesOrderFormPage.jsx" in files
    assert "api.js" in files
    assert "/api/v1/sales/sales-order" in files["api.js"]
