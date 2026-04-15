"""
Relation Handlers - Manages many2one, one2many, many2many relations.

Provides methods to resolve and traverse relations between dynamic models.
"""

from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class RelationHandler:
    """Handles relation operations between models."""

    @staticmethod
    def get_many2one(
        env, model_name: str, field_name: str, record_ids: List[int]
    ) -> Dict[int, Dict]:
        """Get related records for many2one fields.

        Args:
            env: Environment instance
            model_name: Current model name
            field_name: Field technical name (e.g., 'customer_id')
            record_ids: List of record IDs to get relations for

        Returns:
            Dict mapping record_id -> related record dict
        """
        from models import SysField, SysModel

        # Get the field definition
        sys_field = (
            SysField.query.join(SysModel)
            .filter(
                SysModel.technical_name == model_name,
                SysField.technical_name == field_name,
                SysField.type == "many2one",
            )
            .first()
        )

        if not sys_field or not sys_field.relation_model:
            return {}

        # Get the related model records
        related_model = sys_field.relation_model
        related_table = SysModel.query.filter(
            SysModel.technical_name == related_model,
            SysModel.projectId == env.projectId,
        ).first()

        if not related_table:
            return {}

        # Get unique IDs to fetch
        from extensions import db

        table = db.metadata.tables.get(related_table.table_name)
        if not table:
            return {}

        # Get the foreign key column name
        fk_column = field_name
        if fk_column not in table.c:
            return {}

        # Get unique related IDs
        current_table = db.metadata.tables.get(related_table.table_name)
        result = db.session.execute(
            table.select().where(
                table.c.id.in_(
                    db.session.query(current_table.c[fk_column])
                    .where(current_table.c.id.in_(record_ids))
                    .distinct()
                )
            )
        )

        related_ids = [row.id for row in result]

        if not related_ids:
            return {}

        # Fetch related records
        records = db.session.execute(table.select().where(table.c.id.in_(related_ids)))

        return {row.id: dict(row._mapping) for row in records}

    @staticmethod
    def get_one2many(
        env, model_name: str, field_name: str, record_ids: List[int]
    ) -> Dict[int, List[Dict]]:
        """Get related records for one2many fields.

        Args:
            env: Environment instance
            model_name: Current model name
            field_name: Field technical name (e.g., 'order_lines')
            record_ids: List of parent record IDs

        Returns:
            Dict mapping parent_id -> list of related records
        """
        from models import SysField, SysModel
        from extensions import db

        # Get the field definition
        sys_field = (
            SysField.query.join(SysModel)
            .filter(
                SysModel.technical_name == model_name,
                SysField.technical_name == field_name,
                SysField.type == "one2many",
            )
            .first()
        )

        if not sys_field or not sys_field.relation_model:
            return {}

        # Get the related model
        related_model_name = sys_field.relation_model
        related_table_def = SysModel.query.filter(
            SysModel.technical_name == related_model_name,
            SysModel.projectId == env.projectId,
        ).first()

        if not related_table_def:
            return {}

        # Find the inverse field (foreign key in related table)
        inverse_field = sys_field.relation_field or f"{model_name.split('.')[-1]}_id"

        related_table = db.metadata.tables.get(related_table_def.table_name)
        if not related_table or inverse_field not in related_table.c:
            return {}

        # Fetch related records
        result = db.session.execute(
            related_table.select().where(related_table.c[inverse_field].in_(record_ids))
        )

        # Group by parent ID
        grouped = {}
        for row in result:
            parent_id = row._mapping.get(inverse_field)
            if parent_id not in grouped:
                grouped[parent_id] = []
            grouped[parent_id].append(dict(row._mapping))

        return grouped

    @staticmethod
    def get_many2many(
        env, model_name: str, field_name: str, record_ids: List[int]
    ) -> Dict[int, List[Dict]]:
        """Get related records for many2many fields.

        Args:
            env: Environment instance
            model_name: Current model name
            field_name: Field technical name (e.g., 'tag_ids')
            record_ids: List of record IDs

        Returns:
            Dict mapping record_id -> list of related records
        """
        from models import SysField, SysModel
        from extensions import db
        from sqlalchemy import table as sa_table, column, select, join

        # Get the field definition
        sys_field = (
            SysField.query.join(SysModel)
            .filter(
                SysModel.technical_name == model_name,
                SysField.technical_name == field_name,
                SysField.type == "many2many",
            )
            .first()
        )

        if not sys_field or not sys_field.relation_model:
            return {}

        # Get the current model table
        current_model = SysModel.query.filter(
            SysModel.technical_name == model_name, SysModel.projectId == env.projectId
        ).first()

        if not current_model:
            return {}

        # Create the relation table name
        model_table_name = current_model.table_name
        related_table_name = sys_field.relation_model.split(".")[-1]
        relation_table_name = sys_field.relation_model  # Could be custom

        # Try to find the many2many relation table
        # Standard naming: model1_model2_rel
        possible_rel_names = [
            f"{model_table_name}_{related_table_name}_rel",
            f"{related_table_name}_{model_table_name}_rel",
            f"{model_table_name}_{related_table_name}",
            relation_table_name,
        ]

        rel_table = None
        for rel_name in possible_rel_names:
            if rel_name in db.metadata.tables:
                rel_table = db.metadata.tables[rel_name]
                break

        if not rel_table:
            logger.warning(f"Relation table not found for {model_name}.{field_name}")
            return {}

        # Get the two columns in the relation table
        rel_columns = [c.name for c in rel_table.c]

        # Find which column references which table
        # Assuming standard: model1_id, model2_id
        current_col = None
        related_col = None

        for col in rel_columns:
            if model_table_name in col or col.endswith("_1"):
                current_col = col
            elif related_table_name in col or col.endswith("_2"):
                related_col = col

        if not current_col or not related_col:
            current_col = rel_columns[0]
            related_col = rel_columns[1]

        # Get related IDs
        related_ids = db.session.execute(
            select([rel_table.c[related_col]]).where(
                rel_table.c[current_col].in_(record_ids)
            )
        )
        related_id_list = [row[0] for row in related_ids]

        if not related_id_list:
            return {}

        # Fetch related records
        related_model = sys_field.relation_model
        related_table_def = SysModel.query.filter(
            SysModel.technical_name == related_model,
            SysModel.projectId == env.projectId,
        ).first()

        if not related_table_def:
            return {}

        related_table = db.metadata.tables.get(related_table_def.table_name)
        if not related_table:
            return {}

        records = db.session.execute(
            related_table.select().where(related_table.c.id.in_(related_id_list))
        )

        # Group by original record ID
        # This is more complex for many2many - need to join
        result_map = {rid: [] for rid in record_ids}

        # Get the mapping
        mapping = db.session.execute(
            select([rel_table.c[current_col], related_table.c])
            .select_from(
                join(
                    rel_table,
                    related_table,
                    rel_table.c[related_col] == related_table.c.id,
                )
            )
            .where(rel_table.c[current_col].in_(record_ids))
        )

        for row in mapping:
            parent_id = row._mapping.get(current_col)
            if parent_id:
                result_map[parent_id].append(dict(row._mapping))

        return result_map


# Global instance
_relation_handler = None


def get_relation_handler() -> RelationHandler:
    """Get the global relation handler."""
    global _relation_handler
    if _relation_handler is None:
        _relation_handler = RelationHandler()
    return _relation_handler
