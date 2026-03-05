from flask.views import MethodView
from flask import request, current_app, send_from_directory
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import text, select, desc

from ..extensions import db
from ..schemas import (
    SysModelSchema,
    SysFieldSchema,
    AuditLogSchema,
    SysViewSchema,
    SysViewCreateSchema,
    SysComponentSchema,
    SysComponentCreateSchema,
    SysActionSchema,
    SysActionCreateSchema,
)
from ..schemas import SysModelSchema as schemas_module
from ..utils import apply_filters, apply_sorting, paginate
from ..services import BuilderService
from ..decorators import admin_required
from .generator import CodeGenerator, TemplateValidator, AdaptiveBuilder

blp = Blueprint("builder", __name__, description="No-Code Builder Operations")

builder_service = BuilderService()


@blp.route("/sys-models")
class SysModelList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, SysModelSchema(many=True))
    def get(self):
        """List all system models"""
        try:
            items, headers = builder_service.get_all_models(
                search_fields=["name", "title"], sort_by=None, sort_order="asc"
            )
            return items, 200, headers
        except Exception as e:
            import sys
            import traceback

            traceback.print_exc()
            print(f"Error listing SysModels: {e}", file=sys.stderr)
            abort(500, message=f"Internal Server Error: {str(e)}")

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(SysModelSchema)
    @blp.response(201, SysModelSchema)
    def post(self, model_data):
        """Create a new system model"""
        data = model_data.__dict__ if hasattr(model_data, "__dict__") else model_data

        if "project_id" not in data:
            abort(400, message="project_id is required to create a model.")

        return builder_service.create_model(
            project_id=data["project_id"],
            name=data["name"],
            title=data.get("title"),
            description=data.get("description"),
            permissions=data.get("permissions"),
        ), 201


@blp.route("/sys-models/<int:model_id>")
class SysModelResource(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, SysModelSchema)
    def get(self, model_id):
        """Get system model details"""
        return builder_service.get_model(model_id)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(SysModelSchema)
    @blp.response(200, SysModelSchema)
    def put(self, model_data, model_id):
        """Update system model"""
        data = model_data.__dict__ if hasattr(model_data, "__dict__") else model_data
        return builder_service.update_model(model_id, data)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(204)
    def delete(self, model_id):
        """Delete system model"""
        builder_service.delete_model(model_id)
        return ""


@blp.route("/sys-fields")
class SysFieldList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(SysFieldSchema)
    @blp.response(201, SysFieldSchema)
    def post(self, field_data):
        """Add a field to a system model"""
        data = field_data.__dict__ if hasattr(field_data, "__dict__") else field_data

        if "model_id" not in data:
            abort(400, message="model_id is required")

        return builder_service.create_field(
            model_id=data["model_id"],
            name=data["name"],
            field_type=data["type"],
            title=data.get("title"),
            required=data.get("required"),
            is_unique=data.get("is_unique"),
            default_value=data.get("default_value"),
            options=data.get("options"),
            order=data.get("order", 0),
            formula=data.get("formula"),
            summary_expression=data.get("summary_expression"),
            validation_regex=data.get("validation_regex"),
            validation_message=data.get("validation_message"),
        ), 201


