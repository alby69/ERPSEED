from models.workflow import Workflow
from models.webhook import WebhookEndpoint
from extensions import db
from flask_smorest import abort

class AutomationCommandHandler:
    def handle_create_workflow(self, cmd):
        workflow = Workflow(
            name=cmd.name,
            description=cmd.description,
            trigger_type=cmd.trigger_type,
            projectId=cmd.projectId,
            config=cmd.config
        )
        db.session.add(workflow)
        db.session.commit()
        return workflow

    def handle_update_workflow(self, cmd):
        workflow = db.session.get(Workflow, cmd.workflowId)
        if not workflow:
            abort(404, message="Workflow not found.")
        for key, value in cmd.data.items():
            if hasattr(workflow, key):
                setattr(workflow, key, value)
        db.session.commit()
        return workflow

    def handle_delete_workflow(self, cmd):
        workflow = db.session.get(Workflow, cmd.workflowId)
        if not workflow:
            abort(404, message="Workflow not found.")
        db.session.delete(workflow)
        db.session.commit()
        return True

    def handle_create_webhook(self, cmd):
        webhook = WebhookEndpoint(
            name=cmd.name,
            url=cmd.url,
            event_type=cmd.event_type,
            projectId=cmd.projectId,
            is_active=cmd.is_active
        )
        db.session.add(webhook)
        db.session.commit()
        return webhook
