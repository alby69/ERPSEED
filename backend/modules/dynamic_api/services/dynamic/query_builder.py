import json
import re
from sqlalchemy import select, func
from backend.core.utils.utils import get_table_object

class QueryBuilder:
    """Handles construction of relational queries for dynamic models."""

    @staticmethod
    def build_relational_query(sys_model, table, schema=None):
        """Build query with joins for relations, lookups, and summaries."""
        columns_to_select = [table]
        relation_fields = {}
        joins_to_make = {}

        for field in sys_model.fields:
            # Handle Relations
            if field.type == "relation" and field.options:
                try:
                    options = json.loads(field.options)
                    target_table_name = options.get("target_table")
                    if target_table_name:
                        target_table = get_table_object(target_table_name, schema=schema)
                        label_prefix = f"{field.name}__"
                        relation_fields[field.name] = {
                            "target_table": target_table,
                            "label_prefix": label_prefix,
                        }
                        for col in target_table.c:
                            columns_to_select.append(col.label(f"{label_prefix}{col.name}"))

                        join_key = f"{table.name}_{target_table_name}"
                        if join_key not in joins_to_make:
                            joins_to_make[join_key] = (
                                target_table,
                                table.c[field.name] == target_table.c.id,
                            )
                except (json.JSONDecodeError, KeyError):
                    pass

            # Handle Lookups
            if field.type == "lookup" and field.options:
                try:
                    options = json.loads(field.options)
                    target_table_name = options.get("target_table")
                    local_key = options.get("local_key")
                    remote_key = options.get("remote_key", "id")
                    remote_field = options.get("remote_field")

                    if target_table_name and local_key and remote_field:
                        target_table = get_table_object(target_table_name, schema=schema)
                        columns_to_select.append(target_table.c[remote_field].label(field.name))
                        join_key = f"{table.name}_{target_table_name}"
                        if join_key not in joins_to_make:
                            joins_to_make[join_key] = (
                                target_table,
                                table.c[local_key] == target_table.c[remote_key],
                            )
                except (json.JSONDecodeError, KeyError):
                    pass

            # Handle Summaries
            if field.type == "summary" and field.options and field.summary_expression:
                try:
                    options = json.loads(field.options)
                    target_table_name = options.get("target_table")
                    foreign_key = options.get("foreign_key")

                    if target_table_name:
                        target_table = get_table_object(target_table_name, schema=schema)
                        match = re.match(r"(\w+)\((\w+)\)", field.summary_expression)
                        if match:
                            func_name, col_name = match.groups()
                            if col_name in target_table.c:
                                sql_func = getattr(func, func_name)
                                if foreign_key:
                                    subquery = (
                                        select(sql_func(target_table.c[col_name]))
                                        .where(target_table.c[foreign_key] == table.c.id)
                                        .scalar_subquery()
                                    )
                                else:
                                    subquery = select(sql_func(target_table.c[col_name])).scalar_subquery()

                                columns_to_select.append(subquery.label(field.name))
                except (json.JSONDecodeError, KeyError, AttributeError):
                    pass

        query = select(*columns_to_select)
        for join_target, join_condition in joins_to_make.values():
            query = query.join(join_target, join_condition, isouter=True)

        return query, relation_fields
