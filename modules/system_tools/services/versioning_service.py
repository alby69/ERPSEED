"""
Model Versioning Service
Handles snapshots and version history for SysModel definitions.
"""
import json
from extensions import db
from models import SysModel, SysField, SysModelVersion

class ModelVersioningService:
    @staticmethod
    def create_snapshot(model_id, description=None, user_id=None):
        """Create a version snapshot of a SysModel and its fields."""
        model = SysModel.query.get_or_404(model_id)

        # Get fields
        fields = SysField.query.filter_by(model_id=model_id).all()
        fields_data = []
        for f in fields:
            fields_data.append({
                "technical_name": f.technical_name,
                "title": f.title,
                "type": f.type,
                "required": f.required,
                "ui_widget": f.ui_widget,
                "order": f.order
            })

        snapshot = {
            "model": {
                "name": model.name,
                "technical_name": model.technical_name,
                "title": model.title,
                "table_name": model.table_name,
            },
            "fields": fields_data
        }

        # Determine next version number
        last_version = SysModelVersion.query.filter_by(model_id=model_id)\
                                           .order_by(SysModelVersion.version_number.desc())\
                                           .first()
        next_version = (last_version.version_number + 1) if last_version else 1

        version = SysModelVersion(
            model_id=model_id,
            version_number=next_version,
            description=description,
            data=json.dumps(snapshot),
            created_by=user_id
        )

        db.session.add(version)
        db.session.commit()
        return version

    @staticmethod
    def get_history(model_id):
        """Get version history for a model."""
        return SysModelVersion.query.filter_by(model_id=model_id)\
                                   .order_by(SysModelVersion.version_number.desc())\
                                   .all()
