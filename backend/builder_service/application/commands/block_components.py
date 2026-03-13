"""
Builder Commands - Commands for Block, Component, Archetype.
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional

from backend.shared.commands import Command, CreateCommand, UpdateCommand, DeleteCommand, QueryCommand


# === ARCHETYPE COMMANDS ===
@dataclass
class CreateArchetypeCommand(CreateCommand):
    name: str = ""
    component_type: str = ""
    description: str = ""
    default_config: Dict[str, Any] = None
    api_schema: Dict[str, Any] = None
    icon: str = ""
    
    def __post_init__(self):
        if self.default_config is None: self.default_config = {}
        if self.api_schema is None: self.api_schema = {}
    
    def to_payload(self) -> Dict[str, Any]:
        return {"name": self.name, "component_type": self.component_type, "description": self.description,
            "default_config": self.default_config, "api_schema": self.api_schema, "icon": self.icon}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CreateArchetypeCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            name=data.get("name", ""), component_type=data.get("component_type", ""), description=data.get("description", ""),
            default_config=data.get("default_config", {}), api_schema=data.get("api_schema", {}), icon=data.get("icon", ""))


@dataclass
class UpdateArchetypeCommand(UpdateCommand):
    name: Optional[str] = None
    description: Optional[str] = None
    default_config: Optional[Dict] = None
    
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
class GetArchetypeCommand(QueryCommand):
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GetArchetypeCommand":
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
    project_id: int = 0
    archetype_id: int = 0
    name: str = ""
    description: str = ""
    config: Dict[str, Any] = None
    block_id: Optional[int] = None
    
    def __post_init__(self):
        if self.config is None: self.config = {}
    
    def to_payload(self) -> Dict[str, Any]:
        return {"project_id": self.project_id, "archetype_id": self.archetype_id, "name": self.name,
            "description": self.description, "config": self.config, "block_id": self.block_id}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CreateComponentCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            project_id=data.get("project_id", 0), archetype_id=data.get("archetype_id", 0), name=data.get("name", ""),
            description=data.get("description", ""), config=data.get("config", {}), block_id=data.get("block_id"))


@dataclass
class UpdateComponentCommand(UpdateCommand):
    name: Optional[str] = None
    config: Optional[Dict] = None
    position_x: Optional[int] = None
    position_y: Optional[int] = None
    
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
class GetComponentCommand(QueryCommand):
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GetComponentCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            entity_id=data.get("entity_id", data.get("id", 0)))


@dataclass
class ListComponentsCommand(QueryCommand):
    project_id: Optional[int] = None
    block_id: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ListComponentsCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            filters=data.get("filters", {}), pagination=data.get("pagination", {}),
            project_id=data.get("project_id"), block_id=data.get("block_id"))


# === BLOCK COMMANDS ===
@dataclass
class CreateBlockCommand(CreateCommand):
    project_id: int = 0
    name: str = ""
    description: str = ""
    component_ids: list = None
    
    def __post_init__(self):
        if self.component_ids is None: self.component_ids = []
    
    def to_payload(self) -> Dict[str, Any]:
        return {"project_id": self.project_id, "name": self.name, "description": self.description,
            "component_ids": self.component_ids, "created_by": self.user_id}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CreateBlockCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            project_id=data.get("project_id", 0), name=data.get("name", ""), description=data.get("description", ""),
            component_ids=data.get("component_ids", []))


@dataclass
class UpdateBlockCommand(UpdateCommand):
    name: Optional[str] = None
    description: Optional[str] = None
    component_ids: Optional[list] = None
    status: Optional[str] = None
    
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
class GetBlockCommand(QueryCommand):
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GetBlockCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            entity_id=data.get("entity_id", data.get("id", 0)))


@dataclass
class ListBlocksCommand(QueryCommand):
    project_id: Optional[int] = None
    status: Optional[str] = None
    include_templates: bool = False
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ListBlocksCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            filters=data.get("filters", {}), pagination=data.get("pagination", {}),
            project_id=data.get("project_id"), status=data.get("status"),
            include_templates=data.get("include_templates", False))


# === BLOCK TEMPLATE COMMANDS ===
@dataclass
class CreateBlockFromTemplateCommand(CreateCommand):
    """Create a new Block instance from a Template."""
    project_id: int = 0
    template_id: int = 0
    name: str = ""
    description: str = ""
    params_override: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.params_override is None: self.params_override = {}
    
    def to_payload(self) -> Dict[str, Any]:
        return {"project_id": self.project_id, "template_id": self.template_id, "name": self.name,
            "description": self.description, "params_override": self.params_override, "created_by": self.user_id}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CreateBlockFromTemplateCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            project_id=data.get("project_id", 0), template_id=data.get("template_id", 0),
            name=data.get("name", ""), description=data.get("description", ""),
            params_override=data.get("params_override", {}))


@dataclass
class ConvertToTemplateCommand(UpdateCommand):
    """Convert a Block to a Template."""
    name: str = ""
    description: str = ""
    
    def to_payload(self) -> Dict[str, Any]:
        return {"is_template": True, "name": self.name or None, "description": self.description or None}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConvertToTemplateCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            entity_id=data.get("entity_id", data.get("id", 0)), name=data.get("name", ""),
            description=data.get("description", ""))


@dataclass
class UpdateTemplateParamsCommand(UpdateCommand):
    """Update params for a Block instance."""
    params_override: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.params_override is None: self.params_override = {}
    
    def to_payload(self) -> Dict[str, Any]:
        return {"params_override": self.params_override}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UpdateTemplateParamsCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            entity_id=data.get("entity_id", data.get("id", 0)), params_override=data.get("params_override", {}))


@dataclass
class ListTemplatesCommand(QueryCommand):
    """List available Block Templates."""
    project_id: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ListTemplatesCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            filters=data.get("filters", {}), pagination=data.get("pagination", {}),
            project_id=data.get("project_id"))
