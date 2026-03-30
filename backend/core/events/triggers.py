import json
from datetime import datetime

def trigger_webhook(event: str, data: dict, async_mode: bool = True):
    try:
        from backend.core.services.webhook_service import WebhookService
        from backend.core.services.webhook_service import WebhookService
        WebhookService.trigger_event(event, data, async_mode)
    except Exception:
        pass

    try:
        from backend.modules.automation.services.workflow_service import WorkflowService
        WorkflowService.trigger_event(event, data)
    except Exception:
        pass

    try:
        from backend.shared.events import get_event_bus, DomainEvent
        event_bus = get_event_bus()
        domain_event = DomainEvent(event_type=event, payload=data)
        event_bus.publish(domain_event)
    except Exception:
        pass

def on_user_created(user):
    trigger_webhook("user.created", {"id": user.id, "email": user.email})

def on_user_updated(user):
    trigger_webhook("user.updated", {"id": user.id, "email": user.email})

def on_user_deleted(user_id, email):
    trigger_webhook("user.deleted", {"id": user_id, "email": email})

def on_project_created(project):
    trigger_webhook("project.created", {"id": project.id, "name": project.name})

def on_project_updated(project):
    trigger_webhook("project.updated", {"id": project.id, "name": project.name})

def on_project_deleted(project_id, name):
    trigger_webhook("project.deleted", {"id": project_id, "name": name})

def on_model_created(model):
    trigger_webhook("model.created", {"id": model.id, "name": model.name})

def on_model_updated(model):
    trigger_webhook("model.updated", {"id": model.id, "name": model.name})

def on_model_deleted(model_id, name):
    trigger_webhook("model.deleted", {"id": model_id, "name": name})

def on_record_created(model_name, record_id, data, project_id):
    trigger_webhook("record.created", {"model": model_name, "record_id": record_id, "project_id": project_id, "data": data})

def on_record_updated(model_name, record_id, data, project_id):
    trigger_webhook("record.updated", {"model": model_name, "record_id": record_id, "project_id": project_id, "data": data})

def on_record_deleted(model_name, record_id, project_id):
    trigger_webhook("record.deleted", {"model": model_name, "record_id": record_id, "project_id": project_id})
