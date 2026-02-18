from flask import request
from sqlalchemy import or_, desc, asc, func, inspect, Table
import json
import decimal
from datetime import datetime
from .extensions import db
from flask_smorest import abort

# Import AuditLog from core if available, else create dummy
try:
    from backend.core.models import AuditLog
except ImportError:
    # Fallback for migration period
    class AuditLog:
        @staticmethod
        def log_create(*args, **kwargs):
            pass
        @staticmethod
        def log_login(*args, **kwargs):
            pass

def apply_filters(query, model, search_fields):
    """Apply text search filters (q) to the query."""
    q = request.args.get('q')
    if q and search_fields:
        filters = []
        for field in search_fields:
            if hasattr(model, field):
                filters.append(getattr(model, field).ilike(f"%{q}%"))
        if filters:
            query = query.filter(or_(*filters))
    return query

def apply_sorting(query, model):
    """Apply sorting to the query based on sort_by and sort_order."""
    sort_by = request.args.get('sort_by')
    sort_order = request.args.get('sort_order', 'asc')

    if sort_by and hasattr(model, sort_by):
        column = getattr(model, sort_by)
        if sort_order == 'desc':
            query = query.order_by(desc(column))
        else:
            query = query.order_by(asc(column))
    return query

def apply_date_filters(query, model, date_field='created_at'):
    """Apply date range filters (date_from, date_to)."""
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')

    if hasattr(model, date_field):
        column = getattr(model, date_field)
        if date_from:
            query = query.filter(column >= date_from)
        if date_to:
            query = query.filter(func.date(column) <= date_to)
    return query

def _get_type_mapping():
    return {
        'string': 'VARCHAR(255)', 'text': 'TEXT', 'integer': 'INTEGER',
        'float': 'FLOAT', 'boolean': 'BOOLEAN', 'date': 'DATE',
        'datetime': 'TIMESTAMP', 'relation': 'INTEGER', 'select': 'VARCHAR(255)',
        'file': 'VARCHAR(255)', 'image': 'VARCHAR(255)',
        'currency': 'FLOAT',
        'tags': 'TEXT',
        'color': 'VARCHAR(20)'
    }

def _build_column_definition(field):
    """Helper to build a single column's SQL definition string from a SysField."""
    type_mapping = _get_type_mapping()

    if field.type in ['formula', 'summary', 'lookup', 'calculated']:
        return None

    column_type = type_mapping.get(field.type)
    if not column_type:
        return None

    column_def = f'"{field.name}" {column_type}'
    if field.required:
        column_def += ' NOT NULL'

    if field.is_unique:
        column_def += ' UNIQUE'

    if field.default_value is not None:
        if field.type in ['string', 'text', 'date', 'datetime', 'select', 'file', 'image']:
            escaped_default = field.default_value.replace("'", "''")
            column_def += f" DEFAULT '{escaped_default}'"
        else:
            column_def += f" DEFAULT {field.default_value}"

    return column_def

def _get_foreign_key_definition(field, schema=None):
    """Helper to build a FOREIGN KEY constraint string."""
    if field.type == 'relation' and field.options:
        try:
            options = json.loads(field.options)
            target_table = options.get('target_table')
            if target_table and target_table.isidentifier():
                target = f'"{schema}"."{target_table}"' if schema else f'"{target_table}"'
                return f'FOREIGN KEY ("{field.name}") REFERENCES {target}(id) ON DELETE SET NULL'
        except (json.JSONDecodeError, KeyError):
            pass
    return None

def generate_create_table_sql(sys_model, schema=None):
    """
    Generate a 'CREATE TABLE' SQL string from a SysModel object, handling relations.
    """
    type_mapping = _get_type_mapping()

    table_name = sys_model.name
    if not table_name or not table_name.isidentifier():
        raise ValueError(f"Invalid table name: {table_name}")

    columns = [
        'id SERIAL PRIMARY KEY',
        'created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP',
        'updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP'
    ]
    foreign_keys = []
    
    for field in sys_model.fields:
        if not field.name or not field.name.isidentifier():
            continue

        col_def = _build_column_definition(field)
        if col_def:
            columns.append(col_def)

        fk_def = _get_foreign_key_definition(field, schema=schema)
        if fk_def:
            foreign_keys.append(fk_def)

    all_definitions = columns + foreign_keys
    
    full_table_name = f'"{schema}"."{table_name}"' if schema else f'"{table_name}"'
    sql = f'CREATE TABLE IF NOT EXISTS {full_table_name} (\n    ' + ',\n    '.join(all_definitions) + '\n);'
    return sql

