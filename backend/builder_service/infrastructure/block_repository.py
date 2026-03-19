"""
Builder Repository - SQLAlchemy implementation for Block, Component, Archetype.
"""
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class ArchetypeRepository:
    def __init__(self, db=None):
        self.db = db
    
    def _get_class(self):
        from backend.domain.builder.models import Archetype
        return Archetype
    
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        cls = self._get_class()
        item = cls(**data)
        self.db.session.add(item)
        self.db.session.commit()
        return self._to_dict(item)
    
    def find_by_id(self, archetype_id: int) -> Optional[Dict[str, Any]]:
        cls = self._get_class()
        item = cls.query.get(archetype_id)
        return self._to_dict(item) if item else None
    
    def find_all(self, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        cls = self._get_class()
        query = cls.query
        total = query.count()
        items = query.offset((page - 1) * per_page).limit(per_page).all()
        return {"items": [self._to_dict(i) for i in items], "total": total, "page": page, "per_page": per_page}
    
    def update(self, archetype_id: int, changes: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        cls = self._get_class()
        item = cls.query.get(archetype_id)
        if not item: return None
        for key, value in changes.items():
            if hasattr(item, key): setattr(item, key, value)
        self.db.session.commit()
        return self._to_dict(item)
    
    def delete(self, archetype_id: int) -> Optional[Dict[str, Any]]:
        cls = self._get_class()
        item = cls.query.get(archetype_id)
        if not item: return None
        data = self._to_dict(item)
        self.db.session.delete(item)
        self.db.session.commit()
        return data
    
    def _to_dict(self, item) -> Dict[str, Any]:
        return {"id": item.id, "name": item.name, "component_type": item.component_type,
            "description": item.description, "default_config": item.default_config or {},
            "api_schema": item.api_schema or {}, "icon": item.icon or "", "preview_url": item.preview_url or "",
            "is_system": item.is_system, "parent_id": item.parent_id,
            "created_at": item.created_at.isoformat() if item.created_at else None,
            "updated_at": item.updated_at.isoformat() if item.updated_at else None}


class ComponentRepository:
    def __init__(self, db=None):
        self.db = db
    
    def _get_class(self):
        from backend.domain.builder.models import Component
        return Component
    
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        cls = self._get_class()
        item = cls(**data)
        self.db.session.add(item)
        self.db.session.commit()
        return self._to_dict(item)
    
    def find_by_id(self, component_id: int) -> Optional[Dict[str, Any]]:
        cls = self._get_class()
        item = cls.query.get(component_id)
        return self._to_dict(item) if item else None
    
    def find_all(self, project_id: int = None, block_id: int = None, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        cls = self._get_class()
        query = cls.query
        if project_id: query = query.filter_by(project_id=project_id)
        if block_id: query = query.filter_by(block_id=block_id)
        total = query.count()
        items = query.offset((page - 1) * per_page).limit(per_page).all()
        return {"items": [self._to_dict(i) for i in items], "total": total, "page": page, "per_page": per_page}
    
    def update(self, component_id: int, changes: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        cls = self._get_class()
        item = cls.query.get(component_id)
        if not item: return None
        for key, value in changes.items():
            if hasattr(item, key): setattr(item, key, value)
        self.db.session.commit()
        return self._to_dict(item)
    
    def delete(self, component_id: int) -> Optional[Dict[str, Any]]:
        cls = self._get_class()
        item = cls.query.get(component_id)
        if not item: return None
        data = self._to_dict(item)
        self.db.session.delete(item)
        self.db.session.commit()
        return data
    
    def _to_dict(self, item) -> Dict[str, Any]:
        return {"id": item.id, "project_id": item.project_id, "archetype_id": item.archetype_id,
            "name": item.name or "", "description": item.description or "", "config": item.config or {},
            "position_x": item.position_x, "position_y": item.position_y, "width": item.width, "height": item.height,
            "order_index": item.order_index, "parent_id": item.parent_id, "block_id": item.block_id,
            "created_at": item.created_at.isoformat() if item.created_at else None,
            "updated_at": item.updated_at.isoformat() if item.updated_at else None}


class BlockRepository:
    def __init__(self, db=None):
        self.db = db
    
    def _get_class(self):
        from backend.domain.builder.models import Block
        return Block
    
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        cls = self._get_class()
        item = cls(**data)
        self.db.session.add(item)
        self.db.session.commit()
        return self._to_dict(item)
    
    def find_by_id(self, block_id: int) -> Optional[Dict[str, Any]]:
        cls = self._get_class()
        item = cls.query.get(block_id)
        return self._to_dict(item) if item else None
    
    def find_all(self, project_id: int = None, status: str = None, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        cls = self._get_class()
        query = cls.query
        if project_id: query = query.filter_by(project_id=project_id)
        if status: query = query.filter_by(status=status)
        total = query.count()
        items = query.offset((page - 1) * per_page).limit(per_page).all()
        return {"items": [self._to_dict(i) for i in items], "total": total, "page": page, "per_page": per_page}
    
    def update(self, block_id: int, changes: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        cls = self._get_class()
        item = cls.query.get(block_id)
        if not item: return None
        for key, value in changes.items():
            if hasattr(item, key): setattr(item, key, value)
        self.db.session.commit()
        return self._to_dict(item)
    
    def delete(self, block_id: int) -> Optional[Dict[str, Any]]:
        cls = self._get_class()
        item = cls.query.get(block_id)
        if not item: return None
        data = self._to_dict(item)
        self.db.session.delete(item)
        self.db.session.commit()
        return data
    
    def _to_dict(self, item) -> Dict[str, Any]:
        return {"id": item.id, "project_id": item.project_id, "created_by": item.created_by,
            "name": item.name, "description": item.description, "component_ids": item.component_ids or [],
            "relationships": item.relationships or {}, "api_endpoints": item.api_endpoints or [],
            "version": item.version, "test_suite_id": item.test_suite_id, "quality_score": item.quality_score,
            "is_certified": item.is_certified, "status": item.status,
            "created_at": item.created_at.isoformat() if item.created_at else None,
            "updated_at": item.updated_at.isoformat() if item.updated_at else None}
