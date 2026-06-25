"""
SQLAlchemy Repository Implementation for Builder Service.
"""

import logging
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)


class SQLAlchemyModelRepository:
    """SQLAlchemy implementation of ModelRepository."""

    def __init__(self, db=None):
        self.db = db

    def _get_model_class(self):
        """Get the SysModel class lazily."""
        from backend.models import SysModel

        return SysModel

    def _get_field_class(self):
        """Get the SysField class lazily."""
        from backend.models import SysField

        return SysField

    def find_by_id(self, model_id: int) -> Optional[Dict[str, Any]]:
        """Find a model by ID."""
        SysModel = self._get_model_class()
        model = SysModel.query.get(model_id)

        if not model:
            return None

        return self._model_to_dict(model)

    def find_by_technical_name(
        self, technical_name: str, project_id: int
    ) -> Optional[Dict[str, Any]]:
        """Find a model by technical name."""
        SysModel = self._get_model_class()
        model = SysModel.query.filter_by(
            technical_name=technical_name,
            project_id=project_id,
        ).first()

        if not model:
            return None

        return self._model_to_dict(model)

    def find_by_project(
        self,
        project_id: int,
        status: str = None,
        search: str = None,
    ) -> List[Dict[str, Any]]:
        """Find all models in a project."""
        SysModel = self._get_model_class()

        query = SysModel.query.filter_by(project_id=project_id)

        if status:
            query = query.filter_by(status=status)

        if search:
            query = query.filter(
                (SysModel.name.ilike(f"%{search}%"))
                | (SysModel.title.ilike(f"%{search}%"))
            )

        models = query.order_by(SysModel.name).all()

        return [self._model_to_dict(m) for m in models]

    def save(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create or update a model."""
        SysModel = self._get_model_class()

        model_id = model_data.get("id")

        if model_id:
            model = SysModel.query.get(model_id)
            if not model:
                raise ValueError(f"Model not found: {model_id}")
        else:
            model = SysModel()
            self.db.session.add(model)

        for key, value in model_data.items():
            if hasattr(model, key):
                setattr(model, key, value)

        self.db.session.commit()

        return self._model_to_dict(model)

    def update(self, model_id: int, changes: Dict[str, Any]) -> Dict[str, Any]:
        """Update a model."""
        return self.save({"id": model_id, **changes})

    def delete(self, model_id: int) -> Dict[str, Any]:
        """Delete a model."""
        SysModel = self._get_model_class()

        model = SysModel.query.get(model_id)

        if not model:
            return {"success": False, "error": "Model not found"}

        model_name = model.name
        self.db.session.delete(model)
        self.db.session.commit()

        return {"success": True, "model_name": model_name}

    def add_field(self, model_id: int, field_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a field to a model."""
        SysField = self._get_field_class()
        SysModel = self._get_model_class()

        model = SysModel.query.get(model_id)
        if not model:
            raise ValueError(f"Model not found: {model_id}")

        field = SysField()
        field.model_id = model_id

        for key, value in field_data.items():
            if hasattr(field, key):
                setattr(field, key, value)

        self.db.session.add(field)
        self.db.session.commit()

        return self._field_to_dict(field)

    def update_field(self, field_id: int, field_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a field."""
        SysField = self._get_field_class()

        field = SysField.query.get(field_id)

        if not field:
            return {"success": False, "error": "Field not found"}

        for key, value in field_data.items():
            if hasattr(field, key):
                setattr(field, key, value)

        self.db.session.commit()

        return self._field_to_dict(field)

    def delete_field(self, field_id: int) -> Dict[str, Any]:
        """Delete a field."""
        SysField = self._get_field_class()

        field = SysField.query.get(field_id)

        if not field:
            return {"success": False, "error": "Field not found"}

        field_name = field.name
        self.db.session.delete(field)
        self.db.session.commit()

        return {"success": True, "field_name": field_name}

    def get_fields(self, model_id: int) -> List[Dict[str, Any]]:
        """Get all fields for a model."""
        SysField = self._get_field_class()

        fields = (
            SysField.query.filter_by(model_id=model_id)
            .order_by(SysField.position, SysField.id)
            .all()
        )

        return [self._field_to_dict(f) for f in fields]

    def find_field_by_id(self, field_id: int) -> Optional[Dict[str, Any]]:
        """Find a field by ID."""
        SysField = self._get_field_class()

        field = SysField.query.get(field_id)

        if not field:
            return None

        return self._field_to_dict(field)

    def _model_to_dict(self, model) -> Dict[str, Any]:
        """Convert model to dictionary."""
        result = {
            "id": model.id,
            "project_id": model.project_id,
            "name": model.name,
            "technical_name": model.technical_name,
            "title": model.title,
            "description": model.description,
            "table_name": model.table_name,
            "status": model.status,
            "permissions": model.permissions,
            "created_at": model.created_at.isoformat() if model.created_at else None,
            "updated_at": model.updated_at.isoformat() if model.updated_at else None,
        }

        if hasattr(model, "fields"):
            result["fields"] = [self._field_to_dict(f) for f in model.fields]

        return result

    def _field_to_dict(self, field) -> Dict[str, Any]:
        """Convert field to dictionary."""
        return {
            "id": field.id,
            "model_id": field.model_id,
            "name": field.name,
            "technical_name": field.technical_name,
            "type": field.type,
            "label": field.label,
            "description": field.description,
            "required": field.required,
            "unique": field.is_unique,
            "default_value": field.default_value,
            "options": field.options,
            "position": getattr(field, "position", 0),
        }
