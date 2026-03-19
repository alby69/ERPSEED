"""
Code Generator for Builder - Generates code from model definitions.
"""
import textwrap
from typing import Dict, Any, List

TYPE_MAPPING = {
    'string': 'db.String(255)', 'integer': 'db.Integer', 'float': 'db.Float', 'boolean': 'db.Boolean',
    'date': 'db.Date', 'datetime': 'db.DateTime', 'text': 'db.Text', 'select': 'db.String(50)',
    'file': 'db.String(500)', 'json': 'db.JSON',
}


def _class_name(name: str) -> str:
    return ''.join(word.capitalize() for word in name.split('_'))


def _generate_field(field) -> str:
    col_type = TYPE_MAPPING.get(field.get('type', 'string'), 'db.String(255)')
    col = f"db.Column({col_type})"
    opts = []
    if field.get('required'): opts.append('nullable=False')
    if field.get('is_unique') or field.get('unique'): opts.append('unique=True')
    default = field.get('default_value') or field.get('default')
    if default is not None:
        ftype = field.get('type', 'string')
        if ftype == 'integer':
            try: default = int(default)
            except: default = f"'{default}'"
        elif ftype == 'boolean': default = str(default).lower() in ('true', '1', 'yes')
        elif ftype not in ('integer', 'float', 'boolean'): default = f"'{default}'"
        opts.append(f'default={default}')
    if opts: col = f"db.Column({col_type}, {', '.join(opts)})"
    return col


def generate_model(model_data: Dict[str, Any]) -> str:
    name = model_data.get('name', '')
    fields = model_data.get('fields', [])
    lines = [f"class {_class_name(name)}(BaseModel):", f'    __tablename__ = "{name}"', "", "    id = db.Column(db.Integer, primary_key=True)"]
    for f in sorted(fields, key=lambda x: x.get('position', 0)):
        lines.append(f"    {f['name']} = {_generate_field(f)}")
    lines.extend(["", "    def to_dict(self):", "        return {"])
    for f in fields: lines.append(f"            '{f['name']}': self.{f['name']},")
    lines.append("        }")
    return "\n".join(lines)


def generate_api(model_data: Dict[str, Any], api_prefix: str = '/api') -> str:
    name = model_data.get('name', '').lower()
    class_name = _class_name(model_data.get('name', ''))
    return textwrap.dedent(f'''\
    from flask import Blueprint, request, jsonify
    from ..extensions import db
    from ..models import {class_name}
    
    bp = Blueprint('{name}', __name__, url_prefix='{api_prefix}/{name}')
    
    @bp.route('', methods=['GET'])
    def list_{name}():
        items = {class_name}.query.all()
        return jsonify([i.to_dict() for i in items])
    
    @bp.route('', methods=['POST'])
    def create_{name}():
        data = request.get_json()
        item = {class_name}(**data)
        db.session.add(item)
        db.session.commit()
        return jsonify(item.to_dict()), 201
    
    @bp.route('/<int:id>', methods=['GET'])
    def get_{name}(id):
        item = {class_name}.query.get_or_404(id)
        return jsonify(item.to_dict())
    
    @bp.route('/<int:id>', methods=['PUT'])
    def update_{name}(id):
        item = {class_name}.query.get_or_404(id)
        data = request.get_json()
        for key, value in data.items(): setattr(item, key, value)
        db.session.commit()
        return jsonify(item.to_dict())
    
    @bp.route('/<int:id>', methods=['DELETE'])
    def delete_{name}(id):
        item = {class_name}.query.get_or_404(id)
        db.session.delete(item)
        db.session.commit()
        return '', 204
    ''')


def generate_crud_service(model_data: Dict[str, Any]) -> str:
    class_name = _class_name(model_data.get('name', ''))
    name = model_data.get('name', '').lower()
    return textwrap.dedent(f'''\
    class {class_name}Service:
        """Service per la gestione di {model_data.get('title') or model_data.get('name')}."""
        
        def get_all(self, filters=None):
            query = {class_name}.query
            if filters:
                for key, value in filters.items():
                    if hasattr({class_name}, key): query = query.filter(getattr({class_name}, key) == value)
            return query.all()
        
        def get_by_id(self, id): return {class_name}.query.get(id)
        
        def create(self, data):
            item = {class_name}(**data)
            db.session.add(item)
            db.session.commit()
            return item
        
        def update(self, id, data):
            item = {class_name}.query.get_or_404(id)
            for key, value in data.items(): setattr(item, key, value)
            db.session.commit()
            return item
        
        def delete(self, id):
            item = {class_name}.query.get_or_404(id)
            db.session.delete(item)
            db.session.commit()
    ''')


def generate_module(model_data: Dict[str, Any], api_prefix: str = '/api') -> Dict[str, str]:
    return {'model': generate_model(model_data), 'api': generate_api(model_data, api_prefix), 'service': generate_crud_service(model_data)}


def validate_model(model_data: Dict[str, Any]) -> List[str]:
    errors = []
    if not model_data.get('name'): errors.append("Il nome del modello è obbligatorio")
    if not model_data.get('fields'): errors.append(f"Il modello '{model_data.get('name', '')}' non ha campi definiti")
    field_names = set()
    for f in model_data.get('fields', []):
        if not f.get('name'): errors.append("Trovato campo senza nome")
        elif f['name'] in field_names: errors.append(f"Nome campo duplicato: {f['name']}")
        else: field_names.add(f['name'])
        if f.get('type') not in TYPE_MAPPING: errors.append(f"Tipo non supportato: {f.get('type')}")
    return errors
