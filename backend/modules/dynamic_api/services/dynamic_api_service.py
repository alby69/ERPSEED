"""
Dynamic API Service
-------------------
This service handles dynamic CRUD operations for models created via the No-Code Builder.
It manages schema resolution, data validation, file uploads, nested writes (master-detail),
and provides advanced querying capabilities including filtering, sorting, and pagination.

Key features:
- Multi-tenant data isolation (via schema-per-project)
- Role-based access control per model
- Automatic handling of relations and formulas
- CSV Import/Export functionality
"""

import json
import csv
import io
import datetime
from sqlalchemy import (
    select,
    insert,
    update,
    delete,
    func,
    or_,
    desc,
    asc,
    String,
    Text,
)
from werkzeug.utils import secure_filename
from flask import request, current_app
from flask_jwt_extended import get_jwt_identity

from backend.core.services.base import BaseService
from backend.core.utils.utils import get_table_object, serialize_value, log_audit

from .dynamic.field_validator import FieldValidator
from .dynamic.query_builder import QueryBuilder
from .dynamic.result_processor import ResultProcessor


class DynamicApiService(BaseService):
    """
    Service for dynamic CRUD operations on builder-created models.
    Orchestrates specialized components for validation, querying, and processing.
    """

    def check_permissions(self, sys_model, action, projectId=None):
        """
        Verifies if the current user has permission to perform a specific action on a model.

        Args:
            sys_model: The SysModel instance.
            action (str): The action to check ('read' or 'write').
            projectId (int, optional): The project ID to verify ownership.

        Raises:
            HTTPException: 401 (Unauthorized), 403 (Forbidden), or 404 (Not Found).
        """
        from backend.models.user import User
        from flask_smorest import abort

        if projectId is not None and sys_model.projectId != projectId:
            abort(404, message=f"Model '{sys_model.name}' not found in project {projectId}.")

        userId = get_jwt_identity()
        user = self.db.session.get(User, userId)

        if not user:
            abort(401, message="User not found.")

        if user.role == "admin":
            return

        if not sys_model.permissions:
            return

        try:
            perms = json.loads(sys_model.permissions)
            allowed_roles = perms.get(action, [])
            if user.role not in allowed_roles:
                abort(403, message=f"Permission denied: You need '{action}' access for this resource.")
        except (json.JSONDecodeError, TypeError):
            pass

    def get_model(self, projectId, model_name, require_published=True):
        """Get a SysModel by name."""
        from backend.models.system import SysModel
        from flask_smorest import abort

        query = SysModel.query.filter_by(projectId=projectId, name=model_name)
        if require_published:
            query = query.filter_by(status="published")

        sys_model = query.first()
        if not sys_model:
            status_msg = " or not published" if require_published else ""
            abort(404, message=f"Model '{model_name}' not found{status_msg}.")

        return sys_model

    def validate_value(self, field, value):
        """Delegate to FieldValidator."""
        return FieldValidator.validate(field, value)

    def build_relational_query(self, sys_model, table, schema=None):
        """Delegate to QueryBuilder."""
        return QueryBuilder.build_relational_query(sys_model, table, schema)

    def process_results(self, raw_results, relation_fields, sys_model):
        """Delegate to ResultProcessor."""
        return ResultProcessor.process_results(raw_results, relation_fields, sys_model)

    def handle_file_uploads(self, data, sys_model):
        """Handle file uploads for file/image fields."""
        upload_folder = current_app.config.get("UPLOAD_FOLDER", "uploads")
        import os
        os.makedirs(upload_folder, exist_ok=True)

        allowed_extensions = {"txt", "pdf", "png", "jpg", "jpeg", "gif"}

        for field in sys_model.fields:
            if field.type in ["file", "image"]:
                if field.name in request.files:
                    file = request.files[field.name]
                    if file and file.filename:
                        ext = allowed_extensions if field.type == "file" else {"png", "jpg", "jpeg", "gif"}
                        if "." not in file.filename or file.filename.rsplit(".", 1)[1].lower() not in ext:
                            from flask_smorest import abort
                            abort(400, message=f"File type not allowed for field '{field.name}'.")

                        filename = secure_filename(file.filename)
                        file.save(os.path.join(upload_folder, filename))
                        data[field.name] = filename
        return data

    def handle_nested_writes(self, main_id, data, sys_model, schema=None):
        """Handle insert/update of detail records (lines)."""
        for field in sys_model.fields:
            if field.type == "lines" and field.name in data:
                lines_data = data[field.name]
                if not isinstance(lines_data, list):
                    continue

                try:
                    options = json.loads(field.options)
                    target_table_name = options.get("target_table")
                    foreign_key = options.get("foreign_key")

                    if target_table_name and foreign_key:
                        target_table = get_table_object(target_table_name, schema=schema)
                        for line in lines_data:
                            line[foreign_key] = main_id
                            if line.get("_destroy"):
                                if line.get("id"):
                                    self.db.session.execute(delete(target_table).where(target_table.c.id == line["id"]))
                            elif line.get("id"):
                                self.db.session.execute(update(target_table).where(target_table.c.id == line["id"]).values(line))
                            else:
                                if "id" in line: del line["id"]
                                self.db.session.execute(insert(target_table).values(line))
                except Exception as e:
                    current_app.logger.error(f"Error handling nested write for {field.name}: {e}")

    def evaluate_default_value(self, default_val, field_type):
        """Evaluate placeholders in default values."""
        from backend.models.user import User

        if not isinstance(default_val, str):
            return default_val

        val_upper = default_val.upper().strip()
        if val_upper == "{TODAY}":
            return datetime.date.today()
        elif val_upper == "{NOW}":
            return datetime.datetime.now()
        elif val_upper == "{CURRENT_USER}":
            userId = get_jwt_identity()
            if userId:
                if field_type in ["relation", "integer"]:
                    return int(userId)
                user = self.db.session.get(User, userId)
                return user.email if user else None
            return None

        return default_val

    def list_records(self, projectId, model_name, page=1, per_page=10):
        """
        Retrieves a paginated list of records for a dynamic model.

        Supports:
        - Global search (q parameter)
        - Column-specific filtering
        - Dynamic sorting
        - Relation expansion

        Returns:
            tuple: (processed_results, response_headers)
        """
        sys_model = self.get_model(projectId, model_name, require_published=True)
        self.check_permissions(sys_model, "read", projectId)

        schema_name = f"project_{projectId}"
        table = get_table_object(model_name, schema=schema_name)

        query, relation_fields = self.build_relational_query(sys_model, table, schema=schema_name)

        q = request.args.get("q")
        if q:
            filters = []
            for field in sys_model.fields:
                if field.type in ["string", "text"] and field.name in table.c:
                    filters.append(table.c[field.name].ilike(f"%{q}%"))

            for rel_info in relation_fields.values():
                target_table = rel_info["target_table"]
                for col in target_table.c:
                    if isinstance(col.type, (String, Text)):
                        filters.append(col.ilike(f"%{q}%"))

            if filters:
                query = query.where(or_(*filters))

        count_query = select(func.count()).select_from(query.alias())

        sort_by = request.args.get("sort_by")
        sort_order = request.args.get("sort_order", "asc")

        if sort_by:
            if sort_by in table.c:
                col = table.c[sort_by]
                query = query.order_by(desc(col) if sort_order == "desc" else asc(col))
            elif "." in sort_by:
                parts = sort_by.split(".")
                if len(parts) == 2:
                    rel_key, rel_col = parts
                    target_info = relation_fields.get(rel_key) or relation_fields.get(f"{rel_key}_id")
                    if target_info:
                        target_table = target_info["target_table"]
                        if rel_col in target_table.c:
                            col = target_table.c[rel_col]
                            query = query.order_by(desc(col) if sort_order == "desc" else asc(col))
        elif "id" in table.c:
            query = query.order_by(desc(table.c.id))

        query = query.limit(per_page).offset((page - 1) * per_page)

        # Optimization: Use a single execution for count and results if possible,
        # but for now we keep them separate for clarity and standard compatibility.
        total_count = self.db.session.execute(count_query).scalar_one_or_none() or 0

        # Optimization: Fetch all results in one go to avoid N+1 in process_results
        raw_results = self.db.session.execute(query).mappings().all()

        result = self.process_results(raw_results, relation_fields, sys_model)

        headers = {
            "X-Total-Count": str(total_count),
            "X-Pages": str((total_count + per_page - 1) // per_page),
            "X-Current-Page": str(page),
            "X-Per-Page": str(per_page),
        }

        start = (page - 1) * per_page
        if total_count == 0:
            headers["Content-Range"] = "items */0"
        else:
            if not isinstance(result, list) or len(result) == 0:
                headers["Content-Range"] = f"items */{total_count}"
            else:
                end = start + len(result) - 1
                headers["Content-Range"] = f"items {start}-{end}/{total_count}"

        return result, headers

    def create_record(self, projectId, model_name, data):
        """Create a new record."""
        sys_model = self.get_model(projectId, model_name, require_published=True)
        self.check_permissions(sys_model, "write", projectId)

        schema_name = f"project_{projectId}"
        table = get_table_object(model_name, schema=schema_name)

        if request.content_type and "multipart/form-data" in request.content_type:
            data = request.form.to_dict()
            data = self.handle_file_uploads(data, sys_model)

        validated_data = {}
        for field in sys_model.fields:
            if field.type in ["formula", "summary", "lookup", "calculated", "lines"]:
                continue

            value = data.get(field.name)
            if value is None and field.default_value:
                value = self.evaluate_default_value(field.default_value, field.type)

            if field.required and value is None:
                from flask_smorest import abort
                abort(400, message=f"Missing required field: '{field.name}'")

            if value is not None:
                validated_data[field.name] = self.validate_value(field, value)

        for field in sys_model.fields:
            if field.is_unique and field.name in validated_data:
                value = validated_data[field.name]
                if value is not None:
                    exists_query = select(func.count()).select_from(table).where(table.c[field.name] == value)
                    if self.db.session.execute(exists_query).scalar_one() > 0:
                        from flask_smorest import abort
                        abort(409, message=f"Value '{value}' for field '{field.name}' already exists.")

        stmt = insert(table).values(validated_data).returning(table)
        result = self.db.session.execute(stmt).mappings().one()

        self.handle_nested_writes(result.id, data, sys_model, schema=schema_name)
        log_audit(get_jwt_identity(), model_name, result.id, "CREATE", validated_data)

        self.db.session.commit()

        result_dict = {k: serialize_value(v) for k, v in dict(result).items()}

        try:
            from ..webhook_triggers import on_record_created
            on_record_created(model_name, result.id, result_dict, projectId)
        except Exception:
            pass

        return result_dict, 201

    def update_record(self, projectId, model_name, itemId, data):
        """Update an existing record."""
        sys_model = self.get_model(projectId, model_name, require_published=True)
        self.check_permissions(sys_model, "write", projectId)

        schema_name = f"project_{projectId}"
        table = get_table_object(model_name, schema=schema_name)

        if request.content_type and "multipart/form-data" in request.content_type:
            data = request.form.to_dict()
            data = self.handle_file_uploads(data, sys_model)

        validated_data = {}
        for field in sys_model.fields:
            if field.type in ["formula", "summary", "lookup", "calculated", "lines"]:
                continue
            if field.name in data:
                validated_data[field.name] = self.validate_value(field, data[field.name])

        for field in sys_model.fields:
            if field.is_unique and field.name in validated_data:
                value = validated_data[field.name]
                if value is not None:
                    exists_query = select(func.count()).select_from(table).where(table.c[field.name] == value, table.c.id != itemId)
                    if self.db.session.execute(exists_query).scalar_one() > 0:
                        from flask_smorest import abort
                        abort(409, message=f"Value '{value}' for field '{field.name}' already exists.")

        stmt = update(table).where(table.c.id == itemId).values(validated_data).returning(table)
        result = self.db.session.execute(stmt).mappings().one()

        self.handle_nested_writes(itemId, data, sys_model, schema=schema_name)
        log_audit(get_jwt_identity(), model_name, itemId, "UPDATE", validated_data)

        self.db.session.commit()
        result_dict = {k: serialize_value(v) for k, v in dict(result).items()}

        try:
            from ..webhook_triggers import on_record_updated
            on_record_updated(model_name, itemId, result_dict, projectId)
        except Exception:
            pass

        return result_dict

    def delete_record(self, projectId, model_name, itemId):
        """Delete a single record."""
        sys_model = self.get_model(projectId, model_name, require_published=True)
        self.check_permissions(sys_model, "write", projectId)

        schema_name = f"project_{projectId}"
        table = get_table_object(model_name, schema=schema_name)

        stmt = delete(table).where(table.c.id == itemId)
        self.db.session.execute(stmt)
        log_audit(get_jwt_identity(), model_name, itemId, "DELETE")
        self.db.session.commit()

        try:
            from ..webhook_triggers import on_record_deleted
            on_record_deleted(model_name, itemId, projectId)
        except Exception:
            pass

    def bulk_delete(self, projectId, model_name, ids_to_delete):
        """Delete multiple records."""
        sys_model = self.get_model(projectId, model_name, require_published=True)
        self.check_permissions(sys_model, "write", projectId)

        schema_name = f"project_{projectId}"
        table = get_table_object(model_name, schema=schema_name)

        userId = get_jwt_identity()
        for itemId in ids_to_delete:
            log_audit(userId, model_name, itemId, "DELETE")

        stmt = delete(table).where(table.c.id.in_(ids_to_delete))
        self.db.session.execute(stmt)
        self.db.session.commit()

    def get_record(self, projectId, model_name, itemId):
        """Get a single record with relations and lines."""
        sys_model = self.get_model(projectId, model_name, require_published=True)
        self.check_permissions(sys_model, "read", projectId)

        schema_name = f"project_{projectId}"
        table = get_table_object(model_name, schema=schema_name)

        query, relation_fields = self.build_relational_query(sys_model, table, schema=schema_name)
        query = query.where(table.c.id == itemId)
        raw_result = self.db.session.execute(query).mappings().first()

        if not raw_result:
            from flask_smorest import abort
            abort(404, message="Item not found.")

        result = self.process_results(raw_result, relation_fields, sys_model)

        for field in sys_model.fields:
            if field.type == "lines":
                try:
                    opts = json.loads(field.options)
                    target_table = get_table_object(opts["target_table"], schema=schema_name)
                    fk = opts["foreign_key"]
                    lines_query = select(target_table).where(target_table.c[fk] == itemId)
                    lines_res = self.db.session.execute(lines_query).mappings().all()
                    result[field.name] = [{k: serialize_value(v) for k, v in dict(r).items()} for r in lines_res]
                except Exception:
                    pass

        return result

    def get_model_metadata(self, projectId, model_name):
        """Get model metadata for frontend, applying translations."""
        sys_model = self.get_model(projectId, model_name, require_published=True)
        self.check_permissions(sys_model, "read", projectId)
        return sys_model

    def clone_record(self, projectId, model_name, itemId):
        """Clone an existing record."""
        sys_model = self.get_model(projectId, model_name, require_published=True)
        self.check_permissions(sys_model, "write", projectId)

        schema_name = f"project_{projectId}"
        table = get_table_object(model_name, schema=schema_name)

        query = select(table).where(table.c.id == itemId)
        source_record = self.db.session.execute(query).mappings().first()

        if not source_record:
            from flask_smorest import abort
            abort(404, message="Item not found.")

        new_data = {f.name: source_record[f.name] for f in sys_model.fields if f.name in source_record}

        stmt = insert(table).values(new_data).returning(table)
        result = self.db.session.execute(stmt).mappings().one()

        log_audit(get_jwt_identity(), model_name, result.id, "CLONE", {"source_id": itemId})
        self.db.session.commit()

        result_dict = {k: serialize_value(v) for k, v in dict(result).items()}
        return result_dict, 201

    def import_csv(self, projectId, model_name, file):
        """Import data from CSV file."""
        sys_model = self.get_model(projectId, model_name, require_published=True)
        self.check_permissions(sys_model, "write", projectId)

        schema_name = f"project_{projectId}"
        table = get_table_object(model_name, schema=schema_name)

        try:
            stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
            csv_input = csv.DictReader(stream)
        except Exception as e:
            from flask_smorest import abort
            abort(400, message=f"Error reading CSV: {str(e)}")

        valid_fields = {f.name: f for f in sys_model.fields if f.type not in ["formula", "summary", "lookup", "calculated", "lines"]}
        inserted_count = 0
        errors = []

        for i, row in enumerate(csv_input):
            row_data = {}
            try:
                for col, val in row.items():
                    if col in valid_fields:
                        field = valid_fields[col]
                        if val == "": val = None
                        if val is not None:
                            try:
                                row_data[col] = self.validate_value(field, val)
                            except Exception as e:
                                raise ValueError(str(e))

                for field in valid_fields.values():
                    if field.name not in row_data:
                        if field.default_value:
                            row_data[field.name] = self.evaluate_default_value(field.default_value, field.type)
                        elif field.required:
                            raise ValueError(f"Missing required field: {field.name}")

                for field in valid_fields.values():
                    if field.is_unique and field.name in row_data:
                        val = row_data[field.name]
                        if val is not None:
                            exists_query = select(func.count()).select_from(table).where(table.c[field.name] == val)
                            if self.db.session.execute(exists_query).scalar_one() > 0:
                                raise ValueError(f"Value '{val}' for field '{field.name}' already exists.")

                self.db.session.execute(insert(table).values(row_data))
                inserted_count += 1
            except Exception as e:
                errors.append(f"Row {i + 2}: {str(e)}")

        if inserted_count > 0:
            log_audit(get_jwt_identity(), model_name, 0, "IMPORT", {"count": inserted_count})
            self.db.session.commit()

        return {"message": f"Imported {inserted_count} records.", "errors": errors}, 200

    def export_data(self, projectId, model_name, format='csv'):
        """Export data from a dynamic table."""
        sys_model = self.get_model(projectId, model_name, require_published=True)
        self.check_permissions(sys_model, "read", projectId)

        schema_name = f"project_{projectId}"
        table = get_table_object(model_name, schema=schema_name)

        query, relation_fields = self.build_relational_query(sys_model, table, schema=schema_name)
        raw_results = self.db.session.execute(query).mappings().all()
        result = self.process_results(raw_results, relation_fields, sys_model)

        if format == 'json':
            return result

        # CSV Export
        output = io.StringIO()
        if not result:
            return ""

        writer = csv.DictWriter(output, fieldnames=result[0].keys())
        writer.writeheader()
        for row in result:
            # Flatten nested objects for CSV
            flat_row = {}
            for k, v in row.items():
                if isinstance(v, dict):
                    flat_row[k] = json.dumps(v)
                elif isinstance(v, list):
                    flat_row[k] = json.dumps(v)
                else:
                    flat_row[k] = v
            writer.writerow(flat_row)

        return output.getvalue()
