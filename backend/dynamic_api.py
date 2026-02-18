from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required

from .schemas import SysModelSchema, AuditLogSchema
from .services import DynamicApiService

blp = Blueprint("dynamic_api", __name__, url_prefix="/projects/<int:project_id>", description="Dynamic CRUD API for builder models")

dynamic_api_service = DynamicApiService()


@blp.route("/data/<string:model_name>")
class DynamicDataList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
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
    def post(self, project_id, model_name):
        """Create a new record in a dynamically created table."""
        data = request.get_json() or {}
        
        result, status = dynamic_api_service.create_record(
            project_id=project_id,
            model_name=model_name,
            data=data
        )
        
        return result, status

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(204)
    def delete(self, project_id, model_name):
        """Delete multiple records."""
        data = request.get_json() or {}
        ids_to_delete = data.get('ids')
        
        if not ids_to_delete or not isinstance(ids_to_delete, list):
            abort(400, message="A list of 'ids' is required for bulk delete.")
        
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
    def get(self, project_id, model_name, item_id):
        """Retrieve a single record from a dynamic table."""
        return dynamic_api_service.get_record(
            project_id=project_id,
            model_name=model_name,
            item_id=item_id
        )

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def put(self, project_id, model_name, item_id):
        """Update a record in a dynamic table."""
        data = request.get_json() or {}
        
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
    def post(self, project_id, model_name, item_id):
        """Clone an existing record."""
        result, status = dynamic_api_service.clone_record(
            project_id=project_id,
            model_name=model_name,
            item_id=item_id
        )
        
        return result, status


@blp.route("/audit-logs")
class AuditLogList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, AuditLogSchema(many=True))
    def get(self):
        """Retrieve audit logs (admin only)."""
        from .models import User
        from flask import get_jwt_identity
        from .extensions import db
        
        user_id = get_jwt_identity()
        user = db.session.get(User, user_id)
        
        if not user or user.role != 'admin':
            abort(403, message="Access denied")
        
        try:
            from backend.core.models import AuditLog as CoreAuditLog
            AuditLog = CoreAuditLog
        except ImportError:
            from .models import AuditLog
        from sqlalchemy import desc
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        query = AuditLog.query.order_by(desc(AuditLog.timestamp))
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return pagination.items


@blp.route("/data/<string:model_name>/import")
class DynamicDataImport(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self, project_id, model_name):
        """Import data from CSV."""
        if 'file' not in request.files:
            abort(400, message="No file part")
        
        file = request.files['file']
        if file.filename == '':
            abort(400, message="No selected file")
            
        if not file.filename.lower().endswith('.csv'):
            abort(400, message="File must be a CSV")
        
        result, status = dynamic_api_service.import_csv(
            project_id=project_id,
            model_name=model_name,
            file=file
        )
        
        return result, status
