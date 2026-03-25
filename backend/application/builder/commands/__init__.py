"""
Builder Commands - Model, Component, Block, Archetype.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List

from backend.shared.commands import Command, CreateCommand, UpdateCommand, DeleteCommand, QueryCommand


# === MODEL COMMANDS ===
@dataclass
class CreateModelCommand(CreateCommand):
    project_id: int = 0; name: str = ""; title: str = ""; description: str = ""; table_name: str = ""

    def to_payload(self) -> Dict[str, Any]:
        return {"project_id": self.project_id, "name": self.name, "title": self.title, "description": self.description,
            "table_name": self.table_name or self.name.lower().replace(" ", "_")}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CreateModelCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            project_id=data.get("project_id", 0), name=data.get("name", ""), title=data.get("title", ""),
            description=data.get("description", ""), table_name=data.get("table_name", ""))


@dataclass
class UpdateModelCommand(UpdateCommand):
    title: Optional[str] = None; description: Optional[str] = None; status: Optional[str] = None

    def to_payload(self) -> Dict[str, Any]:
        return {k: v for k, v in {"title": self.title, "description": self.description, "status": self.status}.items() if v is not None}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UpdateModelCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            entity_id=data.get("entity_id", data.get("id", 0)), title=data.get("title"), description=data.get("description"),
            status=data.get("status"))


@dataclass
class DeleteModelCommand(DeleteCommand):
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeleteModelCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            entity_id=data.get("entity_id", data.get("id", 0)))


@dataclass
class AddFieldCommand(Command):
    model_id: int = 0; name: str = ""; field_type: str = "string"; label: str = ""; required: bool = False
    unique: bool = False; default_value: Any = None; options: Dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AddFieldCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            model_id=data.get("model_id", 0), name=data.get("name", ""), field_type=data.get("field_type", "string"),
            label=data.get("label", ""), required=data.get("required", False), unique=data.get("unique", False),
            default_value=data.get("default_value"), options=data.get("options", {}))


@dataclass
class DeleteFieldCommand(Command):
    field_id: int = 0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeleteFieldCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            field_id=data.get("field_id", 0))


@dataclass
class GetModelCommand(QueryCommand):
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GetModelCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            entity_id=data.get("entity_id", data.get("id", 0)))


@dataclass
class ListModelsCommand(QueryCommand):
    project_id: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ListModelsCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            filters=data.get("filters", {}), pagination=data.get("pagination", {}), project_id=data.get("project_id"))


@dataclass
class GenerateCodeCommand(Command):
    model_id: int = 0; include_api: bool = True; include_service: bool = True; api_prefix: str = "/api"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GenerateCodeCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            model_id=data.get("model_id", 0), include_api=data.get("include_api", True),
            include_service=data.get("include_service", True), api_prefix=data.get("api_prefix", "/api"))


# === ARCHETYPE COMMANDS ===
@dataclass
class CreateArchetypeCommand(CreateCommand):
    name: str = ""; component_type: str = ""; description: str = ""; icon: str = ""
    default_config: Dict = field(default_factory=dict); api_schema: Dict = field(default_factory=dict)

    def to_payload(self) -> Dict[str, Any]:
        return {"name": self.name, "component_type": self.component_type, "description": self.description,
            "icon": self.icon, "default_config": self.default_config, "api_schema": self.api_schema}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CreateArchetypeCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            name=data.get("name", ""), component_type=data.get("component_type", ""), description=data.get("description", ""),
            icon=data.get("icon", ""), default_config=data.get("default_config", {}), api_schema=data.get("api_schema", {}))


@dataclass
class GetArchetypeCommand(QueryCommand):
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GetArchetypeCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            entity_id=data.get("entity_id", data.get("id", 0)))


@dataclass
class UpdateArchetypeCommand(UpdateCommand):
    name: Optional[str] = None; description: Optional[str] = None; default_config: Optional[Dict] = None

    def to_payload(self) -> Dict[str, Any]:
        payload = {}
        for f in ["name", "description", "default_config"]:
            v = getattr(self, f, None)
            if v is not None: payload[f] = v
        return payload

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UpdateArchetypeCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            entity_id=data.get("entity_id", data.get("id", 0)), name=data.get("name"), description=data.get("description"),
            default_config=data.get("default_config"))


@dataclass
class DeleteArchetypeCommand(DeleteCommand):
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeleteArchetypeCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            entity_id=data.get("entity_id", data.get("id", 0)))


@dataclass
class ListArchetypesCommand(QueryCommand):
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ListArchetypesCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            filters=data.get("filters", {}), pagination=data.get("pagination", {}))


# === COMPONENT COMMANDS ===
@dataclass
class CreateComponentCommand(CreateCommand):
    project_id: int = 0; archetype_id: int = 0; name: str = ""; description: str = ""
    config: Dict = field(default_factory=dict); block_id: Optional[int] = None

    def to_payload(self) -> Dict[str, Any]:
        return {"project_id": self.project_id, "archetype_id": self.archetype_id, "name": self.name,
            "description": self.description, "config": self.config, "block_id": self.block_id}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CreateComponentCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            project_id=data.get("project_id", 0), archetype_id=data.get("archetype_id", 0), name=data.get("name", ""),
            description=data.get("description", ""), config=data.get("config", {}), block_id=data.get("block_id"))


@dataclass
class GetComponentCommand(QueryCommand):
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GetComponentCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            entity_id=data.get("entity_id", data.get("id", 0)))


@dataclass
class UpdateComponentCommand(UpdateCommand):
    name: Optional[str] = None; config: Optional[Dict] = None
    position_x: Optional[int] = None; position_y: Optional[int] = None

    def to_payload(self) -> Dict[str, Any]:
        payload = {}
        for f in ["name", "config", "position_x", "position_y"]:
            v = getattr(self, f, None)
            if v is not None: payload[f] = v
        return payload

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UpdateComponentCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            entity_id=data.get("entity_id", data.get("id", 0)), name=data.get("name"), config=data.get("config"),
            position_x=data.get("position_x"), position_y=data.get("position_y"))


@dataclass
class DeleteComponentCommand(DeleteCommand):
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeleteComponentCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            entity_id=data.get("entity_id", data.get("id", 0)))


@dataclass
class ListComponentsCommand(QueryCommand):
    project_id: Optional[int] = None; block_id: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ListComponentsCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            filters=data.get("filters", {}), pagination=data.get("pagination", {}),
            project_id=data.get("project_id"), block_id=data.get("block_id"))


# === BLOCK COMMANDS ===
@dataclass
class CreateBlockCommand(CreateCommand):
    project_id: int = 0; name: str = ""; description: str = ""; component_ids: List = field(default_factory=list)

    def to_payload(self) -> Dict[str, Any]:
        return {"project_id": self.project_id, "name": self.name, "description": self.description,
            "component_ids": self.component_ids, "created_by": self.user_id}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CreateBlockCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            project_id=data.get("project_id", 0), name=data.get("name", ""), description=data.get("description", ""),
            component_ids=data.get("component_ids", []))


@dataclass
class GetBlockCommand(QueryCommand):
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GetBlockCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            entity_id=data.get("entity_id", data.get("id", 0)))


@dataclass
class UpdateBlockCommand(UpdateCommand):
    name: Optional[str] = None; description: Optional[str] = None
    component_ids: Optional[list] = None; status: Optional[str] = None

    def to_payload(self) -> Dict[str, Any]:
        payload = {}
        for f in ["name", "description", "component_ids", "status"]:
            v = getattr(self, f, None)
            if v is not None: payload[f] = v
        return payload

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UpdateBlockCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            entity_id=data.get("entity_id", data.get("id", 0)), name=data.get("name"), description=data.get("description"),
            component_ids=data.get("component_ids"), status=data.get("status"))


@dataclass
class DeleteBlockCommand(DeleteCommand):
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeleteBlockCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            entity_id=data.get("entity_id", data.get("id", 0)))


@dataclass
class ListBlocksCommand(QueryCommand):
    project_id: Optional[int] = None; include_templates: bool = False

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ListBlocksCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            filters=data.get("filters", {}), pagination=data.get("pagination", {}),
            project_id=data.get("project_id"), include_templates=data.get("include_templates", False))


@dataclass
class ConvertToTemplateCommand(UpdateCommand):
    name: str = ""; description: str = ""

    def to_payload(self) -> Dict[str, Any]:
        return {"is_template": True, "name": self.name or None, "description": self.description or None}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConvertToTemplateCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            entity_id=data.get("entity_id", data.get("id", 0)), name=data.get("name", ""), description=data.get("description", ""))