def generate_schema_diff_sql(sys_model, db_engine, schema=None):
    """
    Compares a SysModel to the live database schema and generates ALTER TABLE statements.
    """
    inspector = inspect(db_engine)
    table_name = sys_model.name

    if not inspector.has_table(table_name, schema=schema):
        return [generate_create_table_sql(sys_model, schema=schema)]

    sql_commands = []
    db_columns = {c['name']: c for c in inspector.get_columns(table_name, schema=schema)}
    model_fields = {f.name: f for f in sys_model.fields if f.type not in ['formula', 'summary', 'lookup', 'calculated']}
    type_mapping = _get_type_mapping()
    
    table_identifier = f'"{schema}"."{table_name}"' if schema else f'"{table_name}"'

    db_unique_constraints = inspector.get_unique_constraints(table_name, schema=schema)
    db_unique_map = {uc['column_names'][0]: uc['name'] 
                     for uc in db_unique_constraints if len(uc['column_names']) == 1}
    
    db_foreign_keys = inspector.get_foreign_keys(table_name, schema=schema)
    db_fk_map = {fk['constrained_columns'][0]: fk['name'] 
                 for fk in db_foreign_keys if len(fk['constrained_columns']) == 1}

    db_column_names = set(db_columns.keys()) - {'id', 'created_at', 'updated_at'}
    model_field_names = set(model_fields.keys())

    for field_name in model_field_names - db_column_names:
        field = model_fields[field_name]
        col_def = _build_column_definition(field)
        if col_def:
            sql_commands.append(f'ALTER TABLE {table_identifier} ADD COLUMN {col_def};')

    for col_name in db_column_names - model_field_names:
        sql_commands.append(f'ALTER TABLE {table_identifier} DROP COLUMN "{col_name}" CASCADE;')

    for field_name in model_field_names.intersection(db_column_names):
        field = model_fields[field_name]
        db_col = db_columns[field_name]
        
        is_db_nullable = db_col.get('nullable', True)
        if field.required and is_db_nullable:
            sql_commands.append(f'ALTER TABLE {table_identifier} ALTER COLUMN "{field_name}" SET NOT NULL;')
        elif not field.required and not is_db_nullable:
            sql_commands.append(f'ALTER TABLE {table_identifier} ALTER COLUMN "{field_name}" DROP NOT NULL;')

        target_type_str = type_mapping.get(field.type)
        if target_type_str:
            target_base_type = target_type_str.split('(')[0]
            current_db_type = str(db_col['type']).upper()
            
            if target_base_type not in current_db_type and current_db_type not in target_type_str:
                 using_clause = f'USING "{field_name}"::{target_type_str}'
                 if field.type == 'boolean':
                     using_clause = f'USING CASE WHEN "{field_name}" IN (\'true\', \'1\', \'t\', \'y\', \'yes\') THEN TRUE ELSE FALSE END'
                 
                 sql_commands.append(f'ALTER TABLE {table_identifier} ALTER COLUMN "{field_name}" TYPE {target_type_str} {using_clause};')

    return sql_commands

def get_table_object(model_name, schema=None):
    """Reflect the database and return a SQLAlchemy Table object."""
    try:
        return Table(model_name, db.metadata, autoload_with=db.engine, schema=schema, extend_existing=True)
    except Exception as e:
        abort(404, message=f"Table '{model_name}' not found in the database. Please generate it first.")

def serialize_value(value):
    """Convert special types (dates, decimals) to JSON-serializable formats."""
    if isinstance(value, (datetime.datetime, datetime.date)):
        return value.isoformat()
    if isinstance(value, decimal.Decimal):
        return float(value)
    return value

def paginate(query):
    """Paginate the query and return items and headers for the frontend."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    headers = {
        'X-Total-Count': str(pagination.total),
        'X-Pages': str(pagination.pages),
        'X-Current-Page': str(pagination.page),
        'X-Per-Page': str(pagination.per_page),
    }
    
    start = (pagination.page - 1) * pagination.per_page
    end = start + len(pagination.items) - 1
    if pagination.total == 0:
        headers['Content-Range'] = 'items */0'
    else:
        if len(pagination.items) == 0:
            headers['Content-Range'] = f'items */{pagination.total}'
        else:
            headers['Content-Range'] = f'items {start}-{end}/{pagination.total}'
        
    return pagination.items, headers

def log_audit(user_id, model_name, record_id, action, changes=None):
    """Logs an audit entry."""
    log = AuditLog(
        user_id=user_id,
        model_name=model_name,
        record_id=record_id,
        action=action,
        changes=json.dumps(changes, default=str) if changes else None
    )
    db.session.add(log)
