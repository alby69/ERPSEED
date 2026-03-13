"""
Domain Entities for Builder Service - Block, Component, Archetype.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List


@dataclass
class Archetype:
    """Component template - base for all components."""
    id: Optional[int] = None
    name: str = ""
    component_type: str = ""
    description: str = ""
    default_config: Dict[str, Any] = field(default_factory=dict)
    api_schema: Dict[str, Any] = field(default_factory=dict)
    icon: str = ""
    preview_url: str = ""
    is_system: bool = False
    parent_id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "name": self.name, "component_type": self.component_type,
            "description": self.description, "default_config": self.default_config, "api_schema": self.api_schema,
            "icon": self.icon, "preview_url": self.preview_url, "is_system": self.is_system,
            "parent_id": self.parent_id, "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Archetype":
        return cls(id=data.get("id"), name=data.get("name", ""), component_type=data.get("component_type", ""),
            description=data.get("description", ""), default_config=data.get("default_config", {}),
            api_schema=data.get("api_schema", {}), icon=data.get("icon", ""), preview_url=data.get("preview_url", ""),
            is_system=data.get("is_system", False), parent_id=data.get("parent_id"))


@dataclass
class Component:
    """Component instance in a project."""
    id: Optional[int] = None
    project_id: int = 0
    archetype_id: int = 0
    name: str = ""
    description: str = ""
    config: Dict[str, Any] = field(default_factory=dict)
    position_x: int = 0
    position_y: int = 0
    width: int = 6
    height: int = 4
    order_index: int = 0
    parent_id: Optional[int] = None
    block_id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "project_id": self.project_id, "archetype_id": self.archetype_id,
            "name": self.name, "description": self.description, "config": self.config,
            "position_x": self.position_x, "position_y": self.position_y, "width": self.width, "height": self.height,
            "order_index": self.order_index, "parent_id": self.parent_id, "block_id": self.block_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Component":
        return cls(id=data.get("id"), project_id=data.get("project_id", 0), archetype_id=data.get("archetype_id", 0),
            name=data.get("name", ""), description=data.get("description", ""), config=data.get("config", {}),
            position_x=data.get("position_x", 0), position_y=data.get("position_y", 0),
            width=data.get("width", 6), height=data.get("height", 4), order_index=data.get("order_index", 0),
            parent_id=data.get("parent_id"), block_id=data.get("block_id"))


@dataclass
class Block:
    """Aggregated Block - collection of components.
    
    Can be a Template (is_template=True) for cross-project reuse,
    or an Instance (template_id set) of a Template.
    """
    id: Optional[int] = None
    project_id: int = 0
    created_by: Optional[int] = None
    name: str = ""
    description: str = ""
    component_ids: List[int] = field(default_factory=list)
    relationships: Dict[str, Any] = field(default_factory=dict)
    api_endpoints: List[Dict[str, Any]] = field(default_factory=list)
    version: str = "1.0.0"
    test_suite_id: Optional[int] = None
    quality_score: int = 0
    is_certified: bool = False
    certification_date: Optional[datetime] = None
    status: str = "draft"
    
    # Block Template fields (Opzione 1)
    is_template: bool = False
    template_id: Optional[int] = None
    params_override: Dict[str, Any] = field(default_factory=dict)
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "project_id": self.project_id, "created_by": self.created_by,
            "name": self.name, "description": self.description, "component_ids": self.component_ids,
            "relationships": self.relationships, "api_endpoints": self.api_endpoints, "version": self.version,
            "test_suite_id": self.test_suite_id, "quality_score": self.quality_score,
            "is_certified": self.is_certified, "certification_date": self.certification_date.isoformat() if self.certification_date else None,
            "status": self.status, "is_template": self.is_template, "template_id": self.template_id,
            "params_override": self.params_override, "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Block":
        return cls(id=data.get("id"), project_id=data.get("project_id", 0), created_by=data.get("created_by"),
            name=data.get("name", ""), description=data.get("description", ""),
            component_ids=data.get("component_ids", []), relationships=data.get("relationships", {}),
            api_endpoints=data.get("api_endpoints", []), version=data.get("version", "1.0.0"),
            test_suite_id=data.get("test_suite_id"), quality_score=data.get("quality_score", 0),
            is_certified=data.get("is_certified", False), status=data.get("status", "draft"),
            is_template=data.get("is_template", False), template_id=data.get("template_id"),
            params_override=data.get("params_override", {}))
