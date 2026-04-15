"""
Dynamic API Service - Handles dynamic CRUD operations for builder models.
"""

import re
import json
import csv
import io
import datetime
from sqlalchemy import (
    Table,
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
    text,
)
from werkzeug.utils import secure_filename
from werkzeug.exceptions import HTTPException
from flask import request, current_app
from flask_jwt_extended import get_jwt_identity

from backend.core.services.base import BaseService


class DynamicApiService(BaseService):
    """
    Service for dynamic CRUD operations on builder-created models.
    Handles relations, formulas, validations, and imports.
    """

    def check_permissions(self, sys_model, action, projectId=None):
        """
        Check role-based permissions for a model.

        Args:
            sys_model: SysModel instance.
            action: Action to check (read, write, etc.).
            projectId: Optional project ID to verify.
        """
        from ..models import User
        from flask_smorest import abort

        if projectId is not None and sys_model.projectId != projectId:
            abort(
                404,
                message=f"Model '{sys_model.name}' not found in project {projectId}.",
            )

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
                abort(
                    403,
                    message=f"Permission denied: You need '{action}' access for this resource.",
                )
        except (json.JSONDecodeError, TypeError):
            pass

    def get_model(self, projectId, model_name, require_published=True):
        """
        Get a SysModel by name, optionally checking for published status.

        Args:
            projectId: Project ID
            model_name: Name of the model
            require_published: If True, only return published models

        Returns:
            SysModel instance or None
        """
        from ..models import SysModel
        from flask_smorest import abort

        query = SysModel.query.filter_by(projectId=projectId, name=model_name)

        if require_published:
            query = query.filter_by(status="published")

        sys_model = query.first()

        if not sys_model and require_published:
            abort(404, message=f"Model '{model_name}' not found or not published.")
        elif not sys_model:
            abort(404, message=f"Model '{model_name}' not found.")

        return sys_model

    def validate_value(self, field, value):
        """
        Validate and convert value based on field type.

        Args:
            field: SysField instance.
            value: Value to validate.

        Returns:
            Validated and converted value.
        """
        from flask_smorest import abort

        if value is None:
            if field.required:
                abort(
                    400, message=f"Field '{field.name}' is required and cannot be null."
                )
            return None

        try:
            if field.validation_regex and field.type in ["string", "text"]:
                if not re.fullmatch(field.validation_regex, str(value)):
                    abort(
                        400,
                        message=field.validation_message
                        or f"Value for '{field.name}' does not match the required format.",
                    )

            if field.type == "select":
                if field.options:
                    try:
                        opts = json.loads(field.options)
                        valid_values = []
                        if isinstance(opts, list):
                            for o in opts:
                                if isinstance(o, dict):
                                    valid_values.append(o.get("value"))
                                else:
                                    valid_values.append(o)

                        if valid_values and value not in valid_values:
                            abort(
                                400,
                                message=f"Invalid value '{value}' for field '{field.name}'. Allowed: {valid_values}",
                            )
                    except (json.JSONDecodeError, AttributeError):
                        pass
                return str(value)

            if field.type in ["integer", "relation"]:
                return int(value)
            elif field.type in ["float", "currency"]:
                return float(value)
            elif field.type == "boolean":
                if isinstance(value, bool):
                    return value
                v_str = str(value).lower()
                if v_str in ["true", "1", "t", "y", "yes"]:
                    return True
                if v_str in ["false", "0", "f", "n", "no"]:
                    return False
                raise ValueError
            elif field.type == "tags":
                if isinstance(value, str):
                    try:
                        value = json.loads(value)
                    except:
                        value = [x.strip() for x in value.split(",") if x.strip()]
                if not isinstance(value, list):
                    abort(
                        400,
                        message=f"Invalid format for tags field '{field.name}'. Expected list.",
                    )
                return json.dumps(value)
            return value
        except (ValueError, TypeError):
            abort(
                400,
                message=f"Invalid type for field '{field.name}'. Expected {field.type}.",
            )

    def _evaluate_formulas(self, record, sys_model):
        """Evaluate formula fields for a record."""
        formula_fields = [
            f for f in sys_model.fields if f.type == "formula" and f.formula
        ]
        if not formula_fields:
            return record

        all_placeholders = set()
        for field in formula_fields:
            placeholders = re.findall(r"\{(\w+)\}", field.formula)
            all_placeholders.update(placeholders)

        context = {p: record.get(p) for p in all_placeholders}

        for key, val in context.items():
            try:
                context[key] = float(val if val is not None else 0)
            except (ValueError, TypeError):
                pass

        for field in formula_fields:
            try:
                expression = re.sub(r"\{(\w+)\}", r"\1", field.formula)
                result = eval(expression, {"__builtins__": {}}, context)
                record[field.name] = result
            except Exception:
                record[field.name] = None
        return record

    def build_relational_query(self, sys_model, table, schema=None):
        """Build query with joins for relations."""
        from ..utils import get_table_object

        columns_to_select = [table]
        relation_fields = {}
        joins_to_make = {}

        for field in sys_model.fields:
            if field.type == "relation" and field.options:
                try:
                    options = json.loads(field.options)
                    target_table_name = options.get("target_table")
                    if target_table_name:
                        target_table = get_table_object(
                            target_table_name, schema=schema
                        )
                        label_prefix = f"{field.name}__"
                        relation_fields[field.name] = {
                            "target_table": target_table,
                            "label_prefix": label_prefix,
                        }
                        for col in target_table.c:
                            columns_to_select.append(
                                col.label(f"{label_prefix}{col.name}")
                            )

                        join_key = f"{table.name}_{target_table_name}"
                        if join_key not in joins_to_make:
                            joins_to_make[join_key] = (
                                target_table,
                                table.c[field.name] == target_table.c.id,
                            )
                except (json.JSONDecodeError, KeyError):
                    pass

            if field.type == "lookup" and field.options:
                try:
                    options = json.loads(field.options)
                    target_table_name = options.get("target_table")
                    local_key = options.get("local_key")
                    remote_key = options.get("remote_key", "id")
                    remote_field = options.get("remote_field")

                    if target_table_name and local_key and remote_field:
                        target_table = get_table_object(
                            target_table_name, schema=schema
                        )
                        columns_to_select.append(
                            target_table.c[remote_field].label(field.name)
                        )
                        join_key = f"{table.name}_{target_table_name}"
                        if join_key not in joins_to_make:
                            joins_to_make[join_key] = (
                                target_table,
                                table.c[local_key] == target_table.c[remote_key],
                            )
                except (json.JSONDecodeError, KeyError):
                    pass

            if field.type == "summary" and field.options and field.summary_expression:
                try:
                    options = json.loads(field.options)
                    target_table_name = options.get("target_table")
                    foreign_key = options.get("foreign_key")

                    if target_table_name:
                        target_table = get_table_object(
                            target_table_name, schema=schema
                        )

                        match = re.match(r"(\w+)\((\w+)\)", field.summary_expression)
                        if match:
                            func_name, col_name = match.groups()
                            if col_name in target_table.c:
                                sql_func = getattr(func, func_name)
                                if foreign_key:
                                    subquery = (
                                        select(sql_func(target_table.c[col_name]))
                                        .where(
                                            target_table.c[foreign_key] == table.c.id
                                        )
                                        .scalar_subquery()
                                    )
                                else:
                                    subquery = select(
                                        sql_func(target_table.c[col_name])
                                    ).scalar_subquery()

                                columns_to_select.append(subquery.label(field.name))
                except (json.JSONDecodeError, KeyError, AttributeError):
                    pass

        query = select(*columns_to_select)
        for join_target, join_condition in joins_to_make.values():
            query = query.join(join_target, join_condition, isouter=True)

        return query, relation_fields

    def process_results(self, raw_results, relation_fields, sys_model):
        """Process flat results into nested objects with formulas."""
        from ..utils import serialize_value

        if not raw_results:
            return []

        is_single = not isinstance(raw_results, list)
        results_list = [raw_results] if is_single else raw_results

        processed_list = []
        field_types = {f.name: f.type for f in sys_model.fields}

        for raw_row in results_list:
            processed_row = {}
            nested_objects = {}

            for key, value in raw_row.items():
                safe_value = serialize_value(value)
                is_relational = False
                for rel_field_name, rel_info in relation_fields.items():
                    prefix = rel_info["label_prefix"]
                    if key.startswith(prefix):
                        original_field_name = key[len(prefix) :]
                        if rel_field_name not in nested_objects:
                            nested_objects[rel_field_name] = {}
                        nested_objects[rel_field_name][original_field_name] = safe_value
                        is_relational = True
                        break
                if not is_relational:
                    val = safe_value
                    if field_types.get(key) == "tags" and isinstance(val, str):
                        try:
                            val = json.loads(val)
                        except:
                            pass
                    processed_row[key] = val

            for rel_field_name, nested_data in nested_objects.items():
                object_name = (
                    rel_field_name[:-3]
                    if rel_field_name.endswith("_id")
                    else rel_field_name
                )
                processed_row[object_name] = (
                    nested_data
                    if not all(v is None for v in nested_data.values())
                    else None
                )

            processed_row = self._evaluate_formulas(processed_row, sys_model)
            processed_list.append(processed_row)

        return processed_list[0] if is_single else processed_list

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
                        ext = (
                            allowed_extensions
                            if field.type == "file"
                            else {"png", "jpg", "jpeg", "gif"}
                        )

                        if (
                            "." not in file.filename
                            or file.filename.rsplit(".", 1)[1].lower() not in ext
                        ):
                            from flask_smorest import abort

                            abort(
                                400,
                                message=f"File type not allowed for field '{field.name}'.",
                            )

                        filename = secure_filename(file.filename)
                        file.save(os.path.join(upload_folder, filename))
                        data[field.name] = filename
        return data

    def handle_nested_writes(self, main_id, data, sys_model, schema=None):
        """Handle insert/update of detail records (lines)."""
        from ..utils import get_table_object

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
                        target_table = get_table_object(
                            target_table_name, schema=schema
                        )

                        for line in lines_data:
                            line[foreign_key] = main_id

                            if line.get("_destroy"):
                                if line.get("id"):
                                    self.db.session.execute(
                                        delete(target_table).where(
                                            target_table.c.id == line["id"]
                                        )
                                    )
                            elif line.get("id"):
                                self.db.session.execute(
                                    update(target_table)
                                    .where(target_table.c.id == line["id"])
                                    .values(line)
                                )
                            else:
                                if "id" in line:
                                    del line["id"]
                                self.db.session.execute(
                                    insert(target_table).values(line)
                                )
                except Exception as e:
                    print(f"Error handling nested write for {field.name}: {e}")

    def evaluate_default_value(self, default_val, field_type):
        """Evaluate placeholders in default values."""
        from flask_jwt_extended import get_jwt_identity
        from ..models import User

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
        """List records with filtering, sorting, pagination."""
        from ..utils import get_table_object, serialize_value

        sys_model = self.get_model(projectId, model_name, require_published=True)

        self.check_permissions(sys_model, "read", projectId)

        schema_name = f"project_{projectId}"
        table = get_table_object(model_name, schema=schema_name)

        query, relation_fields = self.build_relational_query(
            sys_model, table, schema=schema_name
        )

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
                    target_info = relation_fields.get(rel_key) or relation_fields.get(
                        f"{rel_key}_id"
                    )

                    if target_info:
                        target_table = target_info["target_table"]
                        if rel_col in target_table.c:
                            col = target_table.c[rel_col]
                            query = query.order_by(
                                desc(col) if sort_order == "desc" else asc(col)
                            )
        elif "id" in table.c:
            query = query.order_by(desc(table.c.id))

        query = query.limit(per_page).offset((page - 1) * per_page)

        total_count = self.db.session.execute(count_query).scalar_one_or_none() or 0
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
            if len(result) == 0:
                headers["Content-Range"] = f"items */{total_count}"
            else:
                end = start + len(result) - 1
                headers["Content-Range"] = f"items {start}-{end}/{total_count}"

        return result, headers

    def create_record(self, projectId, model_name, data):
        """Create a new record."""
        from ..utils import get_table_object, serialize_value, log_audit
        from flask_jwt_extended import get_jwt_identity

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
                    exists_query = (
                        select(func.count())
                        .select_from(table)
                        .where(table.c[field.name] == value)
                    )
                    if self.db.session.execute(exists_query).scalar_one() > 0:
                        from flask_smorest import abort

                        abort(
                            409,
                            message=f"Value '{value}' for field '{field.name}' already exists.",
                        )

        stmt = insert(table).values(validated_data).returning(table)
        result = self.db.session.execute(stmt).mappings().one()

        self.handle_nested_writes(result.id, data, sys_model, schema=schema_name)
        log_audit(get_jwt_identity(), model_name, result.id, "CREATE", validated_data)

        self.db.session.commit()

        result_dict = dict(result)
        for k, v in result_dict.items():
            result_dict[k] = serialize_value(v)

        try:
            from ..webhook_triggers import on_record_created

            on_record_created(model_name, result.id, result_dict, projectId)
        except Exception:
            pass

        return result_dict, 201

    def update_record(self, projectId, model_name, itemId, data):
        """Update an existing record."""
        from ..utils import get_table_object, serialize_value, log_audit
        from flask_jwt_extended import get_jwt_identity

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
                validated_data[field.name] = self.validate_value(
                    field, data[field.name]
                )

        for field in sys_model.fields:
            if field.is_unique and field.name in validated_data:
                value = validated_data[field.name]
                if value is not None:
                    exists_query = (
                        select(func.count())
                        .select_from(table)
                        .where(table.c[field.name] == value, table.c.id != itemId)
                    )
                    if self.db.session.execute(exists_query).scalar_one() > 0:
                        from flask_smorest import abort

                        abort(
                            409,
                            message=f"Value '{value}' for field '{field.name}' already exists.",
                        )

        stmt = (
            update(table)
            .where(table.c.id == itemId)
            .values(validated_data)
            .returning(table)
        )
        result = self.db.session.execute(stmt).mappings().one()

        self.handle_nested_writes(itemId, data, sys_model, schema=schema_name)
        log_audit(get_jwt_identity(), model_name, itemId, "UPDATE", validated_data)

        self.db.session.commit()

        result_dict = dict(result)
        for k, v in result_dict.items():
            result_dict[k] = serialize_value(v)

        try:
            from ..webhook_triggers import on_record_updated

            on_record_updated(model_name, itemId, result_dict, projectId)
        except Exception:
            pass

        return result_dict

    def delete_record(self, projectId, model_name, itemId):
        """Delete a single record."""
        from ..utils import get_table_object, log_audit
        from flask_jwt_extended import get_jwt_identity

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
        from ..utils import get_table_object, log_audit
        from flask_jwt_extended import get_jwt_identity

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
        from ..utils import get_table_object, serialize_value

        sys_model = self.get_model(projectId, model_name, require_published=True)

        self.check_permissions(sys_model, "read", projectId)

        schema_name = f"project_{projectId}"
        table = get_table_object(model_name, schema=schema_name)

        query, relation_fields = self.build_relational_query(
            sys_model, table, schema=schema_name
        )
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
                    target_table = get_table_object(
                        opts["target_table"], schema=schema_name
                    )
                    fk = opts["foreign_key"]
                    lines_query = select(target_table).where(
                        target_table.c[fk] == itemId
                    )
                    lines_res = self.db.session.execute(lines_query).mappings().all()
                    result[field.name] = [dict(r) for r in lines_res]
                    for l in result[field.name]:
                        for k, v in l.items():
                            l[k] = serialize_value(v)
                except:
                    pass

        return result

    def get_model_metadata(self, projectId, model_name):
        """Get model metadata for frontend."""
        sys_model = self.get_model(projectId, model_name, require_published=True)

        self.check_permissions(sys_model, "read", projectId)

        _ = sys_model.fields

        return sys_model

    def clone_record(self, projectId, model_name, itemId):
        """Clone an existing record."""
        from ..utils import get_table_object, serialize_value, log_audit
        from flask_jwt_extended import get_jwt_identity

        sys_model = self.get_model(projectId, model_name, require_published=True)

        if not sys_model:
            from flask_smorest import abort

            abort(404, message=f"Model '{model_name}' not found.")

        self.check_permissions(sys_model, "write", projectId)

        schema_name = f"project_{projectId}"
        table = get_table_object(model_name, schema=schema_name)

        query = select(table).where(table.c.id == itemId)
        source_record = self.db.session.execute(query).mappings().first()

        if not source_record:
            from flask_smorest import abort

            abort(404, message="Item not found.")

        new_data = {}
        for field in sys_model.fields:
            if field.name in source_record:
                new_data[field.name] = source_record[field.name]

        stmt = insert(table).values(new_data).returning(table)
        result = self.db.session.execute(stmt).mappings().one()

        log_audit(
            get_jwt_identity(), model_name, result.id, "CLONE", {"source_id": itemId}
        )
        self.db.session.commit()

        result_dict = dict(result)
        for k, v in result_dict.items():
            result_dict[k] = serialize_value(v)

        return result_dict, 201

    def import_csv(self, projectId, model_name, file):
        """Import data from CSV file."""
        from ..utils import get_table_object, log_audit
        from flask_jwt_extended import get_jwt_identity

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

        valid_fields = {f.name: f for f in sys_model.fields}

        inserted_count = 0
        errors = []

        for i, row in enumerate(csv_input):
            row_data = {}
            try:
                for col, val in row.items():
                    if col in valid_fields:
                        field = valid_fields[col]
                        if field.type in [
                            "formula",
                            "summary",
                            "lookup",
                            "calculated",
                            "lines",
                        ]:
                            continue

                        if val == "":
                            val = None

                        if val is not None:
                            try:
                                row_data[col] = self.validate_value(field, val)
                            except HTTPException as e:
                                msg = (
                                    e.description
                                    if hasattr(e, "description")
                                    else str(e)
                                )
                                raise ValueError(msg)

                for field in sys_model.fields:
                    if field.type in [
                        "formula",
                        "summary",
                        "lookup",
                        "calculated",
                        "lines",
                    ]:
                        continue

                    if field.name not in row_data:
                        if field.default_value:
                            row_data[field.name] = self.evaluate_default_value(
                                field.default_value, field.type
                            )
                        elif field.required:
                            raise ValueError(f"Missing required field: {field.name}")

                for field in sys_model.fields:
                    if field.is_unique and field.name in row_data:
                        val = row_data[field.name]
                        if val is not None:
                            exists_query = (
                                select(func.count())
                                .select_from(table)
                                .where(table.c[field.name] == val)
                            )
                            if self.db.session.execute(exists_query).scalar_one() > 0:
                                raise ValueError(
                                    f"Value '{val}' for field '{field.name}' already exists."
                                )

                stmt = insert(table).values(row_data)
                self.db.session.execute(stmt)
                inserted_count += 1
            except Exception as e:
                errors.append(f"Row {i + 2}: {str(e)}")

        if inserted_count > 0:
            log_audit(
                get_jwt_identity(), model_name, 0, "IMPORT", {"count": inserted_count}
            )
            self.db.session.commit()

        return {"message": f"Imported {inserted_count} records.", "errors": errors}, 200
