"""
Domain Models for Analytics.

Pure Python dataclasses for charts and dashboards.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List


@dataclass
class ChartLibrary:
    id: Optional[int] = None; library_name: str = ""; display_name: str = ""; description: str = ""
    is_default: bool = False; is_active: bool = True; config: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow); updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "library_name": self.library_name, "display_name": self.display_name,
            "description": self.description, "is_default": self.is_default, "is_active": self.is_active,
            "config": self.config, "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChartLibrary":
        return cls(id=data.get("id"), library_name=data.get("library_name", ""), display_name=data.get("display_name", ""),
            description=data.get("description", ""), is_default=data.get("is_default", False),
            is_active=data.get("is_active", True), config=data.get("config", {}))


@dataclass
class Chart:
    id: Optional[int] = None; project_id: int = 0; name: str = ""; chart_type: str = ""
    config: Dict[str, Any] = field(default_factory=dict); model_id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow); updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "project_id": self.project_id, "name": self.name, "chart_type": self.chart_type,
            "config": self.config, "model_id": self.model_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Chart":
        return cls(id=data.get("id"), project_id=data.get("project_id", 0), name=data.get("name", ""),
            chart_type=data.get("chart_type", ""), config=data.get("config", {}), model_id=data.get("model_id"))


@dataclass
class Dashboard:
    id: Optional[int] = None; project_id: int = 0; name: str = ""
    layout: List[Dict[str, Any]] = field(default_factory=list); is_default: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow); updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "project_id": self.project_id, "name": self.name, "layout": self.layout,
            "is_default": self.is_default, "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Dashboard":
        return cls(id=data.get("id"), project_id=data.get("project_id", 0), name=data.get("name", ""),
            layout=data.get("layout", []), is_default=data.get("is_default", False))
