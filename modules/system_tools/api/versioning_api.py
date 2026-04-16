from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from modules.system_tools.services.versioning_service import ModelVersioningService

blp = Blueprint("versioning", __name__, description="Model versioning and snapshots")

versioning_service = ModelVersioningService()

@blp.route("/projects/<int:project_id>/models/<int:model_id>/versions")
class ModelVersionList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200)
    def get(self, project_id, model_id):
        """List versions for a model"""
        return versioning_service.get_versions(model_id)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(201)
    def post(self, project_id, model_id):
        """Create a new version snapshot"""
        return versioning_service.create_version(model_id, description="Manual snapshot")
