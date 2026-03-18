"""
Debugging API
REST API for system inspection and debugging.
"""
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields
from backend.core.models.audit import AuditLog
from backend.extensions import db

blp = Blueprint(
    "debugging",
    __name__,
    url_prefix="/api/v1/debugging",
    description="System Debugging API"
)

class AuditLogSchema(Schema):
    id = fields.Int(dump_only=True)
    action = fields.String()
    resource_type = fields.String()
    resource_id = fields.Int()
    status = fields.String()
    created_at = fields.DateTime(dump_only=True)
    user_id = fields.Int()

class SystemHealthSchema(Schema):
    status = fields.String()
    database = fields.String()
    version = fields.String()

class StateInspectorSchema(Schema):
    message = fields.String()
    active_sessions = fields.Int()
    memory_usage = fields.String()

@blp.route("/health")
class SystemHealth(MethodView):
    @blp.response(200, SystemHealthSchema)
    def get(self):
        """Get system health status."""
        from sqlalchemy import text
        db_status = "ok"
        try:
            db.session.execute(text("SELECT 1"))
        except Exception:
            db_status = "error"

        return {
            "status": "healthy" if db_status == "ok" else "degraded",
            "database": db_status,
            "version": "1.0.0"
        }

@blp.route("/logs")
class DebugLogs(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, AuditLogSchema(many=True))
    def get(self):
        """Get recent audit logs for debugging."""
        return AuditLog.query.order_by(AuditLog.created_at.desc()).limit(50).all()

@blp.route("/state-inspector")
class StateInspector(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, StateInspectorSchema)
    def get(self):
        """Mock endpoint for state inspection logic."""
        return {
            "message": "State inspector active",
            "active_sessions": 1,
            "memory_usage": "normal"
        }
