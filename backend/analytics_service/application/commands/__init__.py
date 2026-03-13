"""
Analytics Commands - Command classes for Analytics Service.
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional

from backend.shared.commands import Command, CreateCommand, UpdateCommand, DeleteCommand, QueryCommand


@dataclass
class CreateChartCommand(CreateCommand):
    project_id: int = 0
    name: str = ""
    chart_type: str = ""
    config: Dict[str, Any] = None
    model_id: Optional[int] = None
    
    def __post_init__(self):
        if self.config is None:
            self.config = {}
    
    def to_payload(self) -> Dict[str, Any]:
        return {"project_id": self.project_id, "name": self.name, "chart_type": self.chart_type,
            "config": self.config, "model_id": self.model_id}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CreateChartCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            project_id=data.get("project_id", 0), name=data.get("name", ""), chart_type=data.get("chart_type", ""),
            config=data.get("config", {}), model_id=data.get("model_id"))


@dataclass
class UpdateChartCommand(UpdateCommand):
    name: Optional[str] = None
    chart_type: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    
    def to_payload(self) -> Dict[str, Any]:
        payload = {}
        for f in ["name", "chart_type", "config"]:
            v = getattr(self, f, None)
            if v is not None: payload[f] = v
        return payload
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UpdateChartCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            entity_id=data.get("entity_id", data.get("id", 0)), name=data.get("name"), chart_type=data.get("chart_type"),
            config=data.get("config"))


@dataclass
class DeleteChartCommand(DeleteCommand):
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeleteChartCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            entity_id=data.get("entity_id", data.get("id", 0)))


@dataclass
class GetChartCommand(QueryCommand):
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GetChartCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            entity_id=data.get("entity_id", data.get("id", 0)))


@dataclass
class ListChartsCommand(QueryCommand):
    project_id: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ListChartsCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            filters=data.get("filters", {}), pagination=data.get("pagination", {}),
            project_id=data.get("project_id"))


@dataclass
class CreateChartLibraryCommand(CreateCommand):
    library_name: str = ""
    display_name: str = ""
    description: str = ""
    is_default: bool = False
    is_active: bool = True
    config: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.config is None:
            self.config = {}
    
    def to_payload(self) -> Dict[str, Any]:
        return {"library_name": self.library_name, "display_name": self.display_name, "description": self.description,
            "is_default": self.is_default, "is_active": self.is_active, "config": self.config}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CreateChartLibraryCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            library_name=data.get("library_name", ""), display_name=data.get("display_name", ""),
            description=data.get("description", ""), is_default=data.get("is_default", False),
            is_active=data.get("is_active", True), config=data.get("config", {}))


@dataclass
class GetDefaultLibraryCommand(QueryCommand):
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GetDefaultLibraryCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}))


@dataclass
class GetChartLibraryCommand(QueryCommand):
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GetChartLibraryCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            entity_id=data.get("entity_id", data.get("id", 0)))


@dataclass
class ListChartLibrariesCommand(QueryCommand):
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ListChartLibrariesCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            filters=data.get("filters", {}), pagination=data.get("pagination", {}))


@dataclass
class UpdateChartLibraryCommand(UpdateCommand):
    library_name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None
    
    def to_payload(self) -> Dict[str, Any]:
        payload = {}
        for f in ["library_name", "display_name", "description", "is_default", "is_active", "config"]:
            v = getattr(self, f, None)
            if v is not None: payload[f] = v
        return payload
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UpdateChartLibraryCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            entity_id=data.get("entity_id", data.get("id", 0)), library_name=data.get("library_name"),
            display_name=data.get("display_name"), description=data.get("description"),
            is_default=data.get("is_default"), is_active=data.get("is_active"), config=data.get("config"))


@dataclass
class DeleteChartLibraryCommand(DeleteCommand):
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeleteChartLibraryCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            entity_id=data.get("entity_id", data.get("id", 0)))
