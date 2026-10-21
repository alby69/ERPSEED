"""
Unit tests for Scaffold DSL Template Parser and CQRS Commands (Phase 6.1).
"""
import pytest
import os
import tempfile

from backend.core.scaffold.commands import (
    RegisterEntityCommand,
    DefineRelationCommand,
    ScaffoldBackendCommand,
    ScaffoldFrontendCommand,
    GenerateMigrationCommand,
)
from backend.core.scaffold.parser import TemplateParser, ScaffoldParseError


SAMPLE_SALES_ORDER_YAML = """
module: sales
entity: SalesOrder
extends: BaseDocument

metadata:
  label: "Ordine di Vendita"
  icon: "ShoppingCartOutlined"

fields:
  - name: order_number
    type: string
    constraints: [required, unique]
    ui: { label: "Numero Ordine", width: 150 }
  - name: order_date
    type: date
    default: now
    ui: { label: "Data Ordine" }
  - name: total_amount
    type: decimal
    ui: { label: "Totale", readonly: true }

relations:
  - name: customer
    target: entities.Subject
    type: many_to_one
    ui: { component: "ProductLookupInput", label: "Cliente" }
  - name: lines
    target: sales.SalesOrderLine
    type: one_to_many
    cascade: all
    ui: { component: "InlineEditableTable", label: "Righe Ordine" }

permissions:
  create: ["admin", "sales_manager"]
  read: ["admin", "sales_manager", "viewer"]
"""


def test_parse_sales_order_yaml():
    parser = TemplateParser()
    commands = parser.parse_string(SAMPLE_SALES_ORDER_YAML, tenant_id=1)

    assert len(commands) > 0

    # 1. RegisterEntityCommand
    reg_cmd = commands[0]
    assert isinstance(reg_cmd, RegisterEntityCommand)
    assert reg_cmd.module == "sales"
    assert reg_cmd.entity == "SalesOrder"
    assert reg_cmd.extends == "BaseDocument"
    assert reg_cmd.metadata["label"] == "Ordine di Vendita"
    assert reg_cmd.tenant_id == 1

    # Verify BaseDocument inherited fields
    field_names = [f["name"] for f in reg_cmd.fields]
    assert "id" in field_names
    assert "created_at" in field_names
    assert "updated_at" in field_names
    assert "created_by" in field_names
    assert "order_number" in field_names
    assert "order_date" in field_names
    assert "total_amount" in field_names

    # 2. DefineRelationCommands
    rel_cmds = [c for c in commands if isinstance(c, DefineRelationCommand)]
    assert len(rel_cmds) == 2

    customer_rel = rel_cmds[0]
    assert customer_rel.relation_name == "customer"
    assert customer_rel.target == "entities.Subject"
    assert customer_rel.relation_type == "many_to_one"
    assert customer_rel.ui_config["component"] == "ProductLookupInput"

    lines_rel = rel_cmds[1]
    assert lines_rel.relation_name == "lines"
    assert lines_rel.target == "sales.SalesOrderLine"
    assert lines_rel.relation_type == "one_to_many"
    assert lines_rel.cascade == "all"
    assert lines_rel.ui_config["component"] == "InlineEditableTable"

    # 3. ScaffoldBackendCommand
    backend_cmds = [c for c in commands if isinstance(c, ScaffoldBackendCommand)]
    assert len(backend_cmds) == 1
    assert backend_cmds[0].module == "sales"
    assert backend_cmds[0].entity == "SalesOrder"

    # 4. ScaffoldFrontendCommand
    frontend_cmds = [c for c in commands if isinstance(c, ScaffoldFrontendCommand)]
    assert len(frontend_cmds) == 1
    assert frontend_cmds[0].module == "sales"
    assert frontend_cmds[0].entity == "SalesOrder"

    # 5. GenerateMigrationCommand
    migration_cmds = [c for c in commands if isinstance(c, GenerateMigrationCommand)]
    assert len(migration_cmds) == 1
    assert migration_cmds[0].module == "sales"
    assert migration_cmds[0].entity == "SalesOrder"


def test_command_serialization():
    parser = TemplateParser()
    commands = parser.parse_string(SAMPLE_SALES_ORDER_YAML, tenant_id=42)
    reg_cmd = commands[0]

    d = reg_cmd.to_dict()
    assert d["module"] == "sales"
    assert d["entity"] == "SalesOrder"
    assert d["tenant_id"] == 42
    assert "command_id" in d
    assert "timestamp" in d

    payload = reg_cmd.to_payload()
    assert payload["module"] == "sales"
    assert payload["entity"] == "SalesOrder"


def test_parse_file():
    parser = TemplateParser()
    with tempfile.NamedTemporaryFile("w+", suffix=".yaml", delete=False) as f:
        f.write(SAMPLE_SALES_ORDER_YAML)
        temp_filename = f.name

    try:
        commands = parser.parse_file(temp_filename, tenant_id=10)
        assert len(commands) > 0
        assert commands[0].tenant_id == 10
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)


def test_parse_error_empty():
    parser = TemplateParser()
    with pytest.raises(ScaffoldParseError, match="empty"):
        parser.parse_string("")


def test_parse_error_invalid_yaml():
    parser = TemplateParser()
    with pytest.raises(ScaffoldParseError, match="YAML syntax error"):
        parser.parse_string("module: sales\n  invalid: [yaml: : syntax")


def test_parse_error_missing_module():
    parser = TemplateParser()
    bad_yaml = "entity: SalesOrder\nfields: []"
    with pytest.raises(ScaffoldParseError, match="Missing or invalid 'module'"):
        parser.parse_string(bad_yaml)


def test_parse_error_missing_entity():
    parser = TemplateParser()
    bad_yaml = "module: sales\nfields: []"
    with pytest.raises(ScaffoldParseError, match="Missing or invalid 'entity'"):
        parser.parse_string(bad_yaml)


def test_parse_error_non_dict_root():
    parser = TemplateParser()
    with pytest.raises(ScaffoldParseError, match="Root element of template must be a YAML object"):
        parser.parse_string("- item1\n- item2")
