from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required
from backend.modules.dynamic_api.service import get_dynamic_api_service

dynamic_api_service = get_dynamic_api_service()

def register_item_routes(blp):
    @blp.route("/data/<string:model_name>/<int:itemId>")
    class DynamicDataItem(MethodView):
        @blp.doc(security=[{"jwt": []}])
        @jwt_required()
        def get(self, projectId, model_name, itemId):
            """Retrieve a single record from a dynamic table."""
            return dynamic_api_service.get_record(
                projectId=projectId,
                model_name=model_name,
                itemId=itemId
            )

        @blp.doc(security=[{"jwt": []}])
        @jwt_required()
        def put(self, projectId, model_name, itemId):
            """Update a record in a dynamic table."""
            data = request.get_json()
            return dynamic_api_service.update_record(
                projectId=projectId,
                model_name=model_name,
                itemId=itemId,
                data=data
            )

        @blp.doc(security=[{"jwt": []}])
        @jwt_required()
        def delete(self, projectId, model_name, itemId):
            """Delete a record from a dynamic table."""
            dynamic_api_service.delete_record(
                projectId=projectId,
                model_name=model_name,
                itemId=itemId
            )
            return "", 204

    @blp.route("/data/<string:model_name>/<int:itemId>/clone")
    class DynamicDataClone(MethodView):
        @blp.doc(security=[{"jwt": []}])
        @jwt_required()
        def post(self, projectId, model_name, itemId):
            """Clone an existing record."""
            result, status = dynamic_api_service.clone_record(
                projectId=projectId,
                model_name=model_name,
                itemId=itemId
            )
            return result, status
