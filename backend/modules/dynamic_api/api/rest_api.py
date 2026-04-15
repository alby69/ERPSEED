from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import fields, Schema

from backend.core.schemas.schemas import SysModelSchema, AuditLogSchema
from backend.modules.dynamic_api.service import get_dynamic_api_service
from backend.extensions import db
from backend.core.utils.utils import paginate

blp = Blueprint("dynamic_api", __name__, url_prefix="/projects/<int:projectId>", description="Dynamic CRUD API for builder models")

dynamic_api_service = get_dynamic_api_service()

class AnyJsonSchema(Schema):
    class Meta:
        unknown = "INCLUDE"

class BulkDeleteSchema(Schema):
    ids = fields.List(fields.Int(), required=True)


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


@blp.route("/data/<string:model_name>/<int:itemId>")
class DynamicDataItem(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, {"type": "object"})
    def get(self, projectId, model_name, itemId):
        """Retrieve a single record from a dynamic table."""
        return dynamic_api_service.get_record(
            projectId=projectId,
            model_name=model_name,
            itemId=itemId
        )

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(AnyJsonSchema)
    @blp.response(200, {"type": "object"})
    def put(self, data, projectId, model_name, itemId):
        """Update a record in a dynamic table."""

        return dynamic_api_service.update_record(
            projectId=projectId,
            model_name=model_name,
            itemId=itemId,
            data=data
        )

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(204)
    def delete(self, projectId, model_name, itemId):
        """Delete a record from a dynamic table."""
        dynamic_api_service.delete_record(
            projectId=projectId,
            model_name=model_name,
            itemId=itemId
        )
        return ""


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


@blp.route("/data/<string:model_name>/<int:itemId>/clone")
class DynamicDataClone(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(201, {"type": "object"})
    def post(self, projectId, model_name, itemId):
        """Clone an existing record."""
        result, status = dynamic_api_service.clone_record(
            projectId=projectId,
            model_name=model_name,
            itemId=itemId
        )

        if status != 201:
            abort(status, message=result.get('message', 'Error cloning record.'))
        return result


@blp.route("/audit-logs")
class AuditLogList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, AuditLogSchema(many=True))
    def get(self):
        """Retrieve audit logs (admin only)."""
        from backend.models import User
        from backend.extensions import db

        userId = get_jwt_identity()
        user = db.session.get(User, userId)

        if not user or user.role != 'admin':
            abort(403, message="Access denied")

        try:
            from backend.core.models import AuditLog as CoreAuditLog
            AuditLog = CoreAuditLog
        except ImportError:
            abort(500, message="AuditLog model not available.")
        from sqlalchemy import desc

        query = AuditLog.query.order_by(desc(AuditLog.created_at))
        items, headers = paginate(query)
        return items, 200, headers


@blp.route("/data/<string:model_name>/import")
class DynamicDataImport(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(Schema.from_dict({"file": fields.Raw(metadata={"type": "file"}, required=True)}), location="files")
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

        if status != 200:
            abort(status, message=result.get('message', 'Error importing data.'))
        return result
