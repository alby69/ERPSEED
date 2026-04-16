"""
Environment - Provides access to dynamic models (similar to Odoo).

The Environment is the main interface for working with dynamic models.
It provides:
- Model access via env[model_name]
- CRUD operations
- Transaction management
"""

from typing import Dict, Any, Optional, List
import logging

from orm.registry import get_registry
from orm.query import QueryBuilder

logger = logging.getLogger(__name__)


class Environment:
    """Environment for accessing dynamic models.

    Usage:
        env = Environment(tenant_id, user_id)
        leads = env['crm.lead'].search([('state', '=', 'new')])
        lead = env['crm.lead'].create({'name': 'Test'})
    """

    def __init__(self, tenant_id: int, user_id: int = None, project_id: int = None):
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.project_id = project_id
        self.registry = get_registry()
        self._cache = {}

    def __getitem__(self, model_name: str) -> "DynamicModelProxy":
        """Access a model by name.

        Usage:
            env['crm.lead'] → DynamicModelProxy
        """
        return DynamicModelProxy(model_name, self)

    def __call__(self, model_name: str, domain: List = None) -> Any:
        """Search records.

        Usage:
            env['crm.lead']([('state', '=', 'new')]) → list of records
        """
        model = self[model_name]
        if domain:
            return model.search(domain)
        return model

    def flush(self):
        """Flush all pending changes to database."""
        from extensions import db

        db.session.flush()

    def commit(self):
        """Commit the current transaction."""
        from extensions import db

        db.session.commit()

    def rollback(self):
        """Rollback the current transaction."""
        from extensions import db

        db.session.rollback()

    def invalidate_cache(self):
        """Invalidate the environment cache."""
        self._cache.clear()

    def get_model_definition(self, model_name: str) -> Optional[Dict]:
        """Get the full definition of a model from SysModel."""
        from models import SysModel

        sys_model = SysModel.query.filter(
            SysModel.technical_name == model_name,
            SysModel.project_id == self.project_id,
            SysModel.is_active == True,
        ).first()

        if not sys_model:
            return None

        return {
            "id": sys_model.id,
            "name": sys_model.name,
            "technical_name": sys_model.technical_name,
            "table_name": sys_model.table_name,
            "title": sys_model.title,
            "description": sys_model.description,
            "module_id": sys_model.module_id,
            "is_system": sys_model.is_system,
            "status": sys_model.status,
            "fields": [
                {
                    "id": f.id,
                    "name": f.name,
                    "technical_name": f.technical_name,
                    "type": f.type,
                    "required": f.required,
                    "is_unique": f.is_unique,
                    "is_index": f.is_index,
                    "is_active": f.is_active,
                    "default_value": f.default_value,
                    "relation_model": f.relation_model,
                    "relation_type": f.relation_type,
                    "relation_field": f.relation_field,
                    "options": f.options,
                    "ui_widget": f.ui_widget,
                    "ui_placeholder": f.ui_placeholder,
                    "ui_group": f.ui_group,
                    "ui_visible": f.ui_visible,
                    "ui_readonly": f.ui_readonly,
                    "ui_searchable": f.ui_searchable,
                    "ui_filterable": f.ui_filterable,
                    "is_computed": f.is_computed,
                    "compute_script": f.compute_script,
                    "validation_regex": f.validation_regex,
                    "validation_message": f.validation_message,
                }
                for f in sys_model.fields
                if f.is_active
            ],
        }


