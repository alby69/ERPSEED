"""
ImportExport Service - Sistema centralizzato per import/export di componenti.

Fornisce funzionalità per serializzare e deserializzare:
- SysModel (modelli)
- Block (blocchi UI)
- Workflow (workflow automatizzati)
- Module (moduli completi)
- Progetto (intero progetto)

Ogni componente ha:
- config.json: struttura/configurazione
- data.json: dati contenuti
"""

import json
import datetime
from typing import Dict, Any, List, Optional


class ImportExportService:
    """Servizio centralizzato per import/export."""

    def __init__(self, db=None):
        self.db = db

    # ==================== SYSMODEL ====================

    def export_sysmodel_config(self, sys_model) -> Dict[str, Any]:
        """Esporta la configurazione di un SysModel."""
        return {
            "type": "sysmodel",
            "version": "1.0",
            "exported_at": datetime.datetime.utcnow().isoformat(),
            "config": {
                "name": sys_model.name,
                "title": sys_model.title,
                "description": sys_model.description,
                "status": sys_model.status,
                "permissions": sys_model.permissions,
                "fields": [self._export_field(field) for field in sys_model.fields],
            },
        }

    def _export_field(self, field) -> Dict[str, Any]:
        """Esporta la configurazione di un campo."""
        return {
            "name": field.name,
            "title": field.title,
            "type": field.type,
            "required": field.required,
            "is_unique": field.is_unique,
            "default_value": field.default_value,
            "options": field.options,
            "validation_regex": field.validation_regex,
            "validation_message": field.validation_message,
            "order": field.order,
            "formula": field.formula,
            "summary_expression": field.summary_expression,
        }

    def export_sysmodel_data(self, sys_model, projectId: int) -> Dict[str, Any]:
        """Esporta i dati di un SysModel."""
        from backend.modules.dynamic_api.services.dynamic_api_service import DynamicApiService

        dynamic_api = DynamicApiService()

        # Get all records
        result, _ = dynamic_api.list_records(
            projectId=projectId, model_name=sys_model.name, page=1, per_page=10000
        )

        return {
            "type": "sysmodel_data",
            "version": "1.0",
            "exported_at": datetime.datetime.utcnow().isoformat(),
            "model_name": sys_model.name,
            "record_count": result.get("total", 0),
            "data": result.get("data", []),
        }

    def import_sysmodel_config(
        self, config: Dict[str, Any], projectId: int
    ) -> Dict[str, Any]:
        """Importa la configurazione di un SysModel."""
        from backend.models import SysModel, SysField
        from backend.extensions import db

        data = config.get("config", config)

        # Check if model exists
        existing = SysModel.query.filter_by(
            projectId=projectId, name=data["name"]
        ).first()

        if existing:
            # Update existing
            existing.title = data.get("title", existing.title)
            existing.description = data.get("description", existing.description)
            existing.permissions = data.get("permissions", existing.permissions)

            # Update fields
            for field_data in data.get("fields", []):
                field = SysField.query.filter_by(
                    modelId=existing.id, name=field_data["name"]
                ).first()

                if field:
                    for key, value in field_data.items():
                        if key != "id":
                            setattr(field, key, value)
                else:
                    # Create new field
                    new_field = SysField(
                        modelId=existing.id,
                        **{k: v for k, v in field_data.items() if k != "id"},
                    )
                    db.session.add(new_field)

            db.session.commit()
            return {"action": "updated", "model": existing.name}
        else:
            # Create new model
            new_model = SysModel(
                projectId=projectId,
                name=data["name"],
                title=data.get("title", data["name"]),
                description=data.get("description", ""),
                status="draft",
            )
            db.session.add(new_model)
            db.session.flush()

            # Create fields
            for field_data in data.get("fields", []):
                new_field = SysField(
                    modelId=new_model.id,
                    **{k: v for k, v in field_data.items() if k != "id"},
                )
                db.session.add(new_field)

            db.session.commit()
            return {"action": "created", "model": new_model.name}

    def import_sysmodel_data(
        self, data_json: Dict[str, Any], projectId: int
    ) -> Dict[str, Any]:
        """Importa i dati in un SysModel."""
        from backend.modules.dynamic_api.services.dynamic_api_service import DynamicApiService

        model_name = data_json.get("model_name")
        records = data_json.get("data", [])

        if not model_name:
            raise ValueError("model_name is required")

        dynamic_api = DynamicApiService()

        imported_count = 0
        errors = []

        for record in records:
            try:
                result, status = dynamic_api.create_record(
                    projectId=projectId, model_name=model_name, data=record
                )
                if status in [200, 201]:
                    imported_count += 1
            except Exception as e:
                errors.append({"record": record.get("id", "unknown"), "error": str(e)})

        return {"imported": imported_count, "total": len(records), "errors": errors}

    # ==================== BLOCK ====================

    def export_block_config(self, block) -> Dict[str, Any]:
        """Esporta la configurazione di un Block."""
        return {
            "type": "block",
            "version": "1.0",
            "exported_at": datetime.datetime.utcnow().isoformat(),
            "config": {
                "name": block.name,
                "title": block.title,
                "description": block.description,
                "components": [
                    self._export_component(comp) for comp in block.components
                ]
                if hasattr(block, "components")
                else [],
            },
        }

    def _export_component(self, component) -> Dict[str, Any]:
        """Esporta la configurazione di un componente."""
        return {
            "archetype": component.archetype,
            "title": component.title,
            "config": component.config,
            "order": component.order,
        }

    def export_block_data(self, block) -> Dict[str, Any]:
        """Esporta i dati del block (views, settings)."""
        return {
            "type": "block_data",
            "version": "1.0",
            "exported_at": datetime.datetime.utcnow().isoformat(),
            "block_name": block.name,
            "data": {},
        }

    def import_block_config(
        self, config: Dict[str, Any], projectId: int
    ) -> Dict[str, Any]:
        """Importa la configurazione di un Block."""
        from backend.modules.builder.models import Block, Component
        from backend.extensions import db

        data = config.get("config", config)

        existing = Block.query.filter_by(
            projectId=projectId, name=data["name"]
        ).first()

        if existing:
            existing.title = data.get("title", existing.title)
            existing.description = data.get("description", existing.description)
            db.session.commit()
            return {"action": "updated", "block": existing.name}
        else:
            new_block = Block(
                projectId=projectId,
                name=data["name"],
                title=data.get("title", data["name"]),
                description=data.get("description", ""),
            )
            db.session.add(new_block)
            db.session.flush()

            for comp_data in data.get("components", []):
                new_comp = Component(
                    block_id=new_block.id,
                    archetype=comp_data.get("archetype"),
                    title=comp_data.get("title"),
                    config=comp_data.get("config"),
                    order=comp_data.get("order", 0),
                )
                db.session.add(new_comp)

            db.session.commit()
            return {"action": "created", "block": new_block.name}

    # ==================== WORKFLOW ====================

    def export_workflow_config(self, workflow) -> Dict[str, Any]:
        """Esporta la configurazione di un Workflow."""
        return {
            "type": "workflow",
            "version": "1.0",
            "exported_at": datetime.datetime.utcnow().isoformat(),
            "config": {
                "name": workflow.name,
                "title": workflow.title,
                "description": workflow.description,
                "trigger_event": workflow.trigger_event,
                "steps": workflow.steps,
                "is_active": workflow.is_active,
            },
        }

    def export_workflow_data(self, workflow) -> Dict[str, Any]:
        """Esporta i dati del workflow (execution logs)."""
        return {
            "type": "workflow_data",
            "version": "1.0",
            "exported_at": datetime.datetime.utcnow().isoformat(),
            "workflow_name": workflow.name,
            "execution_count": 0,
            "data": {},
        }

    def import_workflow_config(
        self, config: Dict[str, Any], projectId: int
    ) -> Dict[str, Any]:
        """Importa la configurazione di un Workflow."""
        from backend.models import Workflow
        from backend.extensions import db

        data = config.get("config", config)

        existing = Workflow.query.filter_by(
            projectId=projectId, name=data["name"]
        ).first()

        if existing:
            existing.title = data.get("title", existing.title)
            existing.description = data.get("description", existing.description)
            existing.steps = data.get("steps", existing.steps)
            existing.trigger_event = data.get("trigger_event", existing.trigger_event)
            existing.is_active = data.get("is_active", existing.is_active)
            db.session.commit()
            return {"action": "updated", "workflow": existing.name}
        else:
            new_workflow = Workflow(
                projectId=projectId,
                name=data["name"],
                title=data.get("title", data["name"]),
                description=data.get("description", ""),
                trigger_event=data.get("trigger_event"),
                steps=data.get("steps", []),
                is_active=data.get("is_active", False),
            )
            db.session.add(new_workflow)
            db.session.commit()
            return {"action": "created", "workflow": new_workflow.name}

    # ==================== MODULE ====================

    def export_module_config(self, module) -> Dict[str, Any]:
        """Esporta la configurazione completa di un Module."""
        from backend.modules.builder.models import Block

        models = list(module.models) if hasattr(module, "models") else []
        blocks = list(module.blocks) if hasattr(module, "blocks") else []

        return {
            "type": "module",
            "version": "1.0",
            "exported_at": datetime.datetime.utcnow().isoformat(),
            "config": {
                "name": module.name,
                "title": module.title,
                "description": module.description,
                "type": module.type,
                "category": module.category,
                "version": module.version,
                "api_definition": module.api_definition,
                "dependencies": module.dependencies,
                "models": [m.name for m in models],
                "blocks": [b.name for b in blocks],
            },
        }

    def export_module_data(self, module, projectId: int) -> Dict[str, Any]:
        """Esporta tutti i dati del modulo."""
        from backend.modules.dynamic_api.services.dynamic_api_service import DynamicApiService

        dynamic_api = DynamicApiService()
        models = list(module.models) if hasattr(module, "models") else []

        all_data = {
            "type": "module_data",
            "version": "1.0",
            "exported_at": datetime.datetime.utcnow().isoformat(),
            "module_name": module.name,
            "models": {},
        }

        for model in models:
            try:
                result, _ = dynamic_api.list_records(
                    projectId=projectId, model_name=model.name, page=1, per_page=10000
                )
                all_data["models"][model.name] = {
                    "records": result.get("data", []),
                    "count": result.get("total", 0),
                }
            except Exception as e:
                all_data["models"][model.name] = {"error": str(e)}

        return all_data

    def import_module_config(
        self, config: Dict[str, Any], projectId: int
    ) -> Dict[str, Any]:
        """Importa la configurazione di un Module."""
        from backend.core.models.module import Module
        from backend.extensions import db

        data = config.get("config", config)

        existing = Module.query.filter_by(
            projectId=projectId, name=data["name"]
        ).first()

        if existing:
            existing.title = data.get("title", existing.title)
            existing.description = data.get("description", existing.description)
            existing.version = data.get("version", existing.version)
            existing.api_definition = data.get(
                "api_definition", existing.api_definition
            )
            existing.dependencies = data.get("dependencies", existing.dependencies)
            db.session.commit()
            return {"action": "updated", "module": existing.name}
        else:
            new_module = Module(
                projectId=projectId,
                name=data["name"],
                title=data.get("title", data["name"]),
                description=data.get("description", ""),
                type=data.get("type", "custom"),
                category=data.get("category"),
                version=data.get("version", "1.0.0"),
                status="draft",
                api_definition=data.get("api_definition"),
                dependencies=data.get("dependencies", []),
            )
            db.session.add(new_module)
            db.session.commit()
            return {"action": "created", "module": new_module.name}

    # ==================== PROJECT ====================

    def export_sysmodels_project(self, projectId: int) -> Dict[str, Any]:
        """Esporta tutti i SysModel di un progetto."""
        from backend.models import SysModel

        models = SysModel.query.filter_by(projectId=projectId).all()

        return {
            "type": "sysmodels_project",
            "version": "1.0",
            "exported_at": datetime.datetime.utcnow().isoformat(),
            "projectId": projectId,
            "sysmodels": [self.export_sysmodel_config(m) for m in models],
        }

    def export_project_full(self, projectId: int) -> Dict[str, Any]:
        """Esporta l'intero progetto."""
        from backend.models import Project, SysModel, Workflow
        from backend.modules.builder.models import Block

        project = Project.query.get(projectId)
        if not project:
            raise ValueError("Project not found")

        models = SysModel.query.filter_by(projectId=projectId).all()
        blocks = Block.query.filter_by(projectId=projectId).all()
        workflows = Workflow.query.filter_by(projectId=projectId).all()

        # Get all modules for this project
        from backend.core.models.module import Module

        modules = Module.query.filter_by(projectId=projectId).all()

        export_data = {
            "type": "project",
            "version": "1.0",
            "exported_at": datetime.datetime.utcnow().isoformat(),
            "project": {
                "name": project.name,
                "description": project.description,
                "settings": project.settings,
            },
            "sysmodels": [self.export_sysmodel_config(m) for m in models],
            "blocks": [self.export_block_config(b) for b in blocks],
            "workflows": [self.export_workflow_config(w) for w in workflows],
            "modules": [self.export_module_config(m) for m in modules],
        }

        return export_data

    def import_project_full(
        self, project_json: Dict[str, Any], projectId: int
    ) -> Dict[str, Any]:
        """Importa l'intero progetto."""
        results = {"sysmodels": [], "blocks": [], "workflows": [], "modules": []}

        # Import sysmodels
        for sm in project_json.get("sysmodels", []):
            try:
                result = self.import_sysmodel_config(sm, projectId)
                results["sysmodels"].append(result)
            except Exception as e:
                results["sysmodels"].append({"error": str(e)})

        # Import blocks
        for blk in project_json.get("blocks", []):
            try:
                result = self.import_block_config(blk, projectId)
                results["blocks"].append(result)
            except Exception as e:
                results["blocks"].append({"error": str(e)})

        # Import workflows
        for wf in project_json.get("workflows", []):
            try:
                result = self.import_workflow_config(wf, projectId)
                results["workflows"].append(result)
            except Exception as e:
                results["workflows"].append({"error": str(e)})

        # Import modules
        for mod in project_json.get("modules", []):
            try:
                result = self.import_module_config(mod, projectId)
                results["modules"].append(result)
            except Exception as e:
                results["modules"].append({"error": str(e)})

        return results


# Singleton instance
import_export_service = ImportExportService()
