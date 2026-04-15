"""
Query Builder - Dynamic query construction for the ORM.

Provides a fluent interface for building SQL queries from domains.
"""

from typing import List, Dict, Any, Optional
import logging

from extensions import db

logger = logging.getLogger(__name__)


class QueryBuilder:
    """Builds SQLAlchemy queries from domain specifications."""

    OPERATORS = {
        "=": lambda c, v: c == v,
        "!=": lambda c, v: c != v,
        "<": lambda c, v: c < v,
        ">": lambda c, v: c > v,
        "<=": lambda c, v: c <= v,
        ">=": lambda c, v: c >= v,
        "like": lambda c, v: c.like(v),
        "ilike": lambda c, v: c.ilike(v),
        "not ilike": lambda c, v: ~c.ilike(v),
        "in": lambda c, v: c.in_(v),
        "not in": lambda c, v: ~c.in_(v),
        "is null": lambda c, v: c.is_(None) if v else c.isnot(None),
        "is not null": lambda c, v: c.isnot(None) if v else c.is_(None),
        "between": lambda c, v: c.between(v[0], v[1]),
    }

    def __init__(self, model_name: str, env):
        self.model_name = model_name
        self.env = env
        self._domain = []
        self._offset = 0
        self._limit = None
        self._order_by = None
        self._table = None
        self._query = None

    def _get_table(self):
        """Get the SQLAlchemy table for this model."""
        from models import SysModel

        sys_model = SysModel.query.filter(
            SysModel.technical_name == self.model_name,
            SysModel.projectId == self.env.projectId,
            SysModel.is_active == True,
        ).first()

        if not sys_model:
            raise ValueError(f"Model not found: {self.model_name}")

        table = db.metadata.tables.get(sys_model.table_name)
        if not table:
            raise ValueError(f"Table not found: {sys_model.table_name}")

        self._table = table
        return table

    def filter(self, domain: List) -> "QueryBuilder":
        """Add domain filters.

        Args:
            domain: List of tuples [(field, operator, value), ...]
                   Can also be simplified to [(field, value), ...] (= is assumed)

        Returns:
            Self for chaining
        """
        self._domain.extend(domain)
        return self

    def offset(self, offset: int) -> "QueryBuilder":
        """Set offset for pagination."""
        self._offset = offset
        return self

    def limit(self, limit: int) -> "QueryBuilder":
        """Set limit for pagination."""
        self._limit = limit
        return self

    def order_by(self, order: str) -> "QueryBuilder":
        """Set order by clause.

        Args:
            order: e.g., 'name ASC' or 'created_at DESC'
        """
        self._order_by = order
        return self

    def _build_where(self, table):
        """Build WHERE clause from domain."""
        from sqlalchemy import and_

        conditions = []

        for item in self._domain:
            # Normalize domain item
            if len(item) == 2:
                field, value = item
                operator = "="
            elif len(item) == 3:
                field, operator, value = item
            else:
                logger.warning(f"Invalid domain item: {item}")
                continue

            # Get column
            if field not in table.c:
                logger.warning(f"Field not found in table: {field}")
                continue

            column = table.c[field]

            # Get operator function
            op_func = self.OPERATORS.get(
                operator.lower() if isinstance(operator, str) else operator
            )
            if not op_func:
                logger.warning(f"Unknown operator: {operator}")
                continue

            try:
                condition = op_func(column, value)
                conditions.append(condition)
            except Exception as e:
                logger.warning(
                    f"Error building condition {field} {operator} {value}: {e}"
                )
                continue

        if conditions:
            return and_(*conditions)
        return None

    def _build_order_by(self, table):
        """Build ORDER BY clause."""
        if not self._order_by:
            return None

        # Parse "field direction"
        parts = self._order_by.split()
        field = parts[0]
        direction = parts[1].upper() if len(parts) > 1 else "ASC"

        if field not in table.c:
            return None

        column = table.c[field]
        return column.asc() if direction == "ASC" else column.desc()

    def all(self) -> List[Dict]:
        """Execute query and return all results."""
        table = self._get_table()

        query = table.select()

        # Apply WHERE
        where_clause = self._build_where(table)
        if where_clause:
            query = query.where(where_clause)

        # Apply ORDER BY
        order_clause = self._build_order_by(table)
        if order_clause:
            query = query.order_by(order_clause)

        # Apply OFFSET
        if self._offset:
            query = query.offset(self._offset)

        # Apply LIMIT
        if self._limit:
            query = query.limit(self._limit)

        result = db.session.execute(query)
        return [dict(row._mapping) for row in result]

    def first(self) -> Optional[Dict]:
        """Execute query and return first result."""
        results = self.limit(1).all()
        return results[0] if results else None

    def count(self) -> int:
        """Count records matching the domain."""
        from sqlalchemy import func

        table = self._get_table()

        query = db.session.query(func.count(table.c.id))

        where_clause = self._build_where(table)
        if where_clause:
            query = query.where(where_clause)

        return query.scalar()

    def exists(self) -> bool:
        """Check if any records match the domain."""
        return self.count() > 0


def parse_domain(domain: List) -> List:
    """Parse and normalize a domain.

    Handles both simple and complex domain formats.
    """
    normalized = []

    for item in domain:
        if isinstance(item, (list, tuple)):
            if len(item) == 2:
                # Simple: (field, value) → (field, '=', value)
                normalized.append((item[0], "=", item[1]))
            elif len(item) == 3:
                normalized.append(item)
            elif len(item) > 3:
                # Complex domain: AND/OR
                normalized.append(item)

    return normalized
