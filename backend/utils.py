from flask import request
from sqlalchemy import or_, desc, asc, func, inspect
import json
import datetime
import decimal
from .extensions import db
from .models import AuditLog

def apply_filters(query, model, search_fields):
    """Applica filtri di ricerca testuale (q) alla query."""
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
    """Applica ordinamento alla query basato su sort_by e sort_order."""
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
    """Applica filtri per range di date (date_from, date_to)."""
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

    # Computed fields are not real columns
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

def _get_foreign_key_definition(field):
    """Helper to build a FOREIGN KEY constraint string."""
    if field.type == 'relation' and field.options:
        try:
            options = json.loads(field.options)
            target_table = options.get('target_table')
            if target_table and target_table.isidentifier():
                return f'FOREIGN KEY ("{field.name}") REFERENCES "{target_table}"(id) ON DELETE SET NULL'
        except (json.JSONDecodeError, KeyError):
            pass
    return None

def generate_create_table_sql(sys_model):
    """
    Genera una stringa SQL 'CREATE TABLE' da un oggetto SysModel, gestendo le relazioni.
    """
    # Mappatura dei tipi di campo a tipi di colonna PostgreSQL
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

        # Gestione delle relazioni (FOREIGN KEY)
        fk_def = _get_foreign_key_definition(field)
        if fk_def:
            foreign_keys.append(fk_def)

    all_definitions = columns + foreign_keys
    sql = f'CREATE TABLE IF NOT EXISTS "{table_name}" (\n    ' + ',\n    '.join(all_definitions) + '\n);'
    return sql

def generate_schema_diff_sql(sys_model, db_engine):
    """
    Compares a SysModel to the live database schema and generates ALTER TABLE statements.
    """
    inspector = inspect(db_engine)
    table_name = sys_model.name

    if not inspector.has_table(table_name):
        return [generate_create_table_sql(sys_model)]

    sql_commands = []
    db_columns = {c['name']: c for c in inspector.get_columns(table_name)}
    model_fields = {f.name: f for f in sys_model.fields if f.type not in ['formula', 'summary', 'lookup', 'calculated']}
    type_mapping = _get_type_mapping()
    
    # Get existing unique constraints
    # unique_constraints is a list of dicts: [{'name': '...', 'column_names': ['...'], ...}]
    db_unique_constraints = inspector.get_unique_constraints(table_name)
    # Map column name to constraint name for single-column unique constraints
    db_unique_map = {uc['column_names'][0]: uc['name'] 
                     for uc in db_unique_constraints if len(uc['column_names']) == 1}
    
    # Get existing foreign keys
    # foreign_keys is a list of dicts: [{'name': '...', 'constrained_columns': ['...'], 'referred_table': '...', ...}]
    db_foreign_keys = inspector.get_foreign_keys(table_name)
    # Map column name to constraint name for single-column foreign keys
    db_fk_map = {fk['constrained_columns'][0]: fk['name'] 
                 for fk in db_foreign_keys if len(fk['constrained_columns']) == 1}

    db_column_names = set(db_columns.keys()) - {'id', 'created_at', 'updated_at'}
    model_field_names = set(model_fields.keys())

    # --- 1. Find columns to ADD ---
    for field_name in model_field_names - db_column_names:
        field = model_fields[field_name]
        col_def = _build_column_definition(field)
        if col_def:
            sql_commands.append(f'ALTER TABLE "{table_name}" ADD COLUMN {col_def};')

    # --- 2. Find columns to DROP ---
    for col_name in db_column_names - model_field_names:
        sql_commands.append(f'ALTER TABLE "{table_name}" DROP COLUMN "{col_name}" CASCADE;')

    # --- 3. Find columns to MODIFY (NOT NULL, TYPE, UNIQUE, and FK changes) ---
    for field_name in model_field_names.intersection(db_column_names):
        field = model_fields[field_name]
        db_col = db_columns[field_name]
        
        # Check NOT NULL constraint
        is_db_nullable = db_col.get('nullable', True)
        if field.required and is_db_nullable:
            sql_commands.append(f'ALTER TABLE "{table_name}" ALTER COLUMN "{field_name}" SET NOT NULL;')
        elif not field.required and not is_db_nullable:
            sql_commands.append(f'ALTER TABLE "{table_name}" ALTER COLUMN "{field_name}" DROP NOT NULL;')

        # Check TYPE changes
        target_type_str = type_mapping.get(field.type)
        if target_type_str:
            # Extract base type (e.g., 'VARCHAR' from 'VARCHAR(255)') for comparison
            target_base_type = target_type_str.split('(')[0]
            # DB type from inspector is usually an object, convert to string
            current_db_type = str(db_col['type']).upper()
            
            # Simple heuristic comparison (can be improved)
            # e.g. if target is TEXT and current is VARCHAR, we might want to alter
            # Note: SQLAlchemy inspector types can be complex (e.g. VARCHAR(255)), so we check containment or exact match
            if target_base_type not in current_db_type and current_db_type not in target_type_str:
                 # Generate ALTER COLUMN TYPE with USING clause for safe conversion
                 # The USING clause is critical for casting (e.g. text to integer)
                 using_clause = f'USING "{field_name}"::{target_type_str}'
                 # Special case for boolean: cast from integer 0/1 or strings
                 if field.type == 'boolean':
                     using_clause = f'USING CASE WHEN "{field_name}" IN (\'true\', \'1\', \'t\', \'y\', \'yes\') THEN TRUE ELSE FALSE END'
                 
                 sql_commands.append(f'ALTER TABLE "{table_name}" ALTER COLUMN "{field_name}" TYPE {target_type_str} {using_clause};')

    return sql_commands

def serialize_value(value):
    """Converte tipi speciali (date, decimali) in formati JSON-serializzabili."""
    if isinstance(value, (datetime.datetime, datetime.date)):
        return value.isoformat()
    if isinstance(value, decimal.Decimal):
        return float(value)
    return value

def paginate(query):
    """Pagina la query e restituisce items e headers per il frontend."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    headers = {
        'X-Total-Count': str(pagination.total),
        'X-Pages': str(pagination.pages),
        'X-Current-Page': str(pagination.page),
        'X-Per-Page': str(pagination.per_page),
    }
    
    # Aggiungi Content-Range per compatibilità con React Admin e altri frontend
    start = (pagination.page - 1) * pagination.per_page
    end = start + len(pagination.items) - 1
    if pagination.total == 0:
        headers['Content-Range'] = 'items */0'
    else:
        # Gestione caso pagina vuota o fuori range
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