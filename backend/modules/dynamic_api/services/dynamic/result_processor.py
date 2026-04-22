import json
import re
from backend.core.utils.utils import serialize_value
from backend.core.services.security.safe_evaluator import SafeEvaluator

class ResultProcessor:
    """Handles processing of raw database results into structured data."""

    @staticmethod
    def evaluate_formulas(record, sys_model):
        """Evaluate formula fields for a record."""
        formula_fields = [
            f for f in sys_model.fields if f.type == "formula" and f.formula
        ]
        if not formula_fields:
            return record

        all_placeholders = set()
        for field in formula_fields:
            placeholders = re.findall(r"\{(\w+)\}", field.formula)
            all_placeholders.update(placeholders)

        context = {p: record.get(p) for p in all_placeholders}

        for key, val in context.items():
            try:
                context[key] = float(val if val is not None else 0)
            except (ValueError, TypeError):
                pass

        for field in formula_fields:
            try:
                expression = re.sub(r"\{(\w+)\}", r"\1", field.formula)
                # Use SafeEvaluator instead of eval() for security
                result = SafeEvaluator.evaluate(expression, context)
                record[field.name] = result
            except Exception:
                record[field.name] = None
        return record

    @classmethod
    def process_results(cls, raw_results, relation_fields, sys_model):
        """Process flat results into nested objects with formulas."""
        if not raw_results:
            return []

        is_single = not isinstance(raw_results, list)
        results_list = [raw_results] if is_single else raw_results

        processed_list = []
        field_types = {f.name: f.type for f in sys_model.fields}

        for raw_row in results_list:
            processed_row = {}
            nested_objects = {}

            for key, value in raw_row.items():
                safe_value = serialize_value(value)
                is_relational = False
                for rel_field_name, rel_info in relation_fields.items():
                    prefix = rel_info["label_prefix"]
                    if key.startswith(prefix):
                        original_field_name = key[len(prefix) :]
                        if rel_field_name not in nested_objects:
                            nested_objects[rel_field_name] = {}
                        nested_objects[rel_field_name][original_field_name] = safe_value
                        is_relational = True
                        break
                if not is_relational:
                    val = safe_value
                    if field_types.get(key) == "tags" and isinstance(val, str):
                        try:
                            val = json.loads(val)
                        except:
                            pass
                    processed_row[key] = val

            for rel_field_name, nested_data in nested_objects.items():
                object_name = (
                    rel_field_name[:-3]
                    if rel_field_name.endswith("_id")
                    else rel_field_name
                )
                processed_row[object_name] = (
                    nested_data
                    if not all(v is None for v in nested_data.values())
                    else None
                )

            processed_row = cls.evaluate_formulas(processed_row, sys_model)
            processed_list.append(processed_row)

        return processed_list[0] if is_single else processed_list
