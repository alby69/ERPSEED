"""
Builder Code Generator - Genera codice Python dai template.
"""
import textwrap
from typing import List, Dict, Any, Optional
from backend.models import SysModel, SysField


from backend.core.scaffold.generator import CodeGenerator as CoreCodeGenerator


class CodeGenerator:
    """
    Adapter wrapper over core scaffold CodeGenerator to ensure backward compatibility and DRY principles.
    """

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

    def __init__(self):
        self._core_gen = CoreCodeGenerator()

    def generate_module(self, model: SysModel, api_prefix: str = '/api') -> Dict[str, str]:
        """Generates backend code files using centralized CoreCodeGenerator."""
        fields_data = [
            {
                "name": f.name,
                "type": f.type if f.type in self.TYPE_MAPPING else "string",
                "required": f.required,
                "unique": f.is_unique,
                "default": f.default_value,
            }
            for f in sorted(model.fields, key=lambda x: x.order)
        ]

        class_name = ''.join(word.capitalize() for word in model.name.split('_'))
        generated = self._core_gen.generate_backend(
            module_name="builder",
            entity_name=class_name,
            fields=fields_data,
            relations=[],
            metadata={"label": model.title or model.name},
        )

        return {
            'model': generated.get('models.py', ''),
            'api': generated.get('rest_api.py', ''),
            'service': generated.get('handlers.py', ''),
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
            projectId=template_data.get('projectId'),
            name=template_data['name'],
            title=template_data.get('title', template_data['name']),
            description=template_data.get('description'),
        )

        for field_data in template_data.get('fields', []):
            service.create_field(
                modelId=model.id,
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
