"""
Template DSL Parser for Schema-as-Code Scaffold Engine.
Parses YAML declarative templates and converts them into CQRS scaffold commands.
"""
import os
import yaml
from typing import Any, Dict, List, Optional, Union

from backend.core.scaffold.commands import (
    RegisterEntityCommand,
    DefineRelationCommand,
    ScaffoldBackendCommand,
    ScaffoldFrontendCommand,
    GenerateMigrationCommand,
)


class ScaffoldParseError(Exception):
    """Raised when parsing a DSL template fails due to syntax or validation errors."""
    pass


# Default fields injected when extending BaseDocument
BASE_DOCUMENT_FIELDS = [
    {
        "name": "id",
        "type": "integer",
        "constraints": ["primary_key", "autoincrement"],
        "ui": {"label": "ID", "readonly": True},
    },
    {
        "name": "created_at",
        "type": "datetime",
        "default": "now",
        "ui": {"label": "Data Creazione", "readonly": True},
    },
    {
        "name": "updated_at",
        "type": "datetime",
        "default": "now",
        "ui": {"label": "Data Modifica", "readonly": True},
    },
    {
        "name": "created_by",
        "type": "integer",
        "ui": {"label": "Creato da", "readonly": True},
    },
]


class TemplateParser:
    """
    Parses YAML/Markdown DSL specifications for ERPSEED domain modules and generates
    corresponding domain commands.
    """

    def parse_file(self, filepath: str, tenant_id: Optional[int] = None) -> List[Any]:
        """
        Reads a YAML template from a file path and parses it.
        """
        if not os.path.exists(filepath):
            raise ScaffoldParseError(f"Template file not found: {filepath}")
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            raise ScaffoldParseError(f"Failed to read file '{filepath}': {str(e)}")
        return self.parse_string(content, tenant_id=tenant_id)

    def parse_string(self, content: str, tenant_id: Optional[int] = None) -> List[Any]:
        """
        Parses YAML text content into scaffold commands.
        """
        if not content or not content.strip():
            raise ScaffoldParseError("Template content is empty")

        try:
            raw_data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            raise ScaffoldParseError(f"YAML syntax error: {str(e)}")

        if not isinstance(raw_data, dict):
            raise ScaffoldParseError("Root element of template must be a YAML object/dictionary")

        return self.parse_dict(raw_data, tenant_id=tenant_id)

    def parse_dict(self, raw_data: Dict[str, Any], tenant_id: Optional[int] = None) -> List[Any]:
        """
        Validates raw parsed dictionary and materializes CQRS commands.
        """
        module = raw_data.get("module")
        entity = raw_data.get("entity")

        if not module or not isinstance(module, str):
            raise ScaffoldParseError("Missing or invalid 'module' field in template")

        if not entity or not isinstance(entity, str):
            raise ScaffoldParseError("Missing or invalid 'entity' field in template")

        extends = raw_data.get("extends")
        metadata = raw_data.get("metadata", {})
        if not isinstance(metadata, dict):
            raise ScaffoldParseError("'metadata' must be a dictionary")

        raw_fields = raw_data.get("fields", [])
        if not isinstance(raw_fields, list):
            raise ScaffoldParseError("'fields' must be a list")

        raw_relations = raw_data.get("relations", [])
        if not isinstance(raw_relations, list):
            raise ScaffoldParseError("'relations' must be a list")

        permissions = raw_data.get("permissions", {})
        if not isinstance(permissions, dict):
            raise ScaffoldParseError("'permissions' must be a dictionary")

        # Process BaseDocument inheritance
        fields = list(raw_fields)
        if extends == "BaseDocument":
            existing_field_names = {f.get("name") for f in fields if isinstance(f, dict)}
            for base_f in BASE_DOCUMENT_FIELDS:
                if base_f["name"] not in existing_field_names:
                    fields.insert(0, base_f)

        commands = []

        # 1. Register Entity Command
        reg_cmd = RegisterEntityCommand(
            module=module,
            entity=entity,
            extends=extends,
            metadata=metadata,
            fields=fields,
            relations=raw_relations,
            permissions=permissions,
            tenant_id=tenant_id,
        )
        commands.append(reg_cmd)

        # 2. Define Relation Commands for each defined relation
        for rel in raw_relations:
            if not isinstance(rel, dict):
                continue
            rel_name = rel.get("name")
            target = rel.get("target")
            rel_type = rel.get("type", "many_to_one")
            cascade = rel.get("cascade")
            ui_config = rel.get("ui", {})

            if rel_name and target:
                define_rel_cmd = DefineRelationCommand(
                    module=module,
                    entity=entity,
                    relation_name=rel_name,
                    target=target,
                    relation_type=rel_type,
                    cascade=cascade,
                    ui_config=ui_config if isinstance(ui_config, dict) else {},
                    tenant_id=tenant_id,
                )
                commands.append(define_rel_cmd)

        # 3. Scaffold Backend Command
        commands.append(
            ScaffoldBackendCommand(
                module=module,
                entity=entity,
                fields=fields,
                relations=raw_relations,
                tenant_id=tenant_id,
            )
        )

        # 4. Scaffold Frontend Command
        commands.append(
            ScaffoldFrontendCommand(
                module=module,
                entity=entity,
                fields=fields,
                relations=raw_relations,
                tenant_id=tenant_id,
            )
        )

        # 5. Generate Migration Command
        commands.append(
            GenerateMigrationCommand(
                module=module,
                entity=entity,
                tenant_id=tenant_id,
            )
        )

        return commands
