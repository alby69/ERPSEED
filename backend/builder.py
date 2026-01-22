from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
import sys
from sqlalchemy import text
import json
from .models import SysModel, SysField, User, AuditLog
from .extensions import db
from .schemas import SysModelSchema, SysFieldSchema
from .utils import apply_filters, paginate, apply_sorting, generate_schema_diff_sql, log_audit

blp = Blueprint("builder", __name__, description="No-Code Builder Operations")

@blp.route("/sys-models")
class SysModelList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, SysModelSchema(many=True))
    def get(self):
        """List all system models"""
        try:
            query = SysModel.query
            query = apply_filters(query, SysModel, ['name', 'title'])
            query = apply_sorting(query, SysModel)
            items, headers = paginate(query)
            
            # Trigger lazy loading of fields to catch potential DB errors within this try block
            if items:
                _ = items[0].fields
                
            return items, 200, headers
        except Exception as e:
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
        if SysModel.query.filter_by(name=model_data["name"]).first():
            abort(409, message="Model with this name already exists.")
        
        model = SysModel(**model_data)
        db.session.add(model)
        db.session.commit()
        log_audit(get_jwt_identity(), 'sys_models', model.id, 'CREATE', model_data)
        return model

@blp.route("/sys-models/<int:model_id>")
class SysModelResource(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, SysModelSchema)
    def get(self, model_id):
        """Get system model details"""
        return SysModel.query.filter(SysModel.id == model_id).first_or_404()

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(SysModelSchema)
    @blp.response(200, SysModelSchema)
    def put(self, model_data, model_id):
        """Update system model"""
        model = SysModel.query.filter(SysModel.id == model_id).first_or_404()
        
        if "name" in model_data and model_data["name"] != model.name:
            if SysModel.query.filter_by(name=model_data["name"]).first():
                abort(409, message="Model with this name already exists.")

        for key, value in model_data.items():
            setattr(model, key, value)
            
        db.session.commit()
        log_audit(get_jwt_identity(), 'sys_models', model.id, 'UPDATE', model_data)
        return model

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(204)
    def delete(self, model_id):
        """Delete system model"""
        model = SysModel.query.get_or_404(model_id)
        db.session.delete(model)
        log_audit(get_jwt_identity(), 'sys_models', model_id, 'DELETE')
        db.session.commit()
        return ""

@blp.route("/sys-fields")
class SysFieldList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(SysFieldSchema)
    @blp.response(201, SysFieldSchema)
    def post(self, field_data):
        """Add a field to a system model"""
        if "model_id" not in field_data:
             abort(400, message="model_id is required")
             
        if SysField.query.filter_by(model_id=field_data["model_id"], name=field_data["name"]).first():
            abort(409, message="Field with this name already exists in the model.")

        field = SysField(**field_data)
        db.session.add(field)
        db.session.commit()
        log_audit(get_jwt_identity(), 'sys_fields', field.id, 'CREATE', field_data)
        return field

@blp.route("/sys-fields/<int:field_id>")
class SysFieldResource(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(SysFieldSchema)
    @blp.response(200, SysFieldSchema)
    def put(self, field_data, field_id):
        """Update a system field"""
        field = SysField.query.get_or_404(field_id)
        
        if "name" in field_data and field_data["name"] != field.name:
             if SysField.query.filter_by(model_id=field.model_id, name=field_data["name"]).first():
                abort(409, message="Field with this name already exists in the model.")

        for key, value in field_data.items():
            setattr(field, key, value)
            
        db.session.commit()
        log_audit(get_jwt_identity(), 'sys_fields', field.id, 'UPDATE', field_data)
        return field

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(204)
    def delete(self, field_id):
        """Delete a system field"""
        field = SysField.query.get_or_404(field_id)
        db.session.delete(field)
        log_audit(get_jwt_identity(), 'sys_fields', field_id, 'DELETE')
        db.session.commit()
        return ""

@blp.route("/sys-models/<int:model_id>/generate-table")
class SysModelSyncSchema(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200)
    def post(self, model_id):
        """Generate and execute CREATE or ALTER TABLE SQL to sync the DB with the model"""
        model = SysModel.query.get_or_404(model_id)
        
        try:
            sql_commands = generate_schema_diff_sql(model, db.engine)
            for sql in sql_commands:
                db.session.execute(text(sql))
            db.session.commit()
            log_audit(get_jwt_identity(), 'sys_models', model_id, 'GENERATE_TABLE')
        except Exception as e:
            db.session.rollback()
            abort(500, message=f"Error syncing schema: {str(e)}")
            
        if not sql_commands:
            return {"message": f"Schema for table '{model.name}' is already up to date."}
        return {"message": f"Schema for table '{model.name}' synced successfully."}

@blp.route("/sys-models/<int:model_id>/clone")
class SysModelClone(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self, model_id):
        """Clona un modello esistente (definizione e campi)."""
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Solo gli admin possono clonare modelli di sistema
        if user.role != 'admin':
             abort(403, message="Only admins can clone models.")

        source_model = SysModel.query.filter(SysModel.id == model_id).first_or_404()
        
        data = request.get_json()
        new_name = data.get('name')
        new_title = data.get('title')
        
        if not new_name or not new_title:
            abort(400, message="Name and Title are required.")
            
        if SysModel.query.filter_by(name=new_name).first():
            abort(409, message=f"Model with name '{new_name}' already exists.")

        # 1. Clona il Modello
        new_model = SysModel(
            name=new_name,
            title=new_title,
            description=source_model.description,
            permissions=source_model.permissions
        )
        db.session.add(new_model)
        db.session.flush() # Per ottenere il nuovo ID

        # 2. Clona i Campi
        for field in source_model.fields:
            new_field = SysField(
                model_id=new_model.id,
                name=field.name,
                title=field.title,
                type=field.type,
                required=field.required,
                options=field.options,
                order=field.order,
                default_value=field.default_value,
                formula=field.formula,
                summary_expression=field.summary_expression,
                is_unique=field.is_unique,
                validation_regex=field.validation_regex,
                validation_message=field.validation_message,
                tooltip=field.tooltip
            )
            db.session.add(new_field)
        
        db.session.commit()
        log_audit(user_id, 'sys_models', new_model.id, 'CLONE', {'source_id': model_id})
        
        return SysModelSchema().dump(new_model), 201