from flask import request, Response
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from backend.modules.dynamic_api.service import get_dynamic_api_service
from backend.core.schemas.dynamic_schemas import ImportFileSchema

dynamic_api_service = get_dynamic_api_service()

def register_io_routes(blp):
    @blp.route("/data/<string:model_name>/import")
    class DynamicDataImport(MethodView):
        @blp.doc(security=[{"jwt": []}])
        @jwt_required()
        @blp.arguments(ImportFileSchema, location="files")
        @blp.response(200, {"type": "object"})
        def post(self, files, projectId, model_name):
            """Import data from CSV."""
            file = files['file']
            if file.filename == '':
                abort(400, message="No selected file")
            if file.filename and not file.filename.lower().endswith('.csv'):
                abort(400, message="File must be a CSV")

            result, status = dynamic_api_service.import_csv(
                projectId=projectId,
                model_name=model_name,
                file=file
            )
            return result, status

    @blp.route("/data/<string:model_name>/export")
    class DynamicDataExport(MethodView):
        @blp.doc(security=[{"jwt": []}])
        @jwt_required()
        def get(self, projectId, model_name):
            """Export data to CSV or JSON."""
            fmt = request.args.get('format', 'csv')
            result = dynamic_api_service.export_data(
                projectId=projectId,
                model_name=model_name,
                format=fmt
            )

            if fmt == 'csv':
                return Response(
                    result,
                    mimetype="text/csv",
                    headers={"Content-disposition": f"attachment; filename={model_name}_export.csv"}
                )
            return result

    @blp.route("/data/<string:model_name>/import-preview")
    class ImportPreview(MethodView):
        @blp.doc(security=[{"jwt": []}])
        @jwt_required()
        @blp.arguments(ImportFileSchema, location="files")
        @blp.response(200, {"type": "object"})
        def post(self, files, projectId, model_name):
            """Preview import without saving."""
            file = files['file']
            result, status = dynamic_api_service.import_preview(
                projectId=projectId,
                model_name=model_name,
                file=file
            )
            return result, status
