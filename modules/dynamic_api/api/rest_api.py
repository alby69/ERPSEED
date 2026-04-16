from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import fields, Schema

from core.schemas.schemas import SysModelSchema, AuditLogSchema
from modules.dynamic_api.service import get_dynamic_api_service
from extensions import db
from core.utils.utils import paginate

blp = Blueprint("dynamic_api", __name__, url_prefix="/projects/<int:project_id>", description="Dynamic CRUD API for builder models")

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
    def get(self, project_id, model_name):
        """List records from a dynamically created table."""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        result, headers = dynamic_api_service.list_records(
            project_id=project_id,
            model_name=model_name,
            page=page,
            per_page=per_page
        )

        return result, 200, headers

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(AnyJsonSchema)
    @blp.response(201, {"type": "object"})
    def post(self, data, project_id, model_name):
        """Create a new record in a dynamically created table."""

        result, status = dynamic_api_service.create_record(
            project_id=project_id,
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
    def delete(self, data, project_id, model_name):
        """Delete multiple records."""
        ids_to_delete = data['ids']

        dynamic_api_service.bulk_delete(
            project_id=project_id,
            model_name=model_name,
            ids_to_delete=ids_to_delete
        )

        return ""


@blp.route("/data/<string:model_name>/<int:item_id>")
class DynamicDataItem(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, {"type": "object"})
    def get(self, project_id, model_name, item_id):
        """Retrieve a single record from a dynamic table."""
        return dynamic_api_service.get_record(
            project_id=project_id,
            model_name=model_name,
            item_id=item_id
        )

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(AnyJsonSchema)
    @blp.response(200, {"type": "object"})
    def put(self, data, project_id, model_name, item_id):
        """Update a record in a dynamic table."""

        return dynamic_api_service.update_record(
            project_id=project_id,
            model_name=model_name,
            item_id=item_id,
            data=data
        )

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(204)
    def delete(self, project_id, model_name, item_id):
        """Delete a record from a dynamic table."""
        dynamic_api_service.delete_record(
            project_id=project_id,
            model_name=model_name,
            item_id=item_id
        )
        return ""


@blp.route("/data/<string:model_name>/meta")
class DynamicModelMeta(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, SysModelSchema)
    def get(self, project_id, model_name):
        """Retrieve metadata of a dynamic model for the frontend."""
        return dynamic_api_service.get_model_metadata(
            project_id=project_id,
            model_name=model_name
        )


@blp.route("/data/<string:model_name>/<int:item_id>/clone")
class DynamicDataClone(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(201, {"type": "object"})
    def post(self, project_id, model_name, item_id):
        """Clone an existing record."""
        result, status = dynamic_api_service.clone_record(
            project_id=project_id,
            model_name=model_name,
            item_id=item_id
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
        from models import User
        from extensions import db

        user_id = get_jwt_identity()
        user = db.session.get(User, user_id)

        if not user or user.role != 'admin':
            abort(403, message="Access denied")

        try:
            from core.models import AuditLog as CoreAuditLog
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
    def post(self, files, project_id, model_name):
        """Import data from CSV."""
        file = files['file']
        if file.filename == '':
            abort(400, message="No selected file")
        if file.filename and not file.filename.lower().endswith('.csv'):
            abort(400, message="File must be a CSV")

        result, status = dynamic_api_service.import_csv(
            project_id=project_id,
            model_name=model_name,
            file=file
        )

        if status != 200:
            abort(status, message=result.get('message', 'Error importing data.'))
        return result