@blp.route("/sys-fields/<int:field_id>")
class SysFieldResource(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(SysFieldSchema)
    @blp.response(200, SysFieldSchema)
    def put(self, field_data, field_id):
        """Update a system field"""
        data = field_data.__dict__ if hasattr(field_data, "__dict__") else field_data
        return builder_service.update_field(field_id, data)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(204)
    def delete(self, field_id):
        """Delete a system field"""
        builder_service.delete_field(field_id)
        return ""


@blp.route("/sys-models/<int:model_id>/generate-table")
class SysModelSyncSchema(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200)
    def post(self, model_id):
        """Generate and execute CREATE or ALTER TABLE SQL to sync the DB with the model"""
        sql_commands, message = builder_service.sync_schema(model_id, db.engine)

        if not sql_commands:
            return {"message": message}
        return {"message": message}


@blp.route("/sys-models/<int:model_id>/reset-table")
class SysModelResetTable(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200)
    def post(self, model_id):
        """Drop and Re-create the table based on metadata (DATA LOSS WARNING)"""
        user_id = get_jwt_identity()

        backup_folder = current_app.config.get("BACKUP_FOLDER", "backups")

        message = builder_service.reset_table(model_id, user_id, backup_folder)

        return {"message": message}


@blp.route("/sys-models/<int:model_id>/clone")
class SysModelClone(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self, model_id):
        """Clone an existing model (definition and fields)."""
        user_id = get_jwt_identity()

        data = request.get_json()
        new_name = data.get("name")
        new_title = data.get("title")

        if not new_name or not new_title:
            abort(400, message="Name and Title are required.")

        new_model = builder_service.clone_model(model_id, user_id, new_name, new_title)

        return SysModelSchema().dump(new_model), 201


@blp.route("/sys-models/<int:model_id>/backups")
class SysModelBackups(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, model_id):
        """List available backups for a specific model"""
        backup_folder = current_app.config.get("BACKUP_FOLDER", "backups")

        backups = builder_service.get_backups(model_id, backup_folder)

        return backups


@blp.route("/backups/<string:filename>")
class BackupDownload(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, filename):
        """Download a specific backup file"""
        backup_folder = current_app.config.get("BACKUP_FOLDER", "backups")
        import os

        abs_backup_folder = os.path.abspath(backup_folder)

        return send_from_directory(abs_backup_folder, filename, as_attachment=True)


@blp.route("/audit-logs")
class AuditLogList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, AuditLogSchema(many=True))
    def get(self):
        """Retrieve audit logs (admin only)."""
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)

        items, total = builder_service.get_audit_logs(page, per_page)

        return items


@blp.route("/sys-models/<int:model_id>/generate-code")
class SysModelGenerateCode(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, model_id):
        """Generate Python code from model definition."""
        model = builder_service.get_model(model_id)
        if not model:
            abort(404, message="Model not found.")

        validator = TemplateValidator()
        errors = validator.validate(model)
        if errors:
            abort(400, message=f"Validation errors: {', '.join(errors)}")

        generator = CodeGenerator()

        api_prefix = request.args.get("api_prefix", "/api")

        code = generator.generate_module(model, api_prefix)

        return {"model": model.name, "code": code}


@blp.route("/sys-models/<int:model_id>/validate")
class SysModelValidate(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, model_id):
        """Validate model definition."""
        model = builder_service.get_model(model_id)
        if not model:
            abort(404, message="Model not found.")

        validator = TemplateValidator()
        errors = validator.validate(model)

        return {"valid": len(errors) == 0, "errors": errors}


@blp.route("/projects/<int:project_id>/business-rules")
class BusinessRulesList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, project_id):
        """List all business rules for a project."""
        from ..models import SysModel
        import json

        models = SysModel.query.filter_by(
            project_id=project_id, status="published"
        ).all()

        all_rules = []
        for model in models:
            if model.tool_options:
                try:
                    opts = json.loads(model.tool_options)
                    hooks = opts.get("hooks", [])
                    for hook in hooks:
                        all_rules.append(
                            {
                                "id": hook.get("id"),
                                "model_name": model.name,
                                "model_title": model.title,
                                "hook_type": hook.get("hook_type"),
                                "rule_name": hook.get("rule_name"),
                                "rule_logic": hook.get("rule_logic"),
                                "enabled": hook.get("enabled", True),
                                "condition": hook.get("condition"),
                                "action": hook.get("action"),
                            }
                        )
                except (json.JSONDecodeError, AttributeError):
                    pass

        return {"rules": all_rules}

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self, project_id):
        """Create a business rule."""
        from ..models import SysModel
        import json
        from datetime import datetime

        data = request.get_json()

        model_name = data.get("model_name")
        if not model_name:
            abort(400, message="model_name is required.")

        model = SysModel.query.filter_by(project_id=project_id, name=model_name).first()

        if not model:
            abort(404, message=f"Model '{model_name}' not found.")

        tool_options = {}
        if model.tool_options:
            try:
                tool_options = json.loads(model.tool_options)
            except json.JSONDecodeError:
                pass

        if "hooks" not in tool_options:
            tool_options["hooks"] = []

        existing_ids = [h.get("id", 0) for h in tool_options["hooks"]]
        new_id = max(existing_ids, default=0) + 1

        rule = {
            "id": new_id,
            "hook_type": data.get("hook_type"),
            "rule_name": data.get("rule_name", f"Rule_{new_id}"),
            "rule_logic": data.get("rule_logic", ""),
            "condition": data.get("condition"),
            "action": data.get("action"),
            "enabled": True,
            "created_at": datetime.utcnow().isoformat(),
        }

        tool_options["hooks"].append(rule)
        model.tool_options = json.dumps(tool_options)
        db.session.commit()

        return {"success": True, "rule_id": new_id}, 201


