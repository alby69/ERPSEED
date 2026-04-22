from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required
from backend.core.schemas.schemas import SysModelSchema
from backend.modules.dynamic_api.service import get_dynamic_api_service

dynamic_api_service = get_dynamic_api_service()

def register_meta_routes(blp):
    @blp.route("/data/<string:model_name>/meta")
    class DynamicModelMeta(MethodView):
        @blp.doc(security=[{"jwt": []}])
        @jwt_required()
        @blp.response(200, SysModelSchema)
        def get(self, projectId, model_name):
            """Retrieve metadata of a dynamic model for the frontend."""
            return dynamic_api_service.get_model_metadata(
                projectId=projectId,
                model_name=model_name
            )
