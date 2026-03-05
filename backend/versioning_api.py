"""
Versioning API
REST API for managing model versions.
"""
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields
from backend.models import SysModel, SysModelVersion
from backend.services.versioning_service import ModelVersioningService

blp = Blueprint(
    "versioning",
    __name__,
    url_prefix="/api/v1/versioning",
    description="Model Versioning API"
)

class VersionCreateSchema(Schema):
    description = fields.String(required=False)

class VersionSchema(Schema):
    id = fields.Int(dump_only=True)
    version_number = fields.Int(dump_only=True)
    description = fields.String()
    created_at = fields.DateTime(dump_only=True)
    data = fields.String(dump_only=True)

@blp.route("/models/<int:model_id>/versions")
class ModelVersions(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, VersionSchema(many=True))
    def get(self, model_id):
        """Get version history for a model."""
        return ModelVersioningService.get_history(model_id)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(VersionCreateSchema)
    @blp.response(201, VersionSchema)
    def post(self, version_data, model_id):
        """Create a new version snapshot for a model."""
        user_id = get_jwt_identity()
        try:
            version = ModelVersioningService.create_snapshot(
                model_id,
                description=version_data.get("description"),
                user_id=user_id
            )
            return version
        except Exception as e:
            abort(500, message=str(e))
