"""
Domain Entities for Builder Service.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional


@dataclass
class FieldDefinition:
    """Represents a field definition in a model."""

    id: Optional[int] = None
    name: str = ""
    technical_name: str = ""
    type: str = "string"
    label: str = ""
    description: str = ""
    required: bool = False
    unique: bool = False
    default_value: Any = None
    options: Dict[str, Any] = field(default_factory=dict)
    position: int = 0

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "technical_name": self.technical_name,
            "type": self.type,
            "label": self.label,
            "description": self.description,
            "required": self.required,
            "unique": self.unique,
            "default_value": self.default_value,
            "options": self.options,
            "position": self.position,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "FieldDefinition":
        return cls(
            id=data.get("id"),
            name=data.get("name", ""),
            technical_name=data.get("technical_name", ""),
            type=data.get("type", "string"),
            label=data.get("label", ""),
            description=data.get("description", ""),
            required=data.get("required", False),
            unique=data.get("unique", False),
            default_value=data.get("default_value"),
            options=data.get("options", {}),
            position=data.get("position", 0),
        )


@dataclass
class ViewDefinition:
    """Represents a view configuration for a model."""

    id: Optional[int] = None
    name: str = ""
    type: str = "list"
    config: Dict[str, Any] = field(default_factory=dict)
    is_default: bool = False

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "config": self.config,
            "is_default": self.is_default,
        }


@dataclass
class ModelDefinition:
    """Represents a model definition (SysModel)."""

    id: Optional[int] = None
    project_id: int = 0
    name: str = ""
    technical_name: str = ""
    title: str = ""
    description: str = ""
    table_name: str = ""
    status: str = "draft"
    permissions: Dict[str, Any] = field(default_factory=dict)
    fields: List[FieldDefinition] = field(default_factory=list)
    views: List[ViewDefinition] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def add_field(self, field_def: FieldDefinition) -> None:
        """Add a field to the model."""
        self.fields.append(field_def)

    def remove_field(self, field_name: str) -> bool:
        """Remove a field by name."""
        for i, f in enumerate(self.fields):
            if f.technical_name == field_name:
                self.fields.pop(i)
                return True
        return False

    def get_field(self, field_name: str) -> Optional[FieldDefinition]:
        """Get a field by name."""
        for f in self.fields:
            if f.technical_name == field_name:
                return f
        return None

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "project_id": self.project_id,
            "name": self.name,
            "technical_name": self.technical_name,
            "title": self.title,
            "description": self.description,
            "table_name": self.table_name,
            "status": self.status,
            "permissions": self.permissions,
            "fields": [f.to_dict() for f in self.fields],
            "views": [v.to_dict() for v in self.views],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "ModelDefinition":
        fields = [FieldDefinition.from_dict(f) for f in data.get("fields", [])]
        views = [ViewDefinition(**v) for v in data.get("views", [])]
        return cls(
            id=data.get("id"),
            project_id=data.get("project_id", 0),
            name=data.get("name", ""),
            technical_name=data.get("technical_name", ""),
            title=data.get("title", ""),
            description=data.get("description", ""),
            table_name=data.get("table_name", ""),
            status=data.get("status", "draft"),
            permissions=data.get("permissions", {}),
            fields=fields,
            views=views,
        )
