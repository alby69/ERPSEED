from .application.handlers import AutomationCommandHandler
from .application.commands.automation_commands import (
    CreateWorkflowCommand, UpdateWorkflowCommand, DeleteWorkflowCommand,
    CreateWebhookCommand
)
from backend.models.workflow import Workflow
from backend.models.webhook import WebhookEndpoint
from backend.extensions import db

class AutomationService:
    def __init__(self):
        self.handler = AutomationCommandHandler()

    def create_workflow(self, data):
        cmd = CreateWorkflowCommand(**data)
        return self.handler.handle_create_workflow(cmd)

    def update_workflow(self, workflow_id, data):
        cmd = UpdateWorkflowCommand(workflow_id, data)
        return self.handler.handle_update_workflow(cmd)

    def delete_workflow(self, workflow_id):
        cmd = DeleteWorkflowCommand(workflow_id)
        return self.handler.handle_delete_workflow(cmd)

    def list_workflows(self):
        return Workflow.query.all()

    def create_webhook(self, data):
        cmd = CreateWebhookCommand(**data)
        return self.handler.handle_create_webhook(cmd)

    def list_webhooks(self):
        return WebhookEndpoint.query.all()

_automation_service = None

def get_automation_service():
    global _automation_service
    if _automation_service is None:
        _automation_service = AutomationService()
    return _automation_service
