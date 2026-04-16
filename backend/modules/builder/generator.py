"""
Builder Code Generator - Genera codice Python dai template.
"""
import textwrap
from typing import List, Dict, Any, Optional
from backend.models import SysModel, SysField


class CodeGenerator:
    """Genera codice Python da template SysModel/SysField."""

    TYPE_MAPPING = {
        'string': 'db.String(255)',
        'integer': 'db.Integer',
        'float': 'db.Float',
        'boolean': 'db.Boolean',
        'date': 'db.Date',
        'datetime': 'db.DateTime',
        'text': 'db.Text',
        'select': 'db.String(50)',
        'file': 'db.String(500)',
        'json': 'db.JSON',
    }

    def generate_model(self, model: SysModel) -> str:
        """Genera codice SQLAlchemy per un modello."""
        lines = [
            f"class {self._class_name(model.name)}(BaseModel):",
            f'    __tablename__ = "{model.name}"',
            "",
            "    id = db.Column(db.Integer, primary_key=True)",
        ]

        for field in sorted(model.fields, key=lambda f: f.order):
            col_def = self._generate_field(field)
            lines.append(f"    {field.name} = {col_def}")

        lines.extend([
            "",
            "    def to_dict(self):",
            "        return {",
        ])

        for field in model.fields:
            lines.append(f"            '{field.name}': self.{field.name},")

        lines.append("        }")

        return "\n".join(lines)

    def _class_name(self, name: str) -> str:
        """Converte nome tabella in nome classe."""
        return ''.join(word.capitalize() for word in name.split('_'))

    def _generate_field(self, field: SysField) -> str:
        """Genera definizione colonna."""
        col_type = self.TYPE_MAPPING.get(field.type, 'db.String(255)')
        col = f"db.Column({col_type})"

        opts = []
        if field.required:
            opts.append('nullable=False')
        if field.is_unique:
            opts.append('unique=True')
        if field.default_value:
            default = field.default_value
            if field.type == 'integer':
                try:
                    default = int(default)
                except ValueError:
                    default = f"'{default}'"
            elif field.type == 'boolean':
                default = default.lower() in ('true', '1', 'yes')
            elif field.type not in ('integer', 'float', 'boolean'):
                default = f"'{default}'"
            opts.append(f'default={default}')

        if field.options:
            try:
                import json
                options = json.loads(field.options)
                if isinstance(options, dict) and 'default' in options:
                    opts.append(f'default={repr(options["default"])}')
            except:
                pass

        if opts:
            col = f"db.Column({col_type}, {', '.join(opts)})"

        return col

    def generate_api(self, model: SysModel, api_prefix: str = '/api') -> str:
        """Genera codice API REST per un modello."""
        name = model.name.lower()
        class_name = self._class_name(model.name)

        return textwrap.dedent(f'''\
        from flask import Blueprint, request, jsonify
        from backend.extensions import db
        from backend.models import {class_name}

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
            for key, value in data.items():
                setattr(item, key, value)
            db.session.commit()
            return jsonify(item.to_dict())


        @bp.route('/<int:id>', methods=['DELETE'])
        def delete_{name}(id):
            item = {class_name}.query.get_or_404(id)
            db.session.delete(item)
            db.session.commit()
            return '', 204
        ''')

    def generate_crud_service(self, model: SysModel) -> str:
        """Genera codice service CRUD."""
        class_name = self._class_name(model.name)
        name = model.name.lower()

        return textwrap.dedent(f'''\
        class {class_name}Service:
            """Service per la gestione di {model.title or model.name}."""

            def get_all(self, filters=None):
                query = {class_name}.query
                if filters:
                    for key, value in filters.items():
                        if hasattr({class_name}, key):
                            query = query.filter(getattr({class_name}, key) == value)
                return query.all()

            def get_by_id(self, id):
                return {class_name}.query.get(id)

            def create(self, data):
                item = {class_name}(**data)
                db.session.add(item)
                db.session.commit()
                return item

            def update(self, id, data):
                item = {class_name}.query.get_or_404(id)
                for key, value in data.items():
                    setattr(item, key, value)
                db.session.commit()
                return item

            def delete(self, id):
                item = {class_name}.query.get_or_404(id)
                db.session.delete(item)
                db.session.commit()
        ''')

    def generate_module(self, model: SysModel, api_prefix: str = '/api') -> Dict[str, str]:
        """Genera un modulo completo."""
        return {
            'model': self.generate_model(model),
            'api': self.generate_api(model, api_prefix),
            'service': self.generate_crud_service(model),
        }


class TemplateValidator:
    """Valida template prima della generazione."""

    def validate(self, model: SysModel) -> List[str]:
        """Valida un modello e ritorna lista errori."""
        errors = []

        if not model.name:
            errors.append("Il nome del modello è obbligatorio")

        if not model.fields:
            errors.append(f"Il modello '{model.name}' non ha campi definiti")

        field_names = set()
        for field in model.fields:
            if not field.name:
                errors.append("Trovato campo senza nome")
            elif field.name in field_names:
                errors.append(f"Nome campo duplicato: {field.name}")
            field_names.add(field.name)

            if field.type not in CodeGenerator.TYPE_MAPPING:
                errors.append(f"Tipo non supportato: {field.type}")

        return errors


class AdaptiveBuilder:
    """Builder principale che coordina parser, generator e migrator."""

    def __init__(self, app=None, db=None):
        self.app = app
        self.db = db
        self.generator = CodeGenerator()
        self.validator = TemplateValidator()

    def build_from_model(self, model: SysModel, api_prefix: str = '/api') -> Dict[str, str]:
        """Build di un modulo da un SysModel esistente."""
        errors = self.validator.validate(model)
        if errors:
            raise ValueError(f"Validation errors: {', '.join(errors)}")

        return self.generator.generate_module(model, api_prefix)

    def build_from_template(self, template_data: Dict[str, Any]) -> Dict[str, str]:
        """Build da template JSON/dict."""
        from backend.modules.builder.service import get_builder_service as BuilderService

        if not self.app or not self.db:
            raise RuntimeError("App e DB devono essere inizializzati")

        service = BuilderService()

        model = service.create_model(
            project_id=template_data.get('project_id'),
            name=template_data['name'],
            title=template_data.get('title', template_data['name']),
            description=template_data.get('description'),
        )

        for field_data in template_data.get('fields', []):
            service.create_field(
                model_id=model.id,
                name=field_data['name'],
                field_type=field_data['type'],
                title=field_data.get('title'),
                required=field_data.get('required', False),
                is_unique=field_data.get('unique', False),
                default_value=field_data.get('default'),
                options=field_data.get('options'),
            )

        self.db.session.refresh(model)

        return self.build_from_model(model, template_data.get('api_prefix', '/api'))
