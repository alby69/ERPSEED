"""
Computed Fields Engine - Handles calculation of computed fields.

Evaluates Python expressions for computed fields based on other field values.
"""

import json
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ComputedFieldEngine:
    """Engine for computing field values dynamically."""

    def __init__(self):
        self._functions = {}
        self._register_builtin_functions()

    def _register_builtin_functions(self):
        """Register built-in functions available in computed fields."""
        self._functions = {
            # String functions
            "UPPER": str.upper,
            "LOWER": str.lower,
            "TITLE": str.title,
            "STRIP": str.strip,
            "LEN": len,
            # Math functions
            "SUM": sum,
            "MIN": min,
            "MAX": max,
            "ABS": abs,
            "ROUND": round,
            # Date functions
            "NOW": lambda: __import__("datetime").datetime.now(),
            "TODAY": lambda: __import__("datetime").date.today(),
            # Conversion
            "FLOAT": float,
            "INT": int,
            "STR": str,
            "BOOL": bool,
            # JSON
            "JSON_LOADS": json.loads,
            "JSON_DUMPS": json.dumps,
            # Conditional
            "IF": lambda cond, true_val, false_val: true_val if cond else false_val,
            "COALESCE": lambda *args: next((a for a in args if a is not None), None),
            # List operations
            "LIST": list,
            "JOIN": lambda lst, sep: sep.join(lst) if lst else "",
            "SPLIT": lambda s, sep: s.split(sep) if s else [],
            "MAP": lambda lst, fn: list(map(fn, lst)),
            "FILTER": lambda lst, fn: list(filter(fn, lst)),
        }

    def register_function(self, name: str, func: callable):
        """Register a custom function for use in computed fields."""
        self._functions[name.upper()] = func

    def compute(self, record: Dict, field_def: Dict) -> Any:
        """Compute the value of a computed field.

        Args:
            record: Dictionary of field values
            field_def: Field definition containing compute_script

        Returns:
            Computed value
        """
        compute_script = field_def.get("compute_script")
        if not compute_script:
            return None

        try:
            # Create evaluation context
            context = {
                **self._functions,
                "record": record,
                # Expose record fields directly
                **record,
            }

            # Execute the compute script
            result = eval(compute_script, {"__builtins__": {}}, context)
            return result

        except Exception as e:
            logger.error(f"Error computing field {field_def.get('name')}: {e}")
            return None

    def get_dependencies(self, field_def: Dict) -> list:
        """Get list of fields this computed field depends on."""
        depends_on = field_def.get("depends_on", "")
        if not depends_on:
            return []

        return [d.strip() for d in depends_on.split(",") if d.strip()]

    def is_stale(self, record: Dict, field_def: Dict) -> bool:
        """Check if computed field needs to be recalculated.

        For now, always recalculate. In production, could track
        which fields changed and compare with dependencies.
        """
        return True


# Global instance
_computed_engine = None


def get_computed_engine() -> ComputedFieldEngine:
    """Get the global computed field engine."""
    global _computed_engine
    if _computed_engine is None:
        _computed_engine = ComputedFieldEngine()
    return _computed_engine


def compute_field_value(record: Dict, field_def: Dict) -> Any:
    """Convenience function to compute a field value."""
    engine = get_computed_engine()
    return engine.compute(record, field_def)