class DynamicModelProxy:
    """Proxy for dynamic model operations.

    Provides a fluent interface for CRUD operations.
    """

    def __init__(self, model_name: str, env: Environment):
        self.model_name = model_name
        self.env = env

    def search(
        self, domain: List = None, offset: int = 0, limit: int = None, order: str = None
    ) -> List[Dict]:
        """Search for records matching the domain.

        Args:
            domain: List of tuples [(field, operator, value), ...]
            offset: Number of records to skip
            limit: Maximum number of records to return
            order: Order by clause (e.g., 'name ASC')

        Returns:
            List of record dictionaries
        """
        query = QueryBuilder(self.model_name, self.env)

        if domain:
            query = query.filter(domain)

        if offset:
            query = query.offset(offset)

        if limit:
            query = query.limit(limit)

        if order:
            query = query.order_by(order)

        return query.all()

    def create(self, vals: Dict) -> int:
        """Create a new record.

        Args:
            vals: Dictionary of field values

        Returns:
            ID of the created record
        """
        from models import SysModel
        from extensions import db

        # Get the SysModel definition
        sys_model = SysModel.query.filter(
            SysModel.technical_name == self.model_name,
            SysModel.project_id == self.env.project_id,
        ).first()

        if not sys_model:
            raise ValueError(f"Model not found: {self.model_name}")

        # Validate values
        self._validate(sys_model, vals)

        # Create the record in the dynamic table
        table = db.metadata.tables.get(sys_model.table_name)
        if not table:
            raise ValueError(f"Table not found: {sys_model.table_name}")

        # Add tenant_id if present
        if "tenant_id" in table.columns:
            vals["tenant_id"] = self.env.tenant_id

        result = db.session.execute(table.insert(), vals)
        db.session.flush()

        return result.inserted_primary_key[0]

    def write(self, ids: List[int], vals: Dict) -> bool:
        """Update records.

        Args:
            ids: List of record IDs to update
            vals: Dictionary of field values to update

        Returns:
            True if successful
        """
        from models import SysModel
        from extensions import db

        sys_model = SysModel.query.filter(
            SysModel.technical_name == self.model_name,
            SysModel.project_id == self.env.project_id,
        ).first()

        if not sys_model:
            raise ValueError(f"Model not found: {self.model_name}")

        # Validate values
        self._validate(sys_model, vals, update=True)

        table = db.metadata.tables.get(sys_model.table_name)
        if not table:
            raise ValueError(f"Table not found: {sys_model.table_name}")

        db.session.execute(table.update().where(table.c.id.in_(ids)).values(**vals))
        db.session.flush()

        return True

    def unlink(self, ids: List[int]) -> bool:
        """Delete records.

        Args:
            ids: List of record IDs to delete

        Returns:
            True if successful
        """
        from models import SysModel
        from extensions import db

        sys_model = SysModel.query.filter(
            SysModel.technical_name == self.model_name,
            SysModel.project_id == self.env.project_id,
        ).first()

        if not sys_model:
            raise ValueError(f"Model not found: {self.model_name}")

        table = db.metadata.tables.get(sys_model.table_name)
        if not table:
            raise ValueError(f"Table not found: {sys_model.table_name}")

        db.session.execute(table.delete().where(table.c.id.in_(ids)))
        db.session.flush()

        return True

    def read(self, ids: List[int], fields: List[str] = None) -> List[Dict]:
        """Read records by IDs.

        Args:
            ids: List of record IDs
            fields: List of field names to read (None = all)

        Returns:
            List of record dictionaries
        """
        from models import SysModel
        from extensions import db

        sys_model = SysModel.query.filter(
            SysModel.technical_name == self.model_name,
            SysModel.project_id == self.env.project_id,
        ).first()

        if not sys_model:
            raise ValueError(f"Model not found: {self.model_name}")

        table = db.metadata.tables.get(sys_model.table_name)
        if not table:
            raise ValueError(f"Table not found: {sys_model.table_name}")

        query = table.select().where(table.c.id.in_(ids))

        if fields:
            query = query.with_only_columns(
                [table.c[f] for f in fields if f in table.c]
            )

        result = db.session.execute(query)
        return [dict(row) for row in result]

    def _validate(self, sys_model, vals: Dict, update: bool = False):
        """Validate field values against SysField definitions."""
        errors = []

        for field in sys_model.fields:
            field_name = field.technical_name

            # Skip if field not in values
            if field_name not in vals:
                if field.required and not update:
                    errors.append(f"Field '{field.name}' is required")
                continue

            value = vals[field_name]

            # Skip empty values if not required
            if value is None:
                if field.required:
                    errors.append(f"Field '{field.name}' is required")
                continue

            # Type validation would go here
            # For now, just basic checks

        if errors:
            raise ValueError("; ".join(errors))


def get_environment(
    tenant_id: int, user_id: int = None, project_id: int = None
) -> Environment:
    """Get an Environment instance.

    This is the main entry point for using the dynamic ORM.
    """
    return Environment(tenant_id, user_id, project_id)
