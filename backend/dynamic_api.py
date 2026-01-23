from flask.views import MethodView
from flask import request, current_app
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
import sys
from sqlalchemy import Table, select, insert, update, delete, func, or_, desc, asc, String, Text, text
import os
import json, re, datetime, decimal
import csv
import io
from werkzeug.exceptions import HTTPException
from werkzeug.utils import secure_filename

from .models import SysModel, User, SysField, AuditLog
from .extensions import db
from .schemas import SysModelSchema, AuditLogSchema
from .utils import serialize_value, log_audit, generate_schema_diff_sql, get_table_object

blp = Blueprint("dynamic_api", __name__, description="Dynamic CRUD API for builder models")

def check_model_permissions(sys_model, action):
    """Verifica i permessi basati sui ruoli per il modello."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        abort(401, message="User not found.")

    # Admin ha sempre accesso completo
    if user.role == 'admin':
        return

    if not sys_model.permissions:
        return # Se non ci sono permessi definiti, accesso consentito (o definire policy di default)

    try:
        perms = json.loads(sys_model.permissions)
        allowed_roles = perms.get(action, [])
        if user.role not in allowed_roles:
            abort(403, message=f"Permission denied: You need '{action}' access for this resource.")
    except (json.JSONDecodeError, TypeError):
        pass # Ignora errori di parsing JSON

def validate_value(field, value):
    """Valida e converte il valore in base al tipo del campo."""
    if value is None:
        if field.required:
            abort(400, message=f"Field '{field.name}' is required and cannot be null.")
        return None
        
    try:
        # Custom Regex Validation (for string-like types)
        if field.validation_regex and field.type in ['string', 'text']:
            if not re.fullmatch(field.validation_regex, str(value)):
                abort(400, message=field.validation_message or f"Value for '{field.name}' does not match the required format.")

        if field.type == 'select':
            if field.options:
                try:
                    opts = json.loads(field.options)
                    valid_values = []
                    if isinstance(opts, list):
                        for o in opts:
                            if isinstance(o, dict):
                                valid_values.append(o.get('value'))
                            else:
                                valid_values.append(o)
                    
                    if valid_values and value not in valid_values:
                        abort(400, message=f"Invalid value '{value}' for field '{field.name}'. Allowed: {valid_values}")
                except (json.JSONDecodeError, AttributeError):
                    pass # Ignore malformed options or allow if parsing fails
            return str(value)

        if field.type in ['integer', 'relation']:
            return int(value)
        elif field.type in ['float', 'currency']:
            return float(value)
        elif field.type == 'boolean':
            if isinstance(value, bool):
                return value
            v_str = str(value).lower()
            if v_str in ['true', '1', 't', 'y', 'yes']:
                return True
            if v_str in ['false', '0', 'f', 'n', 'no']:
                return False
            raise ValueError
        elif field.type == 'tags':
            if isinstance(value, str):
                try:
                    value = json.loads(value)
                except:
                    value = [x.strip() for x in value.split(',') if x.strip()]
            if not isinstance(value, list):
                abort(400, message=f"Invalid format for tags field '{field.name}'. Expected list.")
            return json.dumps(value)
        return value
    except (ValueError, TypeError):
        abort(400, message=f"Invalid type for field '{field.name}'. Expected {field.type}.")

def _evaluate_formulas(record, sys_model):
    """Evaluates formula fields for a given record."""
    formula_fields = [f for f in sys_model.fields if f.type == 'formula' and f.formula]
    if not formula_fields:
        return record

    # Find all placeholders in all formulas to build a context
    all_placeholders = set()
    for field in formula_fields:
        placeholders = re.findall(r'\{(\w+)\}', field.formula)
        all_placeholders.update(placeholders)

    # Create a context dictionary with values from the record
    context = {p: record.get(p) for p in all_placeholders}

    # Ensure all values for calculation are numeric, treating None as 0
    for key, val in context.items():
        try:
            context[key] = float(val if val is not None else 0)
        except (ValueError, TypeError):
            # If a value can't be converted, we can't calculate.
            # The formula evaluation will fail gracefully below.
            pass

    for field in formula_fields:
        try:
            # Sanitize formula string by replacing {var} with var
            expression = re.sub(r'\{(\w+)\}', r'\1', field.formula)
            # Safely evaluate the expression with a restricted context
            result = eval(expression, {"__builtins__": {}}, context)
            record[field.name] = result
        except Exception:
            record[field.name] = None # Set to None if evaluation fails
    return record

def _build_relational_query(sys_model, table, schema=None):
    """Builds a SQLAlchemy query with joins and labeled columns for relations."""
    columns_to_select = [table]
    relation_fields = {}
    joins_to_make = {} # To avoid duplicate joins

    for field in sys_model.fields:
        if field.type == 'relation' and field.options:
            try:
                options = json.loads(field.options)
                target_table_name = options.get('target_table')
                if target_table_name:
                    target_table = get_table_object(target_table_name, schema=schema)
                    # Prefix for labels to avoid column name collisions, e.g., "customer_id__name"
                    label_prefix = f"{field.name}__"
                    relation_fields[field.name] = {
                        'target_table': target_table,
                        'label_prefix': label_prefix
                    }
                    for col in target_table.c:
                        columns_to_select.append(col.label(f"{label_prefix}{col.name}"))
                    
                    join_key = f"{table.name}_{target_table_name}"
                    if join_key not in joins_to_make:
                        joins_to_make[join_key] = (target_table, table.c[field.name] == target_table.c.id)

            except (json.JSONDecodeError, KeyError):
                pass  # Ignore malformed options

        # Handle lookup fields
        if field.type == 'lookup' and field.options:
            try:
                options = json.loads(field.options)
                target_table_name = options.get('target_table')
                local_key = options.get('local_key') # e.g., customer_id
                remote_key = options.get('remote_key', 'id') # e.g., id
                remote_field = options.get('remote_field') # e.g., name

                if target_table_name and local_key and remote_field:
                    target_table = get_table_object(target_table_name, schema=schema)
                    columns_to_select.append(target_table.c[remote_field].label(field.name))
                    join_key = f"{table.name}_{target_table_name}"
                    if join_key not in joins_to_make:
                        joins_to_make[join_key] = (target_table, table.c[local_key] == target_table.c[remote_key])
            except (json.JSONDecodeError, KeyError):
                pass  # Ignore malformed options
        
        # Handle summary fields
        if field.type == 'summary' and field.options and field.summary_expression:
            try:
                options = json.loads(field.options)
                target_table_name = options.get('target_table')
                foreign_key = options.get('foreign_key')
                
                if target_table_name:
                    target_table = get_table_object(target_table_name, schema=schema)
                    
                    # Parse expression like "SUM(amount)"
                    match = re.match(r"(\w+)\((\w+)\)", field.summary_expression)
                    if match:
                        func_name, col_name = match.groups()
                        if col_name in target_table.c:
                            sql_func = getattr(func, func_name)
                            if foreign_key:
                                subquery = select(sql_func(target_table.c[col_name])).where(
                                    target_table.c[foreign_key] == table.c.id
                                ).scalar_subquery()
                            else:
                                # Global aggregation (no foreign key)
                                subquery = select(sql_func(target_table.c[col_name])).scalar_subquery()
                                
                            columns_to_select.append(subquery.label(field.name))
            except (json.JSONDecodeError, KeyError, AttributeError):
                pass

    query = select(*columns_to_select)
    # Apply all unique joins as LEFT OUTER JOINs
    for join_target, join_condition in joins_to_make.values():
        query = query.join(join_target, join_condition, isouter=True)
    
    return query, relation_fields

def _process_relational_results(raw_results, relation_fields, sys_model):
    """Restructures flat query results into nested objects and evaluates formulas."""
    if not raw_results: # Se non ci sono risultati, restituisci una lista vuota
        return []

    is_single = not isinstance(raw_results, list)
    results_list = [raw_results] if is_single else raw_results
    
    processed_list = []
    field_types = {f.name: f.type for f in sys_model.fields}

    for raw_row in results_list:
        processed_row = {}
        nested_objects = {}

        # First pass: separate main fields from relational fields
        for key, value in raw_row.items():
            safe_value = serialize_value(value)
            is_relational = False
            for rel_field_name, rel_info in relation_fields.items():
                prefix = rel_info['label_prefix']
                if key.startswith(prefix):
                    original_field_name = key[len(prefix):]
                    if rel_field_name not in nested_objects:
                        nested_objects[rel_field_name] = {}
                    nested_objects[rel_field_name][original_field_name] = safe_value
                    is_relational = True
                    break
            if not is_relational:
                val = safe_value
                # Auto-deserialize tags
                if field_types.get(key) == 'tags' and isinstance(val, str):
                    try:
                        val = json.loads(val)
                    except: pass
                processed_row[key] = val

        # Second pass: attach the nested objects under a clean name (e.g., 'customer')
        for rel_field_name, nested_data in nested_objects.items():
            object_name = rel_field_name[:-3] if rel_field_name.endswith('_id') else rel_field_name
            # If all values in the nested object are None, the join found no match.
            processed_row[object_name] = nested_data if not all(v is None for v in nested_data.values()) else None
        
        # Third pass: evaluate formulas
        processed_row = _evaluate_formulas(processed_row, sys_model)

        processed_list.append(processed_row)

    return processed_list[0] if is_single else processed_list

def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def _handle_file_uploads(data, sys_model):
    """Handles file uploads for file/image fields."""
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)

    for field in sys_model.fields:
        if field.type in ['file', 'image']:
            # Check if a file was uploaded for this field
            if field.name in request.files:
                file = request.files[field.name]
                if file and file.filename:
                    allowed_extensions = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
                    if field.type == 'image':
                        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
                    
                    if not allowed_file(file.filename, allowed_extensions):
                        abort(400, message=f"File type not allowed for field '{field.name}'. Allowed: {allowed_extensions}")

                    filename = secure_filename(file.filename)
                    # Save the file
                    file.save(os.path.join(upload_folder, filename))
                    # Update data with the filename
                    data[field.name] = filename
    return data

def _handle_nested_writes(main_id, data, sys_model, schema=None):
    """Gestisce inserimento/aggiornamento dei record detail (lines)."""
    for field in sys_model.fields:
        if field.type == 'lines' and field.name in data:
            lines_data = data[field.name]
            if not isinstance(lines_data, list):
                continue
            
            try:
                options = json.loads(field.options)
                target_table_name = options.get('target_table')
                foreign_key = options.get('foreign_key')
                
                if target_table_name and foreign_key:
                    target_table = get_table_object(target_table_name, schema=schema)
                    
                    for line in lines_data:
                        # Imposta la chiave esterna
                        line[foreign_key] = main_id
                        
                        if line.get('_destroy'): # Cancellazione
                            if line.get('id'):
                                db.session.execute(delete(target_table).where(target_table.c.id == line['id']))
                        elif line.get('id'): # Aggiornamento
                            db.session.execute(update(target_table).where(target_table.c.id == line['id']).values(line))
                        else: # Inserimento
                            # Rimuovi ID temporanei o null se presenti
                            if 'id' in line: del line['id']
                            db.session.execute(insert(target_table).values(line))
            except Exception as e:
                print(f"Error handling nested write for {field.name}: {e}")
                # Non blocchiamo tutto, ma logghiamo l'errore

def _evaluate_default_value(default_val, field_type):
    """Valuta i placeholder nei valori di default (es. {TODAY}, {CURRENT_USER})."""
    if not isinstance(default_val, str):
        return default_val
    
    val_upper = default_val.upper().strip()
    
    if val_upper == '{TODAY}':
        return datetime.date.today()
    elif val_upper == '{NOW}':
        return datetime.datetime.now()
    elif val_upper == '{CURRENT_USER}':
        user_id = get_jwt_identity()
        if user_id:
            # Se il campo è una relazione o intero, restituisci l'ID
            if field_type in ['relation', 'integer']:
                return int(user_id)
            # Altrimenti restituisci l'email (utile per campi stringa 'created_by')
            user = User.query.get(user_id)
            return user.email if user else None
        return None
    
    return default_val

@blp.route("/data/<string:model_name>")
class DynamicDataList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, model_name):
        """Elenca i record da una tabella creata dinamicamente."""
        # Controlla che il modello esista nei metadati
        sys_model = SysModel.query.filter_by(name=model_name).first_or_404()
        check_model_permissions(sys_model, 'read')
        schema_name = f"project_{sys_model.project_id}"
        table = get_table_object(model_name, schema=schema_name)

        # --- Paginazione ---
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # --- Costruzione Query ---
        query, relation_fields = _build_relational_query(sys_model, table, schema=schema_name)
        
        # Eager load lines? Per ora no, le carichiamo solo nel dettaglio singolo se necessario
        # o implementiamo una logica simile a _build_relational_query per le One-to-Many

        # --- Filtri (q) ---
        q = request.args.get('q')
        if q:
            filters = []
            for field in sys_model.fields:
                # Applica ricerca solo su campi testuali
                if field.type in ['string', 'text'] and field.name in table.c:
                    filters.append(table.c[field.name].ilike(f"%{q}%"))
            
            # Ricerca su campi delle tabelle relazionate
            for rel_info in relation_fields.values():
                target_table = rel_info['target_table']
                for col in target_table.c:
                    if isinstance(col.type, (String, Text)):
                        filters.append(col.ilike(f"%{q}%"))
            
            if filters:
                query = query.where(or_(*filters))

        count_query = select(func.count()).select_from(query.alias())

        # --- Ordinamento ---
        sort_by = request.args.get('sort_by')
        sort_order = request.args.get('sort_order', 'asc')

        if sort_by:
            if sort_by in table.c:
                col = table.c[sort_by]
                if sort_order == 'desc':
                    query = query.order_by(desc(col))
                else:
                    query = query.order_by(asc(col))
            # Supporto ordinamento su relazioni (es. customer.name)
            elif '.' in sort_by:
                parts = sort_by.split('.')
                if len(parts) == 2:
                    rel_key, rel_col = parts
                    # Cerca la relazione corretta (gestisce sia 'customer' che 'customer_id')
                    target_info = relation_fields.get(rel_key) or relation_fields.get(f"{rel_key}_id")
                    
                    if target_info:
                        target_table = target_info['target_table']
                        if rel_col in target_table.c:
                            col = target_table.c[rel_col]
                            query = query.order_by(desc(col) if sort_order == 'desc' else asc(col))
        elif 'id' in table.c:
            query = query.order_by(desc(table.c.id))

        query = query.limit(per_page).offset((page - 1) * per_page)
        
        # --- Esecuzione ---
        total_count = db.session.execute(count_query).scalar_one_or_none() or 0
        raw_results = db.session.execute(query).mappings().all()

        # --- Post-processing per Risultati Annidati ---
        result = _process_relational_results(raw_results, relation_fields, sys_model)
        
        headers = {
            'X-Total-Count': str(total_count),
            'X-Pages': str((total_count + per_page - 1) // per_page),
            'X-Current-Page': str(page),
            'X-Per-Page': str(per_page)
        }

        # Aggiungi Content-Range per compatibilità con React Admin
        start = (page - 1) * per_page
        if total_count == 0:
            headers['Content-Range'] = 'items */0'
        else:
            if len(result) == 0:
                headers['Content-Range'] = f'items */{total_count}'
            else:
                end = start + len(result) - 1
                headers['Content-Range'] = f'items {start}-{end}/{total_count}'
        
        return result, 200, headers

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self, model_name):
        """Crea un nuovo record in una tabella creata dinamicamente."""
        sys_model = SysModel.query.filter_by(name=model_name).first_or_404()
        check_model_permissions(sys_model, 'write')
        schema_name = f"project_{sys_model.project_id}"
        table = get_table_object(model_name, schema=schema_name)
            
        # Handle both JSON and Form data (for file uploads)
        if request.content_type and 'multipart/form-data' in request.content_type:
            json_data = request.form.to_dict()
            json_data = _handle_file_uploads(json_data, sys_model)
        else:
            json_data = request.get_json()
            if json_data is None:
                abort(400, message="Invalid JSON data.")
            
        # --- Validazione ---
        validated_data = {}
        for field in sys_model.fields:
            # Ignore computed fields on input
            if field.type in ['formula', 'summary', 'lookup', 'calculated', 'lines']:
                continue
            
            value = json_data.get(field.name)

            # Gestione Default Value (inclusi placeholder dinamici)
            if value is None and field.default_value:
                value = _evaluate_default_value(field.default_value, field.type)

            if field.required and value is None:
                abort(400, message=f"Missing required field: '{field.name}'")
            
            if value is not None:
                validated_data[field.name] = validate_value(field, value)
        
        # --- Check for uniqueness before insert ---
        for field in sys_model.fields:
            if field.is_unique and field.name in validated_data:
                value = validated_data[field.name]
                if value is not None:
                    exists_query = select(func.count()).select_from(table).where(table.c[field.name] == value)
                    if db.session.execute(exists_query).scalar_one() > 0:
                        abort(409, message=f"Value '{value}' for field '{field.name}' already exists.")

        stmt = insert(table).values(validated_data).returning(table)
        result = db.session.execute(stmt).mappings().one()
        
        # Handle Nested Writes (Lines)
        _handle_nested_writes(result.id, json_data, sys_model, schema=schema_name)
        log_audit(get_jwt_identity(), model_name, result.id, 'CREATE', validated_data)
        
        db.session.commit()
            
        # Serialize result
        result_dict = dict(result)
        for k, v in result_dict.items():
            result_dict[k] = serialize_value(v)

        return result_dict, 201

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(204)
    def delete(self, model_name):
        """Elimina record multipli."""
        sys_model = SysModel.query.filter_by(name=model_name).first_or_404()
        check_model_permissions(sys_model, 'write')
        schema_name = f"project_{sys_model.project_id}"
        table = get_table_object(model_name, schema=schema_name)

        data = request.get_json()
        ids_to_delete = data.get('ids')

        if not ids_to_delete or not isinstance(ids_to_delete, list):
            abort(400, message="A list of 'ids' is required for bulk delete.")

        # Log before deleting
        user_id = get_jwt_identity()
        for item_id in ids_to_delete:
            log_audit(user_id, model_name, item_id, 'DELETE')

        stmt = delete(table).where(table.c.id.in_(ids_to_delete))
        db.session.execute(stmt)
        db.session.commit()
        
        return ""

@blp.route("/data/<string:model_name>/<int:item_id>")
class DynamicDataItem(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, model_name, item_id):
        """Recupera un singolo record da una tabella dinamica."""
        sys_model = SysModel.query.filter_by(name=model_name).first_or_404()
        check_model_permissions(sys_model, 'read')
        schema_name = f"project_{sys_model.project_id}"
        table = get_table_object(model_name, schema=schema_name)

        query, relation_fields = _build_relational_query(sys_model, table, schema=schema_name)
        query = query.where(table.c.id == item_id)
        raw_result = db.session.execute(query).mappings().first()

        if not raw_result:
            abort(404, message="Item not found.")
        
        result = _process_relational_results(raw_result, relation_fields, sys_model)
        
        # Carica manualmente i dati delle linee (One-to-Many)
        # Questo è necessario perché _build_relational_query gestisce solo Many-to-One
        for field in sys_model.fields:
            if field.type == 'lines':
                try:
                    opts = json.loads(field.options)
                    target_table = get_table_object(opts['target_table'], schema=schema_name)
                    fk = opts['foreign_key']
                    lines_query = select(target_table).where(target_table.c[fk] == item_id)
                    lines_res = db.session.execute(lines_query).mappings().all()
                    result[field.name] = [dict(r) for r in lines_res]
                    # Serializza
                    for l in result[field.name]:
                        for k,v in l.items(): l[k] = serialize_value(v)
                except: pass

        return result

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def put(self, model_name, item_id):
        """Aggiorna un record in una tabella dinamica."""
        sys_model = SysModel.query.filter_by(name=model_name).first_or_404()
        check_model_permissions(sys_model, 'write')
        schema_name = f"project_{sys_model.project_id}"
        table = get_table_object(model_name, schema=schema_name)

        # Handle both JSON and Form data (for file uploads)
        if request.content_type and 'multipart/form-data' in request.content_type:
            json_data = request.form.to_dict()
            json_data = _handle_file_uploads(json_data, sys_model)
        else:
            json_data = request.get_json()
            if not json_data:
                abort(400, message="Invalid JSON data.")

        validated_data = {}
        for field in sys_model.fields:
            # Ignore computed fields on input
            if field.type in ['formula', 'summary', 'lookup', 'calculated', 'lines']:
                continue
            if field.name in json_data:
                validated_data[field.name] = validate_value(field, json_data[field.name])

        # --- Check for uniqueness before update ---
        for field in sys_model.fields:
            if field.is_unique and field.name in validated_data:
                value = validated_data[field.name]
                if value is not None:
                    exists_query = select(func.count()).select_from(table).where(
                        table.c[field.name] == value,
                        table.c.id != item_id
                    )
                    if db.session.execute(exists_query).scalar_one() > 0:
                        abort(409, message=f"Value '{value}' for field '{field.name}' already exists.")

        stmt = update(table).where(table.c.id == item_id).values(validated_data).returning(table)
        result = db.session.execute(stmt).mappings().one()
        
        # Handle Nested Writes (Lines)
        _handle_nested_writes(item_id, json_data, sys_model, schema=schema_name)
        log_audit(get_jwt_identity(), model_name, item_id, 'UPDATE', validated_data)
        
        db.session.commit()

        # Serialize result
        result_dict = dict(result)
        for k, v in result_dict.items():
            result_dict[k] = serialize_value(v)

        return result_dict

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(204)
    def delete(self, model_name, item_id):
        """Elimina un record da una tabella dinamica."""
        SysModel.query.filter_by(name=model_name).first_or_404()
        check_model_permissions(sys_model, 'write')
        schema_name = f"project_{sys_model.project_id}"
        table = get_table_object(model_name, schema=schema_name)

        stmt = delete(table).where(table.c.id == item_id)
        db.session.execute(stmt)
        log_audit(get_jwt_identity(), model_name, item_id, 'DELETE')
        db.session.commit()
        return ""

@blp.route("/data/<string:model_name>/meta")
class DynamicModelMeta(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, SysModelSchema)
    def get(self, model_name):
        """Recupera i metadati di un modello dinamico per il frontend."""
        try:
            sys_model = SysModel.query.filter_by(name=model_name).first_or_404()
            check_model_permissions(sys_model, 'read')
            
            # Trigger lazy loading of fields to catch potential DB errors within this try block
            _ = sys_model.fields
            
            return sys_model
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error fetching metadata for {model_name}: {e}", file=sys.stderr)
            abort(500, message=f"Internal Server Error: {str(e)}")

@blp.route("/data/<string:model_name>/<int:item_id>/clone")
class DynamicDataClone(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self, model_name, item_id):
        """Clona un record esistente."""
        sys_model = SysModel.query.filter_by(name=model_name).first_or_404()
        check_model_permissions(sys_model, 'write')
        schema_name = f"project_{sys_model.project_id}"
        table = get_table_object(model_name, schema=schema_name)

        # Recupera il record originale
        query = select(table).where(table.c.id == item_id)
        source_record = db.session.execute(query).mappings().first()

        if not source_record:
            abort(404, message="Item not found.")

        # Copia i dati (solo i campi definiti nel modello, escludendo id/timestamp)
        new_data = {}
        for field in sys_model.fields:
            if field.name in source_record:
                new_data[field.name] = source_record[field.name]

        stmt = insert(table).values(new_data).returning(table)
        result = db.session.execute(stmt).mappings().one()
        log_audit(get_jwt_identity(), model_name, result.id, 'CLONE', {'source_id': item_id})
        db.session.commit()

        # Serialize result
        result_dict = dict(result)
        for k, v in result_dict.items():
            result_dict[k] = serialize_value(v)

        return result_dict, 201

@blp.route("/audit-logs")
class AuditLogList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, AuditLogSchema(many=True))
    def get(self):
        """Recupera i log di audit (solo admin)."""
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if user.role != 'admin':
            abort(403, message="Access denied")
            
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        query = AuditLog.query.order_by(desc(AuditLog.timestamp))
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return pagination.items

@blp.route("/data/<string:model_name>/import")
class DynamicDataImport(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self, model_name):
        """Importa dati da CSV."""
        sys_model = SysModel.query.filter_by(name=model_name).first_or_404()
        check_model_permissions(sys_model, 'write')
        schema_name = f"project_{sys_model.project_id}"
        table = get_table_object(model_name, schema=schema_name)

        if 'file' not in request.files:
            abort(400, message="No file part")
        
        file = request.files['file']
        if file.filename == '':
            abort(400, message="No selected file")
            
        if not file.filename.lower().endswith('.csv'):
            abort(400, message="File must be a CSV")

        try:
            stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
            csv_input = csv.DictReader(stream)
        except Exception as e:
            abort(400, message=f"Error reading CSV: {str(e)}")

        valid_fields = {f.name: f for f in sys_model.fields}
        
        inserted_count = 0
        errors = []
        
        for i, row in enumerate(csv_input):
            row_data = {}
            try:
                # Filter columns that exist in model
                for col, val in row.items():
                    if col in valid_fields:
                        field = valid_fields[col]
                        # Skip computed fields
                        if field.type in ['formula', 'summary', 'lookup', 'calculated', 'lines']:
                            continue
                        
                        # Handle empty strings
                        if val == '':
                            val = None
                        
                        if val is not None:
                            # Validate and convert
                            try:
                                row_data[col] = validate_value(field, val)
                            except HTTPException as e:
                                # Extract message from abort()
                                msg = e.description if hasattr(e, 'description') else str(e)
                                raise ValueError(msg)

                # Check required fields and defaults
                for field in sys_model.fields:
                    if field.type in ['formula', 'summary', 'lookup', 'calculated', 'lines']:
                        continue
                    
                    if field.name not in row_data:
                        if field.default_value:
                            row_data[field.name] = _evaluate_default_value(field.default_value, field.type)
                        elif field.required:
                            raise ValueError(f"Missing required field: {field.name}")

                # Check uniqueness (Basic check, might be slow for large imports)
                for field in sys_model.fields:
                    if field.is_unique and field.name in row_data:
                        val = row_data[field.name]
                        if val is not None:
                            exists_query = select(func.count()).select_from(table).where(table.c[field.name] == val)
                            if db.session.execute(exists_query).scalar_one() > 0:
                                raise ValueError(f"Value '{val}' for field '{field.name}' already exists.")

                stmt = insert(table).values(row_data)
                db.session.execute(stmt)
                inserted_count += 1
            except Exception as e:
                errors.append(f"Row {i+2}: {str(e)}") # i+2 because i starts at 0 and header is row 1
        
        if inserted_count > 0:
            log_audit(get_jwt_identity(), model_name, 0, 'IMPORT', {'count': inserted_count})
            db.session.commit()
        
        return {
            "message": f"Imported {inserted_count} records.",
            "errors": errors
        }, 200