@blp.route("/projects/<int:project_id>/business-rules/<int:rule_id>")
class BusinessRuleDetail(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def delete(self, project_id, rule_id):
        """Delete a business rule."""
        from ..models import SysModel
        import json

        data = request.get_json()
        model_name = data.get("model_name")

        if not model_name:
            abort(400, message="model_name is required in request body.")

        model = SysModel.query.filter_by(project_id=project_id, name=model_name).first()

        if not model:
            abort(404, message=f"Model '{model_name}' not found.")

        tool_options = {}
        if model.tool_options:
            try:
                tool_options = json.loads(model.tool_options)
            except json.JSONDecodeError:
                pass

        hooks = tool_options.get("hooks", [])
        tool_options["hooks"] = [h for h in hooks if h.get("id") != rule_id]

        model.tool_options = json.dumps(tool_options)
        db.session.commit()

        return {"success": True, "message": f"Rule {rule_id} deleted"}


@blp.route("/sys-views")
class SysViewList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, SysViewSchema(many=True))
    def get(self):
        """List all system views"""
        from ..models import SysView, SysModel

        project_id = request.args.get("project_id")
        model_id = request.args.get("model_id")

        query = SysView.query
        if project_id:
            query = query.join(SysModel).filter(SysModel.project_id == project_id)
        if model_id:
            query = query.filter(SysView.model_id == model_id)

        return query.order_by(SysView.order).all()

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(SysViewCreateSchema)
    @blp.response(201, SysViewSchema)
    def post(self, view_data):
        """Create a new system view"""
        data = view_data.__dict__ if hasattr(view_data, "__dict__") else view_data
        from ..models import SysView

        view = SysView()
        view.name = data.get("name")
        view.technical_name = data.get("technical_name", data.get("name"))
        view.title = data.get("title", data.get("name"))
        view.view_type = data.get("view_type", "list")
        view.model_id = data.get("model_id")
        view.config = data.get("config", "{}")
        view.is_default = data.get("is_default", False)
        view.is_active = data.get("is_active", True)
        view.order = data.get("order", 0)

        db.session.add(view)
        db.session.commit()
        return view, 201


@blp.route("/sys-views/<int:view_id>")
class SysViewResource(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, SysViewSchema)
    def get(self, view_id):
        """Get system view details"""
        from ..models import SysView

        view = SysView.query.get_or_404(view_id)
        return view

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(SysViewCreateSchema)
    @blp.response(200, SysViewSchema)
    def put(self, view_data, view_id):
        """Update system view"""
        from ..models import SysView

        view = SysView.query.get_or_404(view_id)
        data = view_data.__dict__ if hasattr(view_data, "__dict__") else view_data

        for key, value in data.items():
            if hasattr(view, key) and key not in ("id", "created_at"):
                setattr(view, key, value)

        db.session.commit()
        return view

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(204)
    def delete(self, view_id):
        """Delete system view"""
        from ..models import SysView

        view = SysView.query.get_or_404(view_id)
        db.session.delete(view)
        db.session.commit()
        return ""


@blp.route("/sys-components")
class SysComponentList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, SysComponentSchema(many=True))
    def get(self):
        """List all system components"""
        from ..models import SysComponent

        return SysComponent.query.filter_by(is_active=True).all()

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(SysComponentCreateSchema)
    @blp.response(201, SysComponentSchema)
    def post(self, component_data):
        """Create a new system component"""
        data = (
            component_data.__dict__
            if hasattr(component_data, "__dict__")
            else component_data
        )
        from ..models import SysComponent

        component = SysComponent()
        component.name = data.get("name")
        component.technical_name = data.get("technical_name", data.get("name"))
        component.title = data.get("title", data.get("name"))
        component.description = data.get("description", "")
        component.component_type = data.get("component_type", "custom")
        component.component_path = data.get("component_path", "")
        component.default_config = data.get("default_config", "{}")
        component.props_schema = data.get("props_schema", "{}")
        component.icon = data.get("icon", "component")
        component.is_custom = True
        component.is_active = True

        db.session.add(component)
        db.session.commit()
        return component, 201


