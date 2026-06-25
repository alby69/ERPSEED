"""
Template Service - Gestione installazione starter templates.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any

from backend.extensions import db
from backend.services.builder_service import BuilderService
from backend.models import SysView, SysModel, SysField

class TemplateService:
    """Service per caricare e installare template predefiniti."""

    def __init__(self):
        self.templates_dir = Path(__file__).parent.parent / "templates" / "data"
        self.builder_service = BuilderService()

    def list_templates(self) -> List[Dict[str, Any]]:
        """Lista tutti i template disponibili su disco."""
        templates = []
        if not self.templates_dir.exists():
            return templates

        for file in self.templates_dir.glob("*.json"):
            try:
                with open(file, "r") as f:
                    data = json.load(f)
                templates.append({
                    "id": data.get("id"),
                    "name": data.get("name"),
                    "description": data.get("description"),
                    "category": data.get("category"),
                    "models_count": len(data.get("models", [])),
                    "views_count": len(data.get("views", []))
                })
            except Exception as e:
                print(f"Error loading template {file}: {e}")

        return templates

    def install_template(self, template_id: str, project_id: int) -> Dict[str, Any]:
        """Installa un template in un progetto specifico."""
        template_file = self.templates_dir / f"{template_id}.json"
        if not template_file.exists():
            raise ValueError(f"Template {template_id} non trovato")

        with open(template_file, "r") as f:
            template = json.load(f)

        created_models = []

        # 1. Create Models and Fields
        for model_data in template.get("models", []):
            model = self.builder_service.create_model(
                project_id=project_id,
                name=model_data["table"],
                title=model_data["title"],
                description=model_data.get("description", "")
            )

            for field_data in model_data.get("fields", []):
                self.builder_service.create_field(
                    model_id=model.id,
                    name=field_data["name"],
                    field_type=field_data["type"],
                    title=field_data["title"],
                    required=field_data.get("required", False),
                    options=json.dumps(field_data.get("options")) if "options" in field_data else None
                )

            created_models.append({"id": model.id, "name": model.name, "technical_name": model.technical_name})

        # 2. Create Views (simplified for now)
        # Note: In a real scenario, we'd use the dedicated VisualBuilder API logic here

        db.session.commit()

        return {
            "success": True,
            "message": f"Template '{template['name']}' installato con successo.",
            "models": created_models
        }

template_service = TemplateService()
