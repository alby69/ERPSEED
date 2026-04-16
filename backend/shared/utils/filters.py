"""
Filter utilities for domain-based filtering.
"""

from typing import List, Any, Tuple, Optional


DOMAIN_OPERATORS = {
    "=": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
    "<": lambda a, b: a < b,
    ">": lambda a, b: a > b,
    "<=": lambda a, b: a <= b,
    ">=": lambda a, b: a >= b,
    "like": lambda a, b: (a or "").lower() in b.lower(),
    "ilike": lambda a, b: (a or "").lower() in b.lower(),
    "in": lambda a, b: a in b,
    "not in": lambda a, b: a not in b,
    "is null": lambda a, b: a is None if b else a is not None,
    "is not null": lambda a, b: a is not None if b else a is None,
    "between": lambda a, b: b[0] <= a <= b[1] if b and len(b) == 2 else False,
}


def normalize_domain(domain: List) -> List[Tuple[str, str, Any]]:
    """Normalize domain to standard format (field, operator, value).

    Args:
        domain: List of domain expressions in various formats

    Returns:
        Normalized domain: [(field, operator, value), ...]
    """
    normalized = []

    for item in domain:
        if isinstance(item, (list, tuple)):
            if len(item) == 2:
                normalized.append((item[0], "=", item[1]))
            elif len(item) == 3:
                normalized.append(item)

    return normalized


def apply_domain_filter(
    items: List[dict], domain: List, fields_map: Optional[dict] = None
) -> List[dict]:
    """Apply domain filter to a list of dictionaries.

    Args:
        items: List of record dictionaries
        domain: Domain expressions [(field, operator, value), ...]
        fields_map: Optional mapping of domain field names to actual keys

    Returns:
        Filtered list of items
    """
    if not domain:
        return items

    normalized = normalize_domain(domain)
    fields_map = fields_map or {}

    filtered = []
    for item in items:
        matches = True
        for field, operator, value in normalized:
            actual_field = fields_map.get(field, field)
            item_value = item.get(actual_field)

            op_func = DOMAIN_OPERATORS.get(
                operator.lower() if isinstance(operator, str) else operator
            )
            if op_func:
                try:
                    if not op_func(item_value, value):
                        matches = False
                        break
                except Exception:
                    matches = False
                    break
            else:
                matches = False
                break

        if matches:
            filtered.append(item)

    return filtered
