from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.core.schemas.schemas import AuditLogSchema
from backend.core.utils.utils import paginate
from backend.extensions import db

def register_audit_routes(blp):
    @blp.route("/audit-logs")
    class AuditLogList(MethodView):
        @blp.doc(security=[{"jwt": []}])
        @jwt_required()
        @blp.response(200, AuditLogSchema(many=True))
        def get(self):
            """Retrieve audit logs (admin only)."""
            from backend.models.user import User
            userId = get_jwt_identity()
            user = db.session.get(User, userId)

            if not user or user.role != 'admin':
                abort(403, message="Access denied")

            try:
                from backend.core.models.audit import AuditLog
            except ImportError:
                abort(500, message="AuditLog model not available.")

            from sqlalchemy import desc
            query = AuditLog.query.order_by(desc(AuditLog.created_at))
            items, headers = paginate(query)
            return items, 200, headers
