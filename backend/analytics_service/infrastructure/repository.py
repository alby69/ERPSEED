"""
Analytics Repository - SQLAlchemy implementation for Charts and Dashboards.
"""
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class ChartRepository:
    def __init__(self, db=None):
        self.db = db
    
    def _get_chart_class(self):
        from backend.models import SysChart
        return SysChart
    
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        SysChart = self._get_chart_class()
        chart = SysChart(**data)
        self.db.session.add(chart)
        self.db.session.commit()
        return self._to_dict(chart)
    
    def find_by_id(self, chart_id: int) -> Optional[Dict[str, Any]]:
        SysChart = self._get_chart_class()
        chart = SysChart.query.get(chart_id)
        return self._to_dict(chart) if chart else None
    
    def find_all(self, project_id: int = None, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        SysChart = self._get_chart_class()
        query = SysChart.query
        if project_id: query = query.filter_by(project_id=project_id)
        total = query.count()
        items = query.offset((page - 1) * per_page).limit(per_page).all()
        return {"items": [self._to_dict(c) for c in items], "total": total, "page": page, "per_page": per_page}
    
    def update(self, chart_id: int, changes: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        SysChart = self._get_chart_class()
        chart = SysChart.query.get(chart_id)
        if not chart: return None
        for key, value in changes.items():
            if hasattr(chart, key): setattr(chart, key, value)
        self.db.session.commit()
        return self._to_dict(chart)
    
    def delete(self, chart_id: int) -> Optional[Dict[str, Any]]:
        SysChart = self._get_chart_class()
        chart = SysChart.query.get(chart_id)
        if not chart: return None
        chart_data = self._to_dict(chart)
        self.db.session.delete(chart)
        self.db.session.commit()
        return chart_data
    
    def _to_dict(self, chart) -> Dict[str, Any]:
        return {"id": chart.id, "project_id": chart.project_id, "name": chart.name, "chart_type": chart.chart_type,
            "config": chart.config, "model_id": chart.model_id, "created_at": chart.created_at.isoformat() if chart.created_at else None,
            "updated_at": chart.updated_at.isoformat() if chart.updated_at else None}


class ChartLibraryRepository:
    def __init__(self, db=None):
        self.db = db
    
    def _get_class(self):
        from backend.models import ChartLibraryConfig
        return ChartLibraryConfig
    
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        cls = self._get_class()
        existing = cls.query.filter_by(library_name=data.get("library_name")).first()
        if existing:
            for key, value in data.items():
                if hasattr(existing, key): setattr(existing, key, value)
            self.db.session.commit()
            return self._to_dict(existing)
        item = cls(**data)
        self.db.session.add(item)
        self.db.session.commit()
        return self._to_dict(item)
    
    def find_by_id(self, library_id: int) -> Optional[Dict[str, Any]]:
        cls = self._get_class()
        item = cls.query.get(library_id)
        return self._to_dict(item) if item else None
    
    def find_all(self, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        cls = self._get_class()
        query = cls.query
        total = query.count()
        items = query.offset((page - 1) * per_page).limit(per_page).all()
        return {"items": [self._to_dict(i) for i in items], "total": total, "page": page, "per_page": per_page}
    
    def find_default(self) -> Optional[Dict[str, Any]]:
        cls = self._get_class()
        item = cls.query.filter_by(is_default=True).first()
        return self._to_dict(item) if item else None
    
    def update(self, library_id: int, changes: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        cls = self._get_class()
        item = cls.query.get(library_id)
        if not item: return None
        for key, value in changes.items():
            if hasattr(item, key): setattr(item, key, value)
        self.db.session.commit()
        return self._to_dict(item)
    
    def delete(self, library_id: int) -> Optional[Dict[str, Any]]:
        cls = self._get_class()
        item = cls.query.get(library_id)
        if not item: return None
        data = self._to_dict(item)
        self.db.session.delete(item)
        self.db.session.commit()
        return data
    
    def _to_dict(self, item) -> Dict[str, Any]:
        return {"id": item.id, "library_name": item.library_name, "display_name": getattr(item, 'display_name', item.library_name),
            "description": getattr(item, 'description', ''), "is_default": item.is_default, "is_active": getattr(item, 'is_active', True),
            "config": getattr(item, 'config', {}), "created_at": item.created_at.isoformat() if hasattr(item, 'created_at') and item.created_at else None,
            "updated_at": item.updated_at.isoformat() if hasattr(item, 'updated_at') and item.updated_at else None}
