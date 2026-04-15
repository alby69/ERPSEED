"""
ERPSeed Dynamic ORM

A meta-model driven ORM that generates database tables from SysModel/SysField definitions.
Provides an Odoo-like interface for working with dynamic models.

Usage:
    from orm import get_environment

    env = get_environment(tenant_id=1, userId=1, projectId=1)

    # Search
    leads = env['crm.lead'].search([('state', '=', 'new')])

    # Create
    lead_id = env['crm.lead'].create({'name': 'Test Company', 'email': 'test@example.com'})

    # Update
    env['crm.lead'].write([lead_id], {'state': 'qualified'})

    # Delete
    env['crm.lead'].unlink([lead_id])
"""

from orm.registry import Registry, get_registry
from orm.environment import Environment, get_environment
from orm.fields import (
    Field,
    Char,
    Text,
    Integer,
    Float,
    Boolean,
    Date,
    DateTime,
    Json,
    Select,
    Many2one,
    One2many,
    Many2many,
    Computed,
    get_field_class,
)
from orm.query import QueryBuilder, parse_domain
from orm.computed import (
    ComputedFieldEngine,
    get_computed_engine,
    compute_field_value,
)
from orm.relations import RelationHandler, get_relation_handler
from orm.module_loader import (
    ModuleLoader,
    get_module_loader,
    scan_and_load_modules,
)

__all__ = [
    # Registry & Environment
    "Registry",
    "get_registry",
    "Environment",
    "get_environment",
    # Query
    "QueryBuilder",
    "parse_domain",
    # Fields
    "Field",
    "Char",
    "Text",
    "Integer",
    "Float",
    "Boolean",
    "Date",
    "DateTime",
    "Json",
    "Select",
    "Many2one",
    "One2many",
    "Many2many",
    "Computed",
    "get_field_class",
    # Computed Engine
    "ComputedFieldEngine",
    "get_computed_engine",
    "compute_field_value",
    # Relations
    "RelationHandler",
    "get_relation_handler",
    # Module Loader
    "ModuleLoader",
    "get_module_loader",
    "scan_and_load_modules",
]