@blp.route("/sys-components/<int:component_id>")
class SysComponentResource(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, SysComponentSchema)
    def get(self, component_id):
        """Get system component details"""
        from ..models import SysComponent

        component = SysComponent.query.get_or_404(component_id)
        return component

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(SysComponentCreateSchema)
    @blp.response(200, SysComponentSchema)
    def put(self, component_data, component_id):
        """Update system component"""
        from ..models import SysComponent

        component = SysComponent.query.get_or_404(component_id)
        data = (
            component_data.__dict__
            if hasattr(component_data, "__dict__")
            else component_data
        )

        for key, value in data.items():
            if hasattr(component, key) and key not in ("id", "created_at"):
                setattr(component, key, value)

        db.session.commit()
        return component

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(204)
    def delete(self, component_id):
        """Delete system component"""
        from ..models import SysComponent

        component = SysComponent.query.get_or_404(component_id)
        db.session.delete(component)
        db.session.commit()
        return ""


@blp.route("/sys-actions")
class SysActionList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, SysActionSchema(many=True))
    def get(self):
        """List all system actions"""
        from ..models import SysAction

        view_id = request.args.get("view_id")
        model_id = request.args.get("model_id")

        query = SysAction.query
        if view_id:
            query = query.filter(SysAction.view_id == view_id)
        if model_id:
            query = query.filter(SysAction.model_id == model_id)

        return query.filter_by(is_active=True).order_by(SysAction.order).all()

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(SysActionCreateSchema)
    @blp.response(201, SysActionSchema)
    def post(self, action_data):
        """Create a new system action"""
        data = action_data.__dict__ if hasattr(action_data, "__dict__") else action_data
        from ..models import SysAction

        action = SysAction()
        action.name = data.get("name")
        action.technical_name = data.get("technical_name", data.get("name"))
        action.title = data.get("title", data.get("name"))
        action.action_type = data.get("action_type", "button")
        action.target = data.get("target", "api")
        action.view_id = data.get("view_id")
        action.model_id = data.get("model_id")
        action.config = data.get("config", "{}")
        action.icon = data.get("icon")
        action.style = data.get("style", "primary")
        action.position = data.get("position", "toolbar")
        action.conditions = data.get("conditions", "{}")
        action.is_active = True
        action.order = data.get("order", 0)

        db.session.add(action)
        db.session.commit()
        return action, 201


@blp.route("/sys-actions/<int:action_id>")
class SysActionResource(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, SysActionSchema)
    def get(self, action_id):
        """Get system action details"""
        from ..models import SysAction

        action = SysAction.query.get_or_404(action_id)
        return action

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(SysActionCreateSchema)
    @blp.response(200, SysActionSchema)
    def put(self, action_data, action_id):
        """Update system action"""
        from ..models import SysAction

        action = SysAction.query.get_or_404(action_id)
        data = action_data.__dict__ if hasattr(action_data, "__dict__") else action_data

        for key, value in data.items():
            if hasattr(action, key) and key not in ("id", "created_at"):
                setattr(action, key, value)

        db.session.commit()
        return action

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(204)
    def delete(self, action_id):
        """Delete system action"""
        from ..models import SysAction

        action = SysAction.query.get_or_404(action_id)
        db.session.delete(action)
        db.session.commit()
        return ""


@blp.route("/component-registry")
class ComponentRegistryResource(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        """Get component registry (built-in + custom)"""
        from ..models import SysComponent
        from ..view_renderer import get_registry as get_view_renderer_registry
        from ..view_renderer.component_registry import ComponentRegistry

        registry = get_view_renderer_registry()

        custom_components = SysComponent.query.filter_by(is_active=True).all()
        if custom_components:
            custom_registry = ComponentRegistry.from_database(custom_components)
            for comp in custom_registry.get_all():
                registry.register(comp)

        return registry.to_dict()


__all__ = ["blp", "CodeGenerator", "TemplateValidator", "AdaptiveBuilder"]
