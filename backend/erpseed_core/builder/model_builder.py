"""
Model Builder - Creates data models with fields and tables
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class Field:
    """Represents a model field"""
    name: str
    type: str
    title: str = ""
    description: str = ""
    required: bool = False
    unique: bool = False
    default: Any = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    choices: List[str] = field(default_factory=list)
    related_model: Optional[str] = None
    on_delete: Optional[str] = None
    widget: str = "text"
    visible: bool = True
    editable: bool = True


@dataclass
class Model:
    """Represents a data model"""
    name: str
    technical_name: str
    table_name: str
    title: str = ""
    description: str = ""
    fields: List[Field] = field(default_factory=list)
    permissions: Dict[str, List[str]] = field(default_factory=dict)
    settings: Dict[str, Any] = field(default_factory=dict)


class ModelBuilder:
    """Builds data models from JSON configuration"""
    
    def __init__(self):
        self.models: Dict[str, Model] = {}
    
    def build(self, data: Dict[str, Any]) -> Model:
        """Build a model from JSON data"""
        fields = []
        for field_data in data.get("fields", []):
            field_obj = Field(
                name=field_data["name"],
                type=field_data.get("type", "string"),
                title=field_data.get("title", field_data["name"]),
                description=field_data.get("description", ""),
                required=field_data.get("required", False),
                unique=field_data.get("unique", False),
                default=field_data.get("default"),
                min_length=field_data.get("min_length"),
                max_length=field_data.get("max_length"),
                min_value=field_data.get("min_value"),
                max_value=field_data.get("max_value"),
                choices=field_data.get("choices", []),
                related_model=field_data.get("related_model"),
                on_delete=field_data.get("on_delete"),
                widget=field_data.get("widget", "text"),
                visible=field_data.get("visible", True),
                editable=field_data.get("editable", True),
            )
            fields.append(field_obj)
        
        model = Model(
            name=data["name"],
            technical_name=data["technical_name"],
            table_name=data.get("table_name", data["technical_name"].lower()),
            title=data.get("title", data["name"]),
            description=data.get("description", ""),
            fields=fields,
            permissions=data.get("permissions", {}),
            settings=data.get("settings", {}),
        )
        
        self.models[model.technical_name] = model
        return model
    
    def get_model(self, technical_name: str) -> Optional[Model]:
        """Get a model by technical name"""
        return self.models.get(technical_name)
    
    def list_models(self) -> List[Model]:
        """List all built models"""
        return list(self.models.values())
    
    def to_dict(self, model: Model) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            "name": model.name,
            "technical_name": model.technical_name,
            "table_name": model.table_name,
            "title": model.title,
            "description": model.description,
            "fields": [
                {
                    "name": f.name,
                    "type": f.type,
                    "title": f.title,
                    "description": f.description,
                    "required": f.required,
                    "unique": f.unique,
                    "default": f.default,
                    "min_length": f.min_length,
                    "max_length": f.max_length,
                    "min_value": f.min_value,
                    "max_value": f.max_value,
                    "choices": f.choices,
                    "related_model": f.related_model,
                    "on_delete": f.on_delete,
                    "widget": f.widget,
                    "visible": f.visible,
                    "editable": f.editable,
                }
                for f in model.fields
            ],
            "permissions": model.permissions,
            "settings": model.settings,
        }
