"""
Workflow Service.

Handles workflow automation logic:
- Event triggering
- Step execution
- Condition evaluation
- Action execution
"""

import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from flask import current_app
from sqlalchemy.orm import Query

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.base import BaseService
from backend.extensions import db
from backend.webhooks import WebhookEvent
from backend.workflows import Workflow, WorkflowStep


class WorkflowService(BaseService):
    """
    Service for managing workflow automation.
    Handles event triggering, step execution, and scheduling.
    """

    @staticmethod
    def trigger_event(
        event: str, data: Dict[str, Any], project_id: Optional[int] = None
    ):
        """
        Trigger all workflows that listen for this event.

        Args:
            event: Event type (e.g., 'user.created')
            data: Event payload data
            project_id: Optional project scope
        """
        from backend.workflows import Workflow, WorkflowExecution, WorkflowLog

        query = Workflow.query.filter_by(is_active=True)
        if project_id:
            query = query.filter(
                (Workflow.project_id == project_id) | (Workflow.project_id == None)
            )

        workflows = query.all()

        from backend.workflow_executor import WorkflowEngine

        for workflow in workflows:
            if workflow.trigger_event == event or workflow.trigger_event == "*":
                WorkflowEngine.run(workflow.id, event, data, project_id=project_id)

        try:
            from backend.shared.events import get_event_bus, DomainEvent

            event_bus = get_event_bus()
            event_bus.publish(
                DomainEvent(
                    event_type=event,
                    payload=data,
                    metadata={
                        "project_id": project_id,
                        "workflows_triggered": len(
                            [
                                w
                                for w in workflows
                                if w.trigger_event == event or w.trigger_event == "*"
                            ]
                        ),
                    },
                )
            )
        except Exception:
            pass

    @staticmethod
    def _execute_step(
        step, data: Dict[str, Any], execution, project_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Execute a single workflow step."""
        step_config = step.get_config()

        if step.step_type == "condition":
            return WorkflowService._execute_condition(step, step_config, data)
        elif step.step_type == "action":
            return WorkflowService._execute_action(step, step_config, data, project_id)
        elif step.step_type == "notification":
            return WorkflowService._execute_notification(step, step_config, data)
        elif step.step_type == "delay":
            return WorkflowService._execute_delay(step, step_config, data)
        elif step.step_type == "webhook":
            return WorkflowService._execute_webhook(step, step_config, data)
        else:
            return {"error": f"Unknown step type: {step.step_type}"}

    @staticmethod
    def _execute_condition(step, config: dict, data: dict) -> Dict[str, Any]:
        """Evaluate a condition step."""
        field = config.get("field")
        operator = config.get("operator")
        value = config.get("value")

        if not field:
            return {"error": "Condition field not specified"}

        field_value = data.get(field)

        result = False

        if operator == "equals":
            result = str(field_value) == str(value)
        elif operator == "not_equals":
            result = str(field_value) != str(value)
        elif operator == "contains":
            result = (
                str(value) in str(field_value) if field_value is not None else False
            )
        elif operator == "greater_than":
            try:
                result = float(field_value or 0) > float(value or 0)
            except (ValueError, TypeError):
                result = False
        elif operator == "less_than":
            try:
                result = float(field_value or 0) < float(value or 0)
            except (ValueError, TypeError):
                result = False
        elif operator == "is_empty":
            result = field_value is None or field_value == ""
        elif operator == "is_not_empty":
            result = field_value is not None and field_value != ""

        return {"output": {"condition_met": result}, "skip": not result}

    @staticmethod
    def _execute_action(
        step, config: dict, data: dict, project_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Execute an action step."""
        action_type = config.get("action_type")

        if action_type == "set_field":
            field = config.get("field")
            value = config.get("value")
            if field:
                data[field] = value
                return {"output": {field: value}}

        elif action_type == "update_record":
            return WorkflowService._execute_update_record(
                step, config, data, project_id
            )

        elif action_type == "create_record":
            return WorkflowService._execute_create_record(
                step, config, data, project_id
            )

        elif action_type == "send_email":
            return {"output": {"message": "Send email action - requires email service"}}

        return {"output": {"message": f"Action {action_type} executed"}}

    @staticmethod
    def _extract_model_from_trigger(event: str) -> Optional[str]:
        """Estrae il nome del modello da un trigger event.

        Esempi:
            'ordini.created' -> 'ordini'
            'record.created' -> None (generic)
            'clienti.updated' -> 'clienti'
        """
        if not event:
            return None

        if "." in event:
            parts = event.split(".")
            if parts[0] not in ["record", "user", "model"]:
                return parts[0]
        return None

    @staticmethod
    def _execute_update_record(
        step, config: dict, data: dict, project_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Esegue l'azione update_record usando DynamicApiService."""
        try:
            from backend.services.dynamic_api_service import DynamicApiService

            event = step.workflow.trigger_event
            model_name = config.get(
                "model_name"
            ) or WorkflowService._extract_model_from_trigger(event)

            if not model_name:
                return {
                    "error": "Cannot determine model name. Specify model_name in step config."
                }

            if not project_id:
                return {"error": "Project ID not available for this workflow."}

            record_id = data.get("id") or config.get("record_id")
            if not record_id:
                return {"error": "No record ID available in trigger data."}

            update_data = config.get("data", {})
            if not update_data and config.get("field") and config.get("value"):
                update_data = {config.get("field"): config.get("value")}

            if not update_data:
                return {"error": "No data provided to update."}

            dynamic_api = DynamicApiService()
            result = dynamic_api.update_record(
                project_id, model_name, record_id, update_data
            )

            return {
                "output": {
                    "action": "update_record",
                    "model": model_name,
                    "record_id": record_id,
                    "updated_fields": list(update_data.keys()),
                    "result": result,
                }
            }

        except Exception as e:
            return {"error": f"Failed to update record: {str(e)}"}

    @staticmethod
    def _execute_create_record(
        step, config: dict, data: dict, project_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Esegue l'azione create_record usando DynamicApiService."""
        try:
            from backend.services.dynamic_api_service import DynamicApiService

            event = step.workflow.trigger_event
            model_name = config.get(
                "model_name"
            ) or WorkflowService._extract_model_from_trigger(event)

            if not model_name:
                return {
                    "error": "Cannot determine model name. Specify model_name in step config."
                }

            if not project_id:
                return {"error": "Project ID not available for this workflow."}

            create_data = config.get("data", {})

            if not create_data:
                return {"error": "No data provided to create record."}

            dynamic_api = DynamicApiService()
            result, status_code = dynamic_api.create_record(
                project_id, model_name, create_data
            )

            new_id = result.get("id")

            return {
                "output": {
                    "action": "create_record",
                    "model": model_name,
                    "new_record_id": new_id,
                    "result": result,
                }
            }

        except Exception as e:
            return {"error": f"Failed to create record: {str(e)}"}

    @staticmethod
    def _execute_notification(step, config: dict, data: dict) -> Dict[str, Any]:
        """Execute a notification step."""
        notification_type = config.get("type", "webhook")

        if notification_type == "webhook":
            url = config.get("url")
            if url:
                try:
                    import requests

                    payload = {
                        "event": "workflow.notification",
                        "workflow": step.workflow.name,
                        "step": step.name,
                        "data": data,
                    }
                    response = requests.post(url, json=payload, timeout=10)
                    return {"output": {"sent": True, "status": response.status_code}}
                except Exception as e:
                    return {"error": str(e)}

        return {"output": {"notification_sent": False}}

    @staticmethod
    def _execute_delay(step, config: dict, data: dict) -> Dict[str, Any]:
        """Execute a delay step."""
        duration = config.get("duration", 0)
        unit = config.get("unit", "seconds")

        delay_seconds = duration
        if unit == "minutes":
            delay_seconds = duration * 60
        elif unit == "hours":
            delay_seconds = duration * 3600
        elif unit == "days":
            delay_seconds = duration * 86400

        return {
            "output": {
                "delay_seconds": delay_seconds,
                "note": "Delay executed (synchronous)",
            }
        }

    @staticmethod
    def _execute_webhook(step, config: dict, data: dict) -> Dict[str, Any]:
        """Execute a webhook call as a step."""
        url = config.get("url")
        method = config.get("method", "POST")

        if not url:
            return {"error": "Webhook URL not specified"}

        try:
            import requests

            headers = {"Content-Type": "application/json"}
            if config.get("headers"):
                headers.update(config.get("headers", {}))

            payload = {
                "workflow": step.workflow.name,
                "step": step.name,
                "trigger_data": data,
            }

            response = requests.request(
                method=method, url=url, json=payload, headers=headers, timeout=30
            )

            return {
                "output": {
                    "webhook_sent": True,
                    "status_code": response.status_code,
                    "response": response.text[:500] if response.text else None,
                }
            }
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def create_workflow(
        name: str,
        trigger_event: str,
        description: Optional[str] = None,
        project_id: Optional[int] = None,
        user_id: Optional[int] = None,
    ) -> "Workflow":
        """Create a new workflow."""
        workflow = Workflow(
            name=name,  # type: ignore
            trigger_event=trigger_event,  # type: ignore
            description=description,  # type: ignore
            project_id=project_id,  # type: ignore
            created_by=user_id,  # type: ignore
        )

        from backend.extensions import db

        db.session.add(workflow)
        db.session.commit()

        return workflow

    @staticmethod
    def add_step(
        workflow_id: int, step_type: str, name: str, config: dict, order: int = 0
    ) -> "WorkflowStep":
        """Add a step to a workflow."""
        step = WorkflowStep(
            workflow_id=workflow_id,  # type: ignore
            step_type=step_type,  # type: ignore
            name=name,  # type: ignore
            config=config,  # type: ignore
            order=order,  # type: ignore
        )

        from backend.extensions import db

        db.session.add(step)
        db.session.commit()

        return step

    @staticmethod
    def update_workflow(workflow_id: int, data: dict) -> "Workflow":
        """Update a workflow."""

        workflow = db.session.get(Workflow, workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")

        if "name" in data:
            workflow.name = data["name"]
        if "description" in data:
            workflow.description = data["description"]
        if "trigger_event" in data:
            workflow.trigger_event = data["trigger_event"]
        if "is_active" in data:
            workflow.is_active = data["is_active"]
        if "project_id" in data:
            workflow.project_id = data["project_id"]

        db.session.commit()
        return workflow

    @staticmethod
    def delete_workflow(workflow_id: int):
        """Delete a workflow."""
        workflow = db.session.get(Workflow, workflow_id)
        if workflow:
            db.session.delete(workflow)
            db.session.commit()

    @staticmethod
    def get_workflows(
        project_id: Optional[int] = None, active_only: bool = True
    ) -> "Query":
        """Get workflows query with optional filters."""
        query = Workflow.query

        if project_id:
            query = query.filter(
                (Workflow.project_id == project_id) | (Workflow.project_id == None)
            )

        if active_only:
            query = query.filter_by(is_active=True)

        return query.order_by(Workflow.created_at.desc())

    @staticmethod
    def get_workflow_executions(workflow_id: int) -> "Query":
        """Get workflow execution history query."""
        from backend.workflows import WorkflowExecution
        from sqlalchemy import desc

        return WorkflowExecution.query.filter_by(workflow_id=workflow_id).order_by(
            desc(WorkflowExecution.started_at)
        )

    @staticmethod
    def get_available_triggers():
        """Get list of available trigger events."""
        return WebhookEvent.get_all_events()

    @staticmethod
    def get_step_types():
        """Get list of available step types and their config schemas."""
        return {
            "condition": {
                "name": "Condition",
                "description": "Evaluate a condition to determine next steps",
                "config_schema": {
                    "field": {"type": "string", "required": True, "label": "Field"},
                    "operator": {
                        "type": "select",
                        "required": True,
                        "label": "Operator",
                        "options": [
                            "equals",
                            "not_equals",
                            "contains",
                            "greater_than",
                            "less_than",
                            "is_empty",
                            "is_not_empty",
                        ],
                    },
                    "value": {"type": "string", "required": False, "label": "Value"},
                },
            },
            "action": {
                "name": "Action",
                "description": "Perform an action",
                "config_schema": {
                    "action_type": {
                        "type": "select",
                        "required": True,
                        "label": "Action Type",
                        "options": [
                            "set_field",
                            "update_record",
                            "create_record",
                            "send_email",
                        ],
                    },
                    "field": {"type": "string", "required": False, "label": "Field"},
                    "value": {"type": "string", "required": False, "label": "Value"},
                },
            },
            "notification": {
                "name": "Notification",
                "description": "Send a notification",
                "config_schema": {
                    "type": {
                        "type": "select",
                        "required": True,
                        "label": "Notification Type",
                        "options": ["webhook", "email"],
                    },
                    "url": {"type": "string", "required": False, "label": "URL"},
                },
            },
            "delay": {
                "name": "Delay",
                "description": "Wait for a specified duration",
                "config_schema": {
                    "duration": {
                        "type": "number",
                        "required": True,
                        "label": "Duration",
                    },
                    "unit": {
                        "type": "select",
                        "required": True,
                        "label": "Unit",
                        "options": ["seconds", "minutes", "hours", "days"],
                    },
                },
            },
            "webhook": {
                "name": "Webhook",
                "description": "Call an external webhook",
                "config_schema": {
                    "url": {"type": "string", "required": True, "label": "URL"},
                    "method": {
                        "type": "select",
                        "required": True,
                        "label": "Method",
                        "options": ["POST", "PUT", "PATCH"],
                    },
                    "headers": {
                        "type": "object",
                        "required": False,
                        "label": "Headers",
                    },
                },
            },
        }


def trigger_workflow_event(
    event: str, data: Dict[str, Any], project_id: Optional[int] = None
):
    """
    Convenience function to trigger workflow automation.

    Usage:
        trigger_workflow_event('user.created', {'user_id': 1, 'email': 'test@example.com'}, project_id=1)
    """
    try:
        WorkflowService.trigger_event(event, data, project_id)
    except Exception as e:
        import traceback

        print(f"Workflow trigger failed: {e}", file=traceback.print_exc())
