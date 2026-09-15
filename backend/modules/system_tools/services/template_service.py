"""
Template Service - Gestione installazione starter templates.
Supports loading templates from YAML blueprints in backend/templates and JSON in backend/templates/data.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any
import yaml

from backend.extensions import db
from backend.modules.builder.service import get_builder_service as BuilderService
from backend.models import SysView, SysModel, SysField


class TemplateService:
    """Service per caricare e installare template predefiniti."""

    def __init__(self):
        self.root_templates_dir = Path(__file__).resolve().parent.parent.parent.parent / "templates"
        self.data_templates_dir = self.root_templates_dir / "data"
        self.builder_service = BuilderService()

    def _find_template_file(self, template_name: str) -> Path:
        """Finds YAML or JSON template file by name/id."""
        yaml_path = self.root_templates_dir / f"{template_name}.yaml"
        if yaml_path.exists():
            return yaml_path

        yml_path = self.root_templates_dir / f"{template_name}.yml"
        if yml_path.exists():
            return yml_path

        json_path = self.data_templates_dir / f"{template_name}.json"
        if json_path.exists():
            return json_path

        raise ValueError(f"Template '{template_name}' non trovato")

    def _load_template_data(self, file_path: Path) -> Dict[str, Any]:
        """Loads data from a YAML or JSON template file."""
        with open(file_path, "r", encoding="utf-8") as f:
            if file_path.suffix in [".yaml", ".yml"]:
                return yaml.safe_load(f)
            return json.load(f)

    def list_templates(self) -> List[Dict[str, Any]]:
        """Lista tutti i template disponibili su disco."""
        templates = []

        # 1. Search YAML files in root_templates_dir
        if self.root_templates_dir.exists():
            for file in self.root_templates_dir.glob("*.yaml"):
                try:
                    data = self._load_template_data(file)
                    templates.append({
                        "id": data.get("id", file.stem),
                        "name": data.get("name", file.stem),
                        "description": data.get("description", ""),
                        "category": data.get("category", "Starter"),
                        "modules": data.get("modules", []),
                        "models_count": len(data.get("models", [])),
                        "views_count": len(data.get("views", []))
                    })
                except Exception as e:
                    print(f"Error loading YAML template {file}: {e}")

        # 2. Search JSON files in data_templates_dir
        if self.data_templates_dir.exists():
            for file in self.data_templates_dir.glob("*.json"):
                try:
                    data = self._load_template_data(file)
                    templates.append({
                        "id": data.get("id", file.stem),
                        "name": data.get("name", file.stem),
                        "description": data.get("description", ""),
                        "category": data.get("category", "Starter"),
                        "modules": data.get("modules", []),
                        "models_count": len(data.get("models", [])),
                        "views_count": len(data.get("views", []))
                    })
                except Exception as e:
                    print(f"Error loading JSON template {file}: {e}")

        templates.sort(key=lambda x: x.get("id") or "")
        return templates

    def apply_template(self, template_name: str, projectId: int = 1, tenant_id: int = 1) -> Dict[str, Any]:
        """Installa/applica un template nel sistema per un determinato progetto e tenant."""
        file_path = self._find_template_file(template_name)
        template = self._load_template_data(file_path)

        created_models = []

        # 1. Create Models and Fields
        for model_data in template.get("models", []):
            table_name = model_data.get("table") or model_data.get("name")
            title = model_data.get("title") or table_name

            # Check if SysModel already exists
            existing_model = SysModel.query.filter_by(technical_name=table_name).first()
            if existing_model:
                model = existing_model
            else:
                model = self.builder_service.create_model(
                    projectId=projectId,
                    name=table_name,
                    title=title,
                    description=model_data.get("description", "")
                )

            for field_data in model_data.get("fields", []):
                existing_field = SysField.query.filter_by(modelId=model.id, name=field_data["name"]).first()
                if not existing_field:
                    self.builder_service.create_field(
                        modelId=model.id,
                        name=field_data["name"],
                        field_type=field_data.get("type", "string"),
                        title=field_data.get("title", field_data["name"]),
                        required=field_data.get("required", False),
                        options=json.dumps(field_data.get("options")) if "options" in field_data else None
                    )

            created_models.append({"id": model.id, "name": model.name, "technical_name": model.technical_name})

        # 2. Activate tenant modules if specified
        activated_modules = template.get("modules", [])

        db.session.commit()

        return {
            "success": True,
            "message": f"Template '{template.get('name', template_name)}' applicato con successo.",
            "template_id": template.get("id", template_name),
            "modules": activated_modules,
            "models": created_models
        }

    def install_template(self, template_id: str, projectId: int = 1) -> Dict[str, Any]:
        """Alias for apply_template for backward compatibility."""
        return self.apply_template(template_id, projectId=projectId)


template_service = TemplateService()
