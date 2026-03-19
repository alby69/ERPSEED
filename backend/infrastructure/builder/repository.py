"""
Builder Repository - SQLAlchemy implementation for Builder entities.
"""
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class ModelRepository:
    def __init__(self, db=None): self.db = db
    
    def _get_model_class(self):
        from backend.models import SysModel
        return SysModel
    
    def _get_field_class(self):
        from backend.models import SysField
        return SysField
    
    def save(self, data: Dict[str, Any]) -> Dict[str, Any]:
        SysModel = self._get_model_class()
        model = SysModel()
        for key, value in data.items():
            if hasattr(model, key): setattr(model, key, value)
        self.db.session.add(model)
        self.db.session.commit()
        return self._to_dict(model)
    
    def find_by_id(self, model_id: int) -> Optional[Dict[str, Any]]:
        SysModel = self._get_model_class()
        model = SysModel.query.get(model_id)
        return self._to_dict(model) if model else None
    
    def find_all(self, project_id: int = None) -> Dict[str, Any]:
        SysModel = self._get_model_class()
        query = SysModel.query
        if project_id: query = query.filter_by(project_id=project_id)
        items = query.all()
        return {"items": [self._to_dict(m) for m in items], "total": len(items)}
    
    def update(self, model_id: int, changes: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        SysModel = self._get_model_class()
        model = SysModel.query.get(model_id)
        if not model: return None
        for key, value in changes.items():
            if hasattr(model, key): setattr(model, key, value)
        self.db.session.commit()
        return self._to_dict(model)
    
    def delete(self, model_id: int) -> Dict[str, Any]:
        SysModel = self._get_model_class()
        model = SysModel.query.get(model_id)
        if not model: return {"success": False, "error": "Not found"}
        model_data = self._to_dict(model)
        self.db.session.delete(model)
        self.db.session.commit()
        return {"success": True, "model": model_data}
    
    def add_field(self, model_id: int, field_data: Dict[str, Any]) -> Dict[str, Any]:
        SysField = self._get_field_class()
        field = SysField()
        field.model_id = model_id
        field.name = field_data.get("name", "")
        field.type = field_data.get("type", "string")
        field.label = field_data.get("label", field_data.get("name", ""))
        field.required = field_data.get("required", False)
        field.unique = field_data.get("unique", False)
        field.default_value = field_data.get("default_value")
        field.options = field_data.get("options", {})
        self.db.session.add(field)
        self.db.session.commit()
        return {"id": field.id, "name": field.name, "type": field.type}
    
    def _to_dict(self, model) -> Dict[str, Any]:
        return {"id": model.id, "project_id": model.project_id, "name": model.name,
            "title": getattr(model, 'title', model.name), "description": getattr(model, 'description', ''),
            "status": getattr(model, 'status', 'draft'),
            "fields": [{"id": f.id, "name": f.name, "type": f.type, "label": getattr(f, 'label', f.name),
                "required": getattr(f, 'required', False)} for f in getattr(model, 'fields', [])]}


class ArchetypeRepository:
    def __init__(self, db=None): self.db = db
    
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        from backend.models import SysArchetype
        archetype = SysArchetype(**data)
        self.db.session.add(archetype)
        self.db.session.commit()
        return self._to_dict(archetype)
    
    def find_all(self) -> Dict[str, Any]:
        from backend.models import SysArchetype
        items = SysArchetype.query.all()
        return {"items": [self._to_dict(a) for a in items], "total": len(items)}
    
    def _to_dict(self, a) -> Dict[str, Any]:
        return {"id": a.id, "name": a.name, "component_type": getattr(a, 'component_type', ''),
            "description": getattr(a, 'description', ''), "icon": getattr(a, 'icon', '')}


class ComponentRepository:
    def __init__(self, db=None): self.db = db
    
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        from backend.models import SysComponent
        comp = SysComponent(**data)
        self.db.session.add(comp)
        self.db.session.commit()
        return {"id": comp.id, "name": comp.name, "archetype_id": comp.archetype_id}
    
    def find_all(self, project_id: int = None, block_id: int = None) -> Dict[str, Any]:
        from backend.models import SysComponent
        query = SysComponent.query
        if project_id: query = query.filter_by(project_id=project_id)
        if block_id: query = query.filter_by(block_id=block_id)
        items = query.all()
        return {"items": [{"id": c.id, "name": c.name} for c in items], "total": len(items)}


class BlockRepository:
    def __init__(self, db=None): self.db = db
    
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        from backend.models import SysBlock
        block = SysBlock(**data)
        self.db.session.add(block)
        self.db.session.commit()
        return self._to_dict(block)
    
    def find_by_id(self, block_id: int) -> Optional[Dict[str, Any]]:
        from backend.models import SysBlock
        block = SysBlock.query.get(block_id)
        return self._to_dict(block) if block else None
    
    def find_all(self, project_id: int = None, include_templates: bool = False) -> Dict[str, Any]:
        from backend.models import SysBlock
        query = SysBlock.query
        if project_id: query = query.filter_by(project_id=project_id)
        if not include_templates: query = query.filter_by(is_template=False)
        items = query.all()
        return {"items": [self._to_dict(b) for b in items], "total": len(items)}
    
    def update(self, block_id: int, changes: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        from backend.models import SysBlock
        block = SysBlock.query.get(block_id)
        if not block: return None
        for key, value in changes.items():
            if hasattr(block, key): setattr(block, key, value)
        self.db.session.commit()
        return self._to_dict(block)
    
    def _to_dict(self, b) -> Dict[str, Any]:
        return {"id": b.id, "project_id": b.project_id, "name": b.name, "description": getattr(b, 'description', ''),
            "version": getattr(b, 'version', '1.0.0'), "status": getattr(b, 'status', 'draft'),
            "is_template": getattr(b, 'is_template', False)}
