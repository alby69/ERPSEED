"""
Builder Service - Handles No-Code Builder business logic.

DEPRECATED: Use backend.endpoints.builder for REST API or migrate to CQRS pattern.
This service is kept for backward compatibility with TemplateService.
"""
import os
import csv
import datetime
from sqlalchemy import text, select, desc

from .base import BaseService


class BuilderService(BaseService):
    """
    Service for managing dynamic models and fields (No-Code Builder).
    Handles schema generation, backups, and model cloning.
    """

    def get_all_models(self, search_fields=None, sort_by=None, sort_order='asc'):
        """
        Get all system models with optional filtering and sorting.

        Args:
            search_fields: List of field names to search in.
            sort_by: Field to sort by.
            sort_order: 'asc' or 'desc'.

        Returns:
            Tuple of (models, pagination_headers).
        """
        from ..models import SysModel
        from ..utils import apply_filters, apply_sorting, paginate

        query = SysModel.query

        if search_fields:
            query = apply_filters(query, SysModel, search_fields)

        if sort_by:
            query = apply_sorting(query, SysModel)

        items, headers = paginate(query)

        if items:
            try:
                _ = items[0].fields
            except Exception as e:
                pass

        return items, headers

    def get_model(self, model_id):
        """
        Get a single model by ID.

        Args:
            model_id: ID of the model.

        Returns:
            SysModel instance with fields loaded.
        """
        from ..models import SysModel
        from sqlalchemy.orm import joinedload

        # Eagerly load the fields relationship
        return self.db.session.query(SysModel).options(
            joinedload(SysModel.fields)
        ).get(model_id)

    def create_model(self, project_id, name, title, description=None, permissions=None, technical_name=None, table_name=None):
        """
        Create a new model definition.

        Args:
            project_id: ID of the project this model belongs to.
            name: Internal name of the model.
            title: Display title.
            description: Optional description.
            permissions: JSON string for ACL.
            technical_name: Full technical name (optional).
            table_name: Database table name (optional).

        Returns:
            Newly created SysModel.

        Raises:
            409: If model name already exists in project.
        """
        from ..models import SysModel

        existing = SysModel.query.filter_by(
            project_id=project_id,
            name=name
        ).first()

        if existing:
            from flask_smorest import abort
            abort(409, message=f"Model with name '{name}' already exists in this project.")

        model = SysModel(
            project_id=project_id,
            name=name,
            technical_name=technical_name or name,
            table_name=table_name or name,
            title=title,
            description=description,
            permissions=permissions
        )

        self.db.session.add(model)
        self.db.session.commit()

        try:
            from ..utils import log_audit
            log_audit(None, 'sys_models', model.id, 'CREATE', {'name': name, 'project_id': project_id})
        except Exception:
            pass

        try:
            from ..webhook_triggers import on_model_created
            on_model_created(model)
        except Exception:
            pass

        return model

    def update_model(self, model_id, data):
        """
        Update an existing model.

        Args:
            model_id: ID of the model.
            data: Dictionary of fields to update.

        Returns:
            Updated SysModel.

        Raises:
            409: If new name conflicts with existing model.
        """
        from ..models import SysModel

        model = self.db.session.get(SysModel, model_id)
        if not model:
            from flask_smorest import abort
            abort(404, message="Model not found.")

        if "name" in data and data["name"] != model.name:
            existing = SysModel.query.filter(
                SysModel.project_id == model.project_id,
                SysModel.name == data["name"],
                SysModel.id != model_id
            ).first()

            if existing:
                from flask_smorest import abort
                abort(409, message=f"Model with name '{data['name']}' already exists.")

        for key, value in data.items():
            if hasattr(model, key):
                setattr(model, key, value)

        self.db.session.commit()

        from ..utils import log_audit
        log_audit(None, 'sys_models', model.id, 'UPDATE', data)

        try:
            from ..webhook_triggers import on_model_updated
            on_model_updated(model)
        except Exception:
            pass

        return model

    def delete_model(self, model_id):
        """
        Delete a model and its metadata.

        Args:
            model_id: ID of the model to delete.
        """
        from ..models import SysModel

        model = self.db.session.get(SysModel, model_id)
        if not model:
            from flask_smorest import abort
            abort(404, message="Model not found.")

        model_name = model.name
        from ..utils import log_audit
        log_audit(None, 'sys_models', model_id, 'DELETE')

        self.db.session.delete(model)
        self.db.session.commit()

        try:
            from ..webhook_triggers import on_model_deleted
            on_model_deleted(model_id, model_name)
        except Exception:
            pass

    def create_field(self, model_id, name, field_type, title=None, technical_name=None, **kwargs):
        """
        Add a field to a model.

        Args:
            model_id: ID of the model.
            name: Field name.
            field_type: Type of field (string, integer, etc.).
            title: Display title.
            technical_name: Technical name in DB.
            **kwargs: Additional field options.

        Returns:
            Newly created SysField.

        Raises:
            409: If field name already exists.
        """
        from ..models import SysField

        existing = SysField.query.filter_by(
            model_id=model_id,
            name=name
        ).first()

        if existing:
            from flask_smorest import abort
            abort(409, message="Field with this name already exists in the model.")

        field = SysField(
            model_id=model_id,
            name=name,
            technical_name=technical_name or name,
            type=field_type,
            title=title or name,
            **kwargs
        )

        self.db.session.add(field)
        self.db.session.commit()

        try:
            from ..utils import log_audit
            log_audit(None, 'sys_fields', field.id, 'CREATE', {'name': name, 'model_id': model_id})
        except Exception:
            pass

        return field

    def update_field(self, field_id, data):
        """
        Update a field.

        Args:
            field_id: ID of the field.
            data: Dictionary of fields to update.

        Returns:
            Updated SysField.
        """
        from ..models import SysField

        field = self.db.session.get(SysField, field_id)
        if not field:
            from flask_smorest import abort
            abort(404, message="Field not found.")

        if "name" in data and data["name"] != field.name:
            existing = SysField.query.filter_by(
                model_id=field.model_id,
                name=data["name"]
            ).first()

            if existing:
                from flask_smorest import abort
                abort(409, message="Field with this name already exists.")

        for key, value in data.items():
            if hasattr(field, key):
                setattr(field, key, value)

        self.db.session.commit()

        from ..utils import log_audit
        log_audit(None, 'sys_fields', field.id, 'UPDATE', data)

        return field

    def delete_field(self, field_id):
        """
        Delete a field.

        Args:
            field_id: ID of the field to delete.
        """
        from ..models import SysField

        field = self.db.session.get(SysField, field_id)
        if not field:
            from flask_smorest import abort
            abort(404, message="Field not found.")

        from ..utils import log_audit
        log_audit(None, 'sys_fields', field_id, 'DELETE')

        self.db.session.delete(field)
        self.db.session.commit()

    def sync_schema(self, model_id, db_engine):
        """
        Sync model definition to database schema.

        Args:
            model_id: ID of the model to sync.
            db_engine: SQLAlchemy engine.

        Returns:
            List of SQL commands executed.
        """
        from ..models import SysModel
        from ..utils import generate_schema_diff_sql, log_audit

        model = self.db.session.get(SysModel, model_id)
        if not model:
            from flask_smorest import abort
            abort(404, message="Model not found.")

        schema_name = f"project_{model.project_id}"

        try:
            sql_commands = generate_schema_diff_sql(model, db_engine, schema=schema_name)

            for sql in sql_commands:
                self.db.session.execute(text(sql))

            self.db.session.commit()
            log_audit(None, 'sys_models', model_id, 'GENERATE_TABLE')

            if not sql_commands:
                return [], f"Schema for table '{model.name}' is already up to date."

            return sql_commands, f"Schema for table '{model.name}' synced successfully."

        except Exception as e:
            self.db.session.rollback()
            from flask_smorest import abort
            abort(500, message=f"Error syncing schema: {str(e)}")

    def reset_table(self, model_id, user_id, backup_folder='backups'):
        """
        Drop and recreate table with backup.

        Args:
            model_id: ID of the model.
            user_id: ID of the user performing the action.
            backup_folder: Folder to store backups.

        Returns:
            Success message.

        Warning:
            This will delete all data in the table!
        """
        from ..models import SysModel
        from ..utils import get_table_object, serialize_value, log_audit
        from flask import current_app
        import os

        model = self.db.session.get(SysModel, model_id)
        if not model:
            from flask_smorest import abort
            abort(404, message="Model not found.")

        schema_name = f"project_{model.project_id}"
        backup_path = None

        try:
            table = get_table_object(model.name, schema=schema_name)
            data_to_backup = self.db.session.execute(select(table)).mappings().all()

            if data_to_backup:
                os.makedirs(backup_folder, exist_ok=True)

                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{model.name}_{timestamp}.csv"
                backup_filepath = os.path.join(backup_folder, filename)

                headers = data_to_backup[0].keys()

                serialized_data = []
                for row in data_to_backup:
                    serialized_data.append({k: serialize_value(v) for k, v in row.items()})

                with open(backup_filepath, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=headers)
                    writer.writeheader()
                    writer.writerows(serialized_data)

                backup_path = backup_filepath

        except Exception as e:
            from flask_smorest import abort
            abort(500, message=f"Failed to create backup before reset: {str(e)}")

        try:
            from ..utils import generate_create_table_sql

            self.db.session.execute(text(f'DROP TABLE IF EXISTS "{schema_name}"."{model.name}" CASCADE'))
            sql = generate_create_table_sql(model, schema=schema_name)
            self.db.session.execute(text(sql))
            self.db.session.commit()

            log_audit(user_id, 'sys_models', model_id, 'RESET_TABLE', {'backup_path': backup_path})

            success_message = f"Table '{model.name}' has been dropped and recreated."
            if backup_path:
                success_message += f" A backup was saved to '{backup_path}'."

            return success_message

        except Exception as e:
            self.db.session.rollback()
            from flask_smorest import abort
            abort(500, message=f"Error resetting table: {str(e)}")

    def clone_model(self, model_id, user_id, new_name, new_title):
        """
        Clone an existing model with all its fields.

        Args:
            model_id: ID of the model to clone.
            user_id: ID of the user performing the action.
            new_name: Name for the new model.
            new_title: Title for the new model.

        Returns:
            Newly created SysModel.
        """
        from ..models import SysModel, SysField
        from ..utils import log_audit

        source_model = self.db.session.get(SysModel, model_id)
        if not source_model:
            from flask_smorest import abort
            abort(404, message="Model not found.")

        existing = SysModel.query.filter_by(
            project_id=source_model.project_id,
            name=new_name
        ).first()

        if existing:
            from flask_smorest import abort
            abort(409, message=f"Model with name '{new_name}' already exists in this project.")

        new_model = SysModel(
            project_id=source_model.project_id,
            name=new_name,
            title=new_title,
            description=source_model.description,
            permissions=source_model.permissions
        )

        self.db.session.add(new_model)
        self.db.session.flush()

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
                validation_message=field.validation_message
            )
            self.db.session.add(new_field)

        self.db.session.commit()

        log_audit(user_id, 'sys_models', new_model.id, 'CLONE', {'source_id': model_id})

        return new_model

    def get_backups(self, model_id, backup_folder='backups'):
        """
        Get list of backup files for a model.

        Args:
            model_id: ID of the model.
            backup_folder: Folder where backups are stored.

        Returns:
            List of backup filenames.
        """
        from ..models import SysModel

        model = self.db.session.get(SysModel, model_id)
        if not model:
            from flask_smorest import abort
            abort(404, message="Model not found.")

        if not os.path.exists(backup_folder):
            return []

        backups = []
        prefix = f"{model.name}_"

        try:
            for f in os.listdir(backup_folder):
                if f.startswith(prefix) and f.endswith(".csv"):
                    backups.append(f)
        except OSError:
            return []

        backups.sort(reverse=True)
        return backups

    def get_audit_logs(self, page=1, per_page=20):
        """
        Get audit logs.

        Args:
            page: Page number.
            per_page: Items per page.

        Returns:
            Tuple of (logs, total_count).
        """
        from ..models import AuditLog

        query = AuditLog.query.order_by(desc(AuditLog.timestamp))
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return pagination.items, pagination.total
