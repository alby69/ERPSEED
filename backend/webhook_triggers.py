"""
Webhook triggers for services.

Easy integration of webhooks into FlaskERP services.
"""
import json
from datetime import datetime


def trigger_webhook(event: str, data: dict, async_mode: bool = True):
    """
    Trigger a webhook event.
    
    Args:
        event: Event type (e.g., 'user.created')
        data: Event payload
        async_mode: Run asynchronously (for production, use Celery)
    """
    try:
        from ..webhook_service import WebhookService
        WebhookService.trigger_event(event, data, async_mode)
    except Exception as e:
        import sys
        print(f"Webhook trigger failed: {e}", file=sys.stderr)
    
    try:
        from ..workflow_service import WorkflowService
        WorkflowService.trigger_event(event, data)
    except Exception as e:
        import sys
        print(f"Workflow trigger failed: {e}", file=sys.stderr)


# User events
def on_user_created(user):
    """Trigger user.created event."""
    trigger_webhook('user.created', {
        'id': user.id,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'role': user.role
    })


def on_user_updated(user):
    """Trigger user.updated event."""
    trigger_webhook('user.updated', {
        'id': user.id,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'role': user.role
    })


def on_user_deleted(user_id, email):
    """Trigger user.deleted event."""
    trigger_webhook('user.deleted', {
        'id': user_id,
        'email': email
    })


# Project events
def on_project_created(project):
    """Trigger project.created event."""
    trigger_webhook('project.created', {
        'id': project.id,
        'name': project.name,
        'title': project.title,
        'owner_id': project.owner_id
    })


def on_project_updated(project):
    """Trigger project.updated event."""
    trigger_webhook('project.updated', {
        'id': project.id,
        'name': project.name,
        'title': project.title
    })


def on_project_deleted(project_id, name):
    """Trigger project.deleted event."""
    trigger_webhook('project.deleted', {
        'id': project_id,
        'name': name
    })


# Model events (Builder)
def on_model_created(model):
    """Trigger model.created event."""
    trigger_webhook('model.created', {
        'id': model.id,
        'name': model.name,
        'title': model.title,
        'project_id': model.project_id
    })


def on_model_updated(model):
    """Trigger model.updated event."""
    trigger_webhook('model.updated', {
        'id': model.id,
        'name': model.name,
        'title': model.title
    })


def on_model_deleted(model_id, name):
    """Trigger model.deleted event."""
    trigger_webhook('model.deleted', {
        'id': model_id,
        'name': name
    })


# Record events (Dynamic API)
def on_record_created(model_name, record_id, data, project_id):
    """Trigger record.created event."""
    trigger_webhook('record.created', {
        'model': model_name,
        'record_id': record_id,
        'project_id': project_id,
        'data': data
    })


def on_record_updated(model_name, record_id, data, project_id):
    """Trigger record.updated event."""
    trigger_webhook('record.updated', {
        'model': model_name,
        'record_id': record_id,
        'project_id': project_id,
        'data': data
    })


def on_record_deleted(model_name, record_id, project_id):
    """Trigger record.deleted event."""
    trigger_webhook('record.deleted', {
        'model': model_name,
        'record_id': record_id,
        'project_id': project_id
    })


# Accounting events
def on_journal_entry_created(entry):
    """Trigger journal.created event."""
    trigger_webhook('journal.created', {
        'id': entry.id,
        'entry_number': entry.entry_number,
        'description': entry.description,
        'total_debit': float(entry.total_debit),
        'total_credit': float(entry.total_credit)
    })


def on_invoice_created(invoice):
    """Trigger invoice.created event."""
    trigger_webhook('invoice.created', {
        'id': invoice.id,
        'invoice_number': invoice.invoice_number,
        'type': invoice.invoice_type,
        'total': float(invoice.total),
        'party_id': invoice.party_id
    })


# HR events
def on_employee_created(employee):
    """Trigger employee.created event."""
    trigger_webhook('employee.created', {
        'id': employee.id,
        'employee_number': employee.employee_number,
        'full_name': employee.first_name + ' ' + employee.last_name,
        'department_id': employee.department_id
    })


def on_leave_requested(leave):
    """Trigger leave.requested event."""
    trigger_webhook('leave.requested', {
        'id': leave.id,
        'employee_id': leave.employee_id,
        'leave_type': leave.leave_type,
        'start_date': leave.start_date.isoformat() if leave.start_date else None,
        'end_date': leave.end_date.isoformat() if leave.end_date else None,
        'days': leave.days
    })


def on_leave_approved(leave):
    """Trigger leave.approved event."""
    trigger_webhook('leave.approved', {
        'id': leave.id,
        'employee_id': leave.employee_id,
        'leave_type': leave.leave_type,
        'start_date': leave.start_date.isoformat() if leave.start_date else None,
        'end_date': leave.end_date.isoformat() if leave.end_date else None,
        'days': leave.days,
        'approved_by': leave.approved_by
    })
