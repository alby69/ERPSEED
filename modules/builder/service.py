from .application.handlers import BuilderCommandHandler
from .application.commands.builder_commands import (
    CreateModelCommand, UpdateModelCommand, DeleteModelCommand,
    CreateFieldCommand, SyncSchemaCommand, CloneModelCommand
)
from models import SysModel, AuditLog
from extensions import db
from core.utils.utils import apply_filters, apply_sorting, paginate
from sqlalchemy import desc

class BuilderService:
    def __init__(self):
        self.handler = BuilderCommandHandler()

    def get_all_models(self, search_fields=None, sort_by=None, sort_order='asc'):
        query = SysModel.query
        if search_fields:
            query = apply_filters(query, SysModel, search_fields)
        if sort_by:
            query = apply_sorting(query, SysModel)
        return paginate(query)

    def get_model(self, model_id):
        from sqlalchemy.orm import joinedload
        return db.session.query(SysModel).options(joinedload(SysModel.fields)).get(model_id)

    def create_model(self, project_id, name, title, **kwargs):
        cmd = CreateModelCommand(project_id, name, title, **kwargs)
        return self.handler.handle_create_model(cmd)

    def update_model(self, model_id, data):
        cmd = UpdateModelCommand(model_id, data)
        return self.handler.handle_update_model(cmd)

    def delete_model(self, model_id):
        cmd = DeleteModelCommand(model_id)
        return self.handler.handle_delete_model(cmd)

    def create_field(self, model_id, name, field_type, title=None, technical_name=None, **kwargs):
        cmd = CreateFieldCommand(model_id, name, field_type, title, technical_name, kwargs)
        return self.handler.handle_create_field(cmd)

    def sync_schema(self, model_id, db_engine):
        cmd = SyncSchemaCommand(model_id, db_engine)
        sql_commands = self.handler.handle_sync_schema(cmd)
        if not sql_commands:
            return [], "Schema is already up to date."
        return sql_commands, "Schema synced successfully."

    def clone_model(self, model_id, user_id, new_name, new_title):
        cmd = CloneModelCommand(model_id, user_id, new_name, new_title)
        return self.handler.handle_clone_model(cmd)

    def get_audit_logs(self, page=1, per_page=20):
        query = AuditLog.query.order_by(desc(AuditLog.created_at))
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return pagination.items, pagination.total

_builder_service = None

def get_builder_service():
    global _builder_service
    if _builder_service is None:
        _builder_service = BuilderService()
    return _builder_service
