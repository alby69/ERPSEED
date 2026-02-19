from flask.views import MethodView
from flask import request, current_app, send_from_directory
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import text, select, desc

from ..extensions import db
from ..schemas import SysModelSchema, SysFieldSchema, AuditLogSchema
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
                search_fields=['name', 'title'],
                sort_by=None,
                sort_order='asc'
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
        data = model_data.__dict__ if hasattr(model_data, '__dict__') else model_data
        
        if "project_id" not in data:
            abort(400, message="project_id is required to create a model.")
        
        return builder_service.create_model(
            project_id=data['project_id'],
            name=data['name'],
            title=data.get('title'),
            description=data.get('description'),
            permissions=data.get('permissions')
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
        data = model_data.__dict__ if hasattr(model_data, '__dict__') else model_data
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
        data = field_data.__dict__ if hasattr(field_data, '__dict__') else field_data
        
        if "model_id" not in data:
            abort(400, message="model_id is required")
        
        return builder_service.create_field(
            model_id=data['model_id'],
            name=data['name'],
            field_type=data['type'],
            title=data.get('title'),
            required=data.get('required'),
            is_unique=data.get('is_unique'),
            default_value=data.get('default_value'),
            options=data.get('options'),
            order=data.get('order', 0),
            formula=data.get('formula'),
            summary_expression=data.get('summary_expression'),
            validation_regex=data.get('validation_regex'),
            validation_message=data.get('validation_message')
        ), 201


@blp.route("/sys-fields/<int:field_id>")
class SysFieldResource(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(SysFieldSchema)
    @blp.response(200, SysFieldSchema)
    def put(self, field_data, field_id):
        """Update a system field"""
        data = field_data.__dict__ if hasattr(field_data, '__dict__') else field_data
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
        
        backup_folder = current_app.config.get('BACKUP_FOLDER', 'backups')
        
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
        new_name = data.get('name')
        new_title = data.get('title')
        
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
        backup_folder = current_app.config.get('BACKUP_FOLDER', 'backups')
        
        backups = builder_service.get_backups(model_id, backup_folder)
        
        return backups


@blp.route("/backups/<string:filename>")
class BackupDownload(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, filename):
        """Download a specific backup file"""
        backup_folder = current_app.config.get('BACKUP_FOLDER', 'backups')
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
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
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
        
        api_prefix = request.args.get('api_prefix', '/api')
        
        code = generator.generate_module(model, api_prefix)
        
        return {
            "model": model.name,
            "code": code
        }


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
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }


__all__ = ['blp', 'CodeGenerator', 'TemplateValidator', 'AdaptiveBuilder']
