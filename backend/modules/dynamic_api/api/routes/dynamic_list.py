from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from backend.modules.dynamic_api.service import get_dynamic_api_service
from backend.core.schemas.dynamic_schemas import AnyJsonSchema, BulkDeleteSchema

dynamic_api_service = get_dynamic_api_service()

def register_list_routes(blp):
    @blp.route("/data/<string:model_name>")
    class DynamicDataList(MethodView):
        @blp.doc(security=[{"jwt": []}])
        @jwt_required()
        @blp.response(200, {"type": "object"})
        def get(self, projectId, model_name):
            """List records from a dynamically created table."""
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)

            result, headers = dynamic_api_service.list_records(
                projectId=projectId,
                model_name=model_name,
                page=page,
                per_page=per_page
            )
            return result, 200, headers

        @blp.doc(security=[{"jwt": []}])
        @jwt_required()
        @blp.arguments(AnyJsonSchema)
        @blp.response(201, {"type": "object"})
        def post(self, data, projectId, model_name):
            """Create a new record in a dynamically created table."""
            result, status = dynamic_api_service.create_record(
                projectId=projectId,
                model_name=model_name,
                data=data
            )
            if status != 201:
                abort(status, message=result.get('message', 'Error creating record.'))
            return result

        @blp.doc(security=[{"jwt": []}])
        @jwt_required()
        @blp.arguments(BulkDeleteSchema)
        @blp.response(204)
        def delete(self, data, projectId, model_name):
            """Delete multiple records."""
            ids_to_delete = data['ids']
            dynamic_api_service.bulk_delete(
                projectId=projectId,
                model_name=model_name,
                ids_to_delete=ids_to_delete
            )
            return ""
