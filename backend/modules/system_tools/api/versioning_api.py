from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from backend.modules.system_tools.services.versioning_service import ModelVersioningService

blp = Blueprint("versioning", __name__, description="Model versioning and snapshots")

versioning_service = ModelVersioningService()

@blp.route("/projects/<int:projectId>/models/<int:modelId>/versions")
class ModelVersionList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200)
    def get(self, projectId, modelId):
        """List versions for a model"""
        return versioning_service.get_versions(modelId)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(201)
    def post(self, projectId, modelId):
        """Create a new version snapshot"""
        return versioning_service.create_version(modelId, description="Manual snapshot")
