import re
import json
from flask_smorest import abort

class FieldValidator:
    """Handles validation and conversion of dynamic field values."""

    @staticmethod
    def validate(field, value):
        """
        Validate and convert value based on field type.
        """
        if value is None:
            if field.required:
                abort(400, message=f"Field '{field.name}' is required and cannot be null.")
            return None

        try:
            if field.validation_regex and field.type in ["string", "text"]:
                if not re.fullmatch(field.validation_regex, str(value)):
                    abort(
                        400,
                        message=field.validation_message
                        or f"Value for '{field.name}' does not match the required format.",
                    )

            if field.type == "select":
                if field.options:
                    try:
                        opts = json.loads(field.options)
                        valid_values = []
                        if isinstance(opts, list):
                            for o in opts:
                                if isinstance(o, dict):
                                    valid_values.append(o.get("value"))
                                else:
                                    valid_values.append(o)

                        if valid_values and value not in valid_values:
                            abort(
                                400,
                                message=f"Invalid value '{value}' for field '{field.name}'. Allowed: {valid_values}",
                            )
                    except (json.JSONDecodeError, AttributeError):
                        pass
                return str(value)

            if field.type in ["integer", "relation"]:
                return int(value)
            elif field.type in ["float", "currency"]:
                return float(value)
            elif field.type == "boolean":
                if isinstance(value, bool):
                    return value
                v_str = str(value).lower()
                if v_str in ["true", "1", "t", "y", "yes"]:
                    return True
                if v_str in ["false", "0", "f", "n", "no"]:
                    return False
                raise ValueError
            elif field.type == "tags":
                if isinstance(value, str):
                    try:
                        value = json.loads(value)
                    except:
                        value = [x.strip() for x in value.split(",") if x.strip()]
                if not isinstance(value, list):
                    abort(
                        400,
                        message=f"Invalid format for tags field '{field.name}'. Expected list.",
                    )
                return json.dumps(value)
            return value
        except (ValueError, TypeError):
            abort(
                400,
                message=f"Invalid type for field '{field.name}'. Expected {field.type}.",
            )
