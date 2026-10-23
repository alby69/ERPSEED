"""
CodeGenerator for Schema-as-Code Scaffold Engine.
Renders Jinja2 backend and frontend code templates from scaffold commands.
"""
import os
import re
from typing import Any, Dict, List, Optional
from jinja2 import Environment, FileSystemLoader

# Map DSL field types to SQLAlchemy column definitions
SA_TYPE_MAP = {
    "string": "db.String(255)",
    "integer": "db.Integer",
    "float": "db.Float",
    "decimal": "db.Numeric(12, 2)",
    "boolean": "db.Boolean",
    "date": "db.Date",
    "datetime": "db.DateTime",
    "text": "db.Text",
    "json": "db.JSON",
}

# Map DSL field types to Marshmallow field definitions
MM_TYPE_MAP = {
    "string": "String",
    "integer": "Integer",
    "float": "Float",
    "decimal": "Decimal",
    "boolean": "Boolean",
    "date": "Date",
    "datetime": "DateTime",
    "text": "String",
    "json": "Dict",
}


def camel_to_snake(name: str) -> str:
    """Converts CamelCase to snake_case."""
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


class CodeGenerator:
    """
    Renders Jinja2 templates to materialize full-stack Python/React source files.
    """

    def __init__(self, template_dir: Optional[str] = None):
        if template_dir is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            template_dir = os.path.join(base_dir, "templates")

        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def _prepare_context(
        self,
        module_name: str,
        entity_name: str,
        fields: List[Dict[str, Any]],
        relations: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        table_name = camel_to_snake(entity_name)
        endpoint_slug = table_name.replace("_", "-")

        fields = fields or []
        relations = relations or []

        formatted_fields = []
        for f in fields:
            f_type = f.get("type", "string")
            f_name = f.get("name")
            constraints = f.get("constraints", [])

            is_req = "required" in constraints or f.get("required", False)
            is_uniq = "unique" in constraints or f.get("unique", False)

            default_val = f.get("default")
            if default_val == "now":
                default_val = None

            formatted_fields.append({
                "name": f_name,
                "type": f_type,
                "sa_type": SA_TYPE_MAP.get(f_type, "db.String(255)"),
                "mm_type": MM_TYPE_MAP.get(f_type, "String"),
                "required": is_req,
                "unique": is_uniq,
                "default_val": repr(default_val) if default_val is not None else None,
                "ui": f.get("ui", {}),
            })

        formatted_relations = []
        for r in relations:
            target = r.get("target", "")
            target_parts = target.split(".")
            target_entity = target_parts[-1] if target_parts else "Unknown"
            target_table = camel_to_snake(target_entity)

            formatted_relations.append({
                "name": r.get("name"),
                "target_entity": target_entity,
                "target_table": target_table,
                "relation_type": r.get("type", "many_to_one"),
                "foreign_key_field": f"{r.get('name')}_id",
                "ui": r.get("ui", {}),
            })

        return {
            "module_name": module_name,
            "entity_name": entity_name,
            "table_name": table_name,
            "endpoint_slug": endpoint_slug,
            "fields": formatted_fields,
            "relations": formatted_relations,
            "metadata": metadata or {},
        }

    def generate_backend(
        self,
        module_name: str,
        entity_name: str,
        fields: List[Dict[str, Any]],
        relations: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, str]:
        """
        Generates backend code files dictionary (filename -> content).
        """
        ctx = self._prepare_context(module_name, entity_name, fields, relations, metadata)

        model_tmpl = self.env.get_template("backend/model.py.j2")
        schema_tmpl = self.env.get_template("backend/schemas.py.j2")
        cmd_tmpl = self.env.get_template("backend/commands.py.j2")
        handler_tmpl = self.env.get_template("backend/handlers.py.j2")
        api_tmpl = self.env.get_template("backend/rest_api.py.j2")

        return {
            "models.py": model_tmpl.render(ctx),
            "schemas.py": schema_tmpl.render(ctx),
            "commands.py": cmd_tmpl.render(ctx),
            "handlers.py": handler_tmpl.render(ctx),
            "rest_api.py": api_tmpl.render(ctx),
        }

    def generate_frontend(
        self,
        module_name: str,
        entity_name: str,
        fields: List[Dict[str, Any]],
        relations: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, str]:
        """
        Generates frontend React files dictionary (filename -> content).
        """
        ctx = self._prepare_context(module_name, entity_name, fields, relations, metadata)

        list_tmpl = self.env.get_template("frontend/ListPage.jsx.j2")
        form_tmpl = self.env.get_template("frontend/FormPage.jsx.j2")
        api_tmpl = self.env.get_template("frontend/api.js.j2")

        return {
            f"{entity_name}ListPage.jsx": list_tmpl.render(ctx),
            f"{entity_name}FormPage.jsx": form_tmpl.render(ctx),
            "api.js": api_tmpl.render(ctx),
        }
