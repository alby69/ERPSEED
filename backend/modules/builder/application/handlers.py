import os
import csv
import datetime
from sqlalchemy import text, select, desc
from backend.models import SysModel, SysField, AuditLog
from backend.extensions import db
from flask_smorest import abort
from backend.core.utils.utils import log_audit, generate_schema_diff_sql, generate_create_table_sql, get_table_object, serialize_value
from backend.core.events.triggers import on_model_created, on_model_updated, on_model_deleted

class BuilderCommandHandler:
    def handle_create_model(self, cmd):
        existing = SysModel.query.filter_by(projectId=cmd.projectId, name=cmd.name).first()
        if existing:
            abort(409, message=f"Model with name '{cmd.name}' already exists in this project.")

        model = SysModel(
            projectId=cmd.projectId,
            name=cmd.name,
            technical_name=cmd.technical_name or cmd.name,
            table_name=cmd.table_name or cmd.name,
            title=cmd.title,
            description=cmd.description,
            permissions=cmd.permissions
        )
        db.session.add(model)
        db.session.commit()

        try:
            log_audit(None, 'sys_models', model.id, 'CREATE', {'name': cmd.name, 'projectId': cmd.projectId})
            on_model_created(model)
        except Exception:
            pass
        return model

    def handle_update_model(self, cmd):
        model = db.session.get(SysModel, cmd.modelId)
        if not model:
            abort(404, message="Model not found.")

        data = cmd.data
        if "name" in data and data["name"] != model.name:
            existing = SysModel.query.filter(
                SysModel.projectId == model.projectId,
                SysModel.name == data["name"],
                SysModel.id != cmd.modelId
            ).first()
            if existing:
                abort(409, message=f"Model with name '{data['name']}' already exists.")

        for key, value in data.items():
            if hasattr(model, key):
                setattr(model, key, value)

        db.session.commit()
        log_audit(None, 'sys_models', model.id, 'UPDATE', data)
        try:
            on_model_updated(model)
        except Exception:
            pass
        return model

    def handle_delete_model(self, cmd):
        model = db.session.get(SysModel, cmd.modelId)
        if not model:
            abort(404, message="Model not found.")

        model_name = model.name
        log_audit(None, 'sys_models', cmd.modelId, 'DELETE')
        db.session.delete(model)
        db.session.commit()
        try:
            on_model_deleted(cmd.modelId, model_name)
        except Exception:
            pass
        return True

    def handle_create_field(self, cmd):
        existing = SysField.query.filter_by(modelId=cmd.modelId, name=cmd.name).first()
        if existing:
            abort(409, message="Field with this name already exists in the model.")

        field = SysField(
            modelId=cmd.modelId,
            name=cmd.name,
            technical_name=cmd.technical_name or cmd.name,
            type=cmd.field_type,
            title=cmd.title or cmd.name,
            **(cmd.kwargs or {})
        )
        db.session.add(field)
        db.session.commit()
        try:
            log_audit(None, 'sys_fields', field.id, 'CREATE', {'name': cmd.name, 'modelId': cmd.modelId})
        except Exception:
            pass
        return field

    def handle_sync_schema(self, cmd):
        model = db.session.get(SysModel, cmd.modelId)
        if not model:
            abort(404, message="Model not found.")

        schema_name = f"project_{model.projectId}"
        try:
            sql_commands = generate_schema_diff_sql(model, cmd.db_engine, schema=schema_name)
            for sql in sql_commands:
                db.session.execute(text(sql))
            db.session.commit()
            log_audit(None, 'sys_models', cmd.modelId, 'GENERATE_TABLE')
            return sql_commands
        except Exception as e:
            db.session.rollback()
            abort(500, message=f"Error syncing schema: {str(e)}")

    def handle_clone_model(self, cmd):
        source_model = db.session.get(SysModel, cmd.modelId)
        if not source_model:
            abort(404, message="Model not found.")

        existing = SysModel.query.filter_by(projectId=source_model.projectId, name=cmd.new_name).first()
        if existing:
            abort(409, message=f"Model with name '{cmd.new_name}' already exists in this project.")

        new_model = SysModel(
            projectId=source_model.projectId,
            name=cmd.new_name,
            title=cmd.new_title,
            description=source_model.description,
            permissions=source_model.permissions,
            technical_name=cmd.new_name,
            table_name=cmd.new_name
        )
        db.session.add(new_model)
        db.session.flush()

        for field in source_model.fields:
            new_field = SysField(
                modelId=new_model.id,
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
                validation_message=field.validation_message
            )
            db.session.add(new_field)

        db.session.commit()
        log_audit(cmd.userId, 'sys_models', new_model.id, 'CLONE', {'source_id': cmd.modelId})
        return new_model
