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

from .base import BaseService
from ..webhooks import WebhookEvent


class WorkflowService(BaseService):
    """
    Service for managing workflow automation.
    Handles event triggering, step execution, and scheduling.
    """
    
    @staticmethod
    def trigger_event(event: str, data: Dict[str, Any], project_id: int = None):
        """
        Trigger all workflows that listen for this event.
        
        Args:
            event: Event type (e.g., 'user.created')
            data: Event payload data
            project_id: Optional project scope
        """
        from ..workflows import Workflow, WorkflowExecution, WorkflowLog
        
        query = Workflow.query.filter_by(is_active=True)
        if project_id:
            query = query.filter(
                (Workflow.project_id == project_id) | (Workflow.project_id == None)
            )
        
        workflows = query.all()
        
        for workflow in workflows:
            if workflow.trigger_event == event or workflow.trigger_event == '*':
                WorkflowService._execute_workflow(workflow, event, data)
    
    @staticmethod
    def _execute_workflow(workflow, event: str, data: Dict[str, Any]):
        """Execute a single workflow."""
        from ..workflows import WorkflowExecution, WorkflowLog
        from backend.extensions import db as db_ext
        
        execution = WorkflowExecution(
            workflow_id=workflow.id,
            trigger_event=event,
            trigger_data=json.dumps(data),
            status='running'
        )
        
        from backend.extensions import db as db_ext
        db_ext.session.add(execution)
        db_ext.session.flush()
        
        try:
            steps = workflow.get_steps()
            
            for step in steps:
                log = WorkflowLog(
                    execution_id=execution.id,
                    step_id=step.id,
                    step_name=step.name,
                    status='running',
                    input_data=json.dumps(data),
                    started_at=datetime.utcnow()
                )
                db_ext.session.add(log)
                db_ext.session.flush()
                
                try:
                    result = WorkflowService._execute_step(step, data, execution)
                    
                    if result.get('skip'):
                        log.status = 'skipped'
                    elif result.get('error'):
                        log.status = 'failed'
                        log.error_message = result.get('error')
                    else:
                        log.status = 'success'
                        log.set_output_data(result.get('output', {}))
                    
                    if result.get('error'):
                        execution.status = 'failed'
                        execution.error_message = result.get('error')
                        break
                    
                    if result.get('output'):
                        data.update(result['output'])
                
                except Exception as e:
                    log.status = 'failed'
                    log.error_message = str(e)
                    execution.status = 'failed'
                    execution.error_message = str(e)
                    db_ext.session.commit()
                    break
                
                log.completed_at = datetime.utcnow()
                db_ext.session.commit()
            
            if execution.status == 'running':
                execution.status = 'completed'
        
        except Exception as e:
            execution.status = 'failed'
            execution.error_message = str(e)
        
        execution.completed_at = datetime.utcnow()
        db_ext.session.commit()
    
    @staticmethod
    def _execute_step(step, data: Dict[str, Any], execution) -> Dict[str, Any]:
        """Execute a single workflow step."""
        step_config = step.get_config()
        
        if step.step_type == 'condition':
            return WorkflowService._execute_condition(step, step_config, data)
        elif step.step_type == 'action':
            return WorkflowService._execute_action(step, step_config, data)
        elif step.step_type == 'notification':
            return WorkflowService._execute_notification(step, step_config, data)
        elif step.step_type == 'delay':
            return WorkflowService._execute_delay(step, step_config, data)
        elif step.step_type == 'webhook':
            return WorkflowService._execute_webhook(step, step_config, data)
        else:
            return {'error': f'Unknown step type: {step.step_type}'}
    
    @staticmethod
    def _execute_condition(step, config: dict, data: dict) -> Dict[str, Any]:
        """Evaluate a condition step."""
        field = config.get('field')
        operator = config.get('operator')
        value = config.get('value')
        
        if not field:
            return {'error': 'Condition field not specified'}
        
        field_value = data.get(field)
        
        result = False
        
        if operator == 'equals':
            result = str(field_value) == str(value)
        elif operator == 'not_equals':
            result = str(field_value) != str(value)
        elif operator == 'contains':
            result = value in str(field_value) if field_value else False
        elif operator == 'greater_than':
            try:
                result = float(field_value) > float(value)
            except (ValueError, TypeError):
                result = False
        elif operator == 'less_than':
            try:
                result = float(field_value) < float(value)
            except (ValueError, TypeError):
                result = False
        elif operator == 'is_empty':
            result = field_value is None or field_value == ''
        elif operator == 'is_not_empty':
            result = field_value is not None and field_value != ''
        
        return {
            'output': {'condition_met': result},
            'skip': not result
        }
    
    @staticmethod
    def _execute_action(step, config: dict, data: dict) -> Dict[str, Any]:
        """Execute an action step."""
        action_type = config.get('action_type')
        
        if action_type == 'set_field':
            field = config.get('field')
            value = config.get('value')
            if field:
                data[field] = value
                return {'output': {field: value}}
        
        elif action_type == 'update_record':
            return {'output': {'message': 'Update record action - implement with dynamic API'}}
        
        elif action_type == 'create_record':
            return {'output': {'message': 'Create record action - implement with dynamic API'}}
        
        elif action_type == 'send_email':
            return {'output': {'message': 'Send email action - requires email service'}}
        
        return {'output': {'message': f'Action {action_type} executed'}}
    
    @staticmethod
    def _execute_notification(step, config: dict, data: dict) -> Dict[str, Any]:
        """Execute a notification step."""
        notification_type = config.get('type', 'webhook')
        
        if notification_type == 'webhook':
            url = config.get('url')
            if url:
                try:
                    import requests
                    payload = {
                        'event': 'workflow.notification',
                        'workflow': step.workflow.name,
                        'step': step.name,
                        'data': data
                    }
                    response = requests.post(url, json=payload, timeout=10)
                    return {'output': {'sent': True, 'status': response.status_code}}
                except Exception as e:
                    return {'error': str(e)}
        
        return {'output': {'notification_sent': False}}
    
    @staticmethod
    def _execute_delay(step, config: dict, data: dict) -> Dict[str, Any]:
        """Execute a delay step."""
        duration = config.get('duration', 0)
        unit = config.get('unit', 'seconds')
        
        delay_seconds = duration
        if unit == 'minutes':
            delay_seconds = duration * 60
        elif unit == 'hours':
            delay_seconds = duration * 3600
        elif unit == 'days':
            delay_seconds = duration * 86400
        
        return {'output': {'delay_seconds': delay_seconds, 'note': 'Delay executed (synchronous)'}}
    
    @staticmethod
    def _execute_webhook(step, config: dict, data: dict) -> Dict[str, Any]:
        """Execute a webhook call as a step."""
        url = config.get('url')
        method = config.get('method', 'POST')
        
        if not url:
            return {'error': 'Webhook URL not specified'}
        
        try:
            import requests
            
            headers = {'Content-Type': 'application/json'}
            if config.get('headers'):
                headers.update(config.get('headers', {}))
            
            payload = {
                'workflow': step.workflow.name,
                'step': step.name,
                'trigger_data': data
            }
            
            response = requests.request(
                method=method,
                url=url,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            return {
                'output': {
                    'webhook_sent': True,
                    'status_code': response.status_code,
                    'response': response.text[:500] if response.text else None
                }
            }
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def create_workflow(name: str, trigger_event: str, description: str = None, 
                       project_id: int = None, user_id: int = None) -> 'Workflow':
        """Create a new workflow."""
        from ..workflows import Workflow
        from backend.extensions import db
        
        workflow = Workflow(
            name=name,
            trigger_event=trigger_event,
            description=description,
            project_id=project_id,
            created_by=user_id
        )
        
        db.session.add(workflow)
        db.session.commit()
        
        return workflow
    
    @staticmethod
    def add_step(workflow_id: int, step_type: str, name: str, config: dict, 
                 order: int = 0) -> 'WorkflowStep':
        """Add a step to a workflow."""
        from ..workflows import WorkflowStep
        from backend.extensions import db
        
        step = WorkflowStep(
            workflow_id=workflow_id,
            step_type=step_type,
            name=name,
            set_config(config),
            order=order
        )
        
        db.session.add(step)
        db.session.commit()
        
        return step
    
    @staticmethod
    def update_workflow(workflow_id: int, data: dict) -> 'Workflow':
        """Update a workflow."""
        from ..workflows import Workflow
        from backend.extensions import db
        
        workflow = db.session.get(Workflow, workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        if 'name' in data:
            workflow.name = data['name']
        if 'description' in data:
            workflow.description = data['description']
        if 'trigger_event' in data:
            workflow.trigger_event = data['trigger_event']
        if 'is_active' in data:
            workflow.is_active = data['is_active']
        if 'project_id' in data:
            workflow.project_id = data['project_id']
        
        db.session.commit()
        return workflow
    
    @staticmethod
    def delete_workflow(workflow_id: int):
        """Delete a workflow."""
        from ..workflows import Workflow
        from backend.extensions import db
        
        workflow = db.session.get(Workflow, workflow_id)
        if workflow:
            db.session.delete(workflow)
            db.session.commit()
    
    @staticmethod
    def get_workflows(project_id: int = None, active_only: bool = True):
        """Get workflows with optional filters."""
        from ..workflows import Workflow
        
        query = Workflow.query
        
        if project_id:
            query = query.filter(
                (Workflow.project_id == project_id) | (Workflow.project_id == None)
            )
        
        if active_only:
            query = query.filter_by(is_active=True)
        
        return query.order_by(Workflow.created_at.desc()).all()
    
    @staticmethod
    def get_workflow_executions(workflow_id: int, limit: int = 50):
        """Get workflow execution history."""
        from ..workflows import WorkflowExecution
        from sqlalchemy import desc
        
        return WorkflowExecution.query.filter_by(
            workflow_id=workflow_id
        ).order_by(desc(WorkflowExecution.started_at)).limit(limit).all()
    
    @staticmethod
    def get_available_triggers():
        """Get list of available trigger events."""
        return WebhookEvent.get_all_events()
    
    @staticmethod
    def get_step_types():
        """Get list of available step types and their config schemas."""
        return {
            'condition': {
                'name': 'Condition',
                'description': 'Evaluate a condition to determine next steps',
                'config_schema': {
                    'field': {'type': 'string', 'required': True, 'label': 'Field'},
                    'operator': {
                        'type': 'select', 
                        'required': True, 
                        'label': 'Operator',
                        'options': ['equals', 'not_equals', 'contains', 'greater_than', 'less_than', 'is_empty', 'is_not_empty']
                    },
                    'value': {'type': 'string', 'required': False, 'label': 'Value'}
                }
            },
            'action': {
                'name': 'Action',
                'description': 'Perform an action',
                'config_schema': {
                    'action_type': {
                        'type': 'select',
                        'required': True,
                        'label': 'Action Type',
                        'options': ['set_field', 'update_record', 'create_record', 'send_email']
                    },
                    'field': {'type': 'string', 'required': False, 'label': 'Field'},
                    'value': {'type': 'string', 'required': False, 'label': 'Value'}
                }
            },
            'notification': {
                'name': 'Notification',
                'description': 'Send a notification',
                'config_schema': {
                    'type': {
                        'type': 'select',
                        'required': True,
                        'label': 'Notification Type',
                        'options': ['webhook', 'email']
                    },
                    'url': {'type': 'string', 'required': False, 'label': 'URL'}
                }
            },
            'delay': {
                'name': 'Delay',
                'description': 'Wait for a specified duration',
                'config_schema': {
                    'duration': {'type': 'number', 'required': True, 'label': 'Duration'},
                    'unit': {
                        'type': 'select',
                        'required': True,
                        'label': 'Unit',
                        'options': ['seconds', 'minutes', 'hours', 'days']
                    }
                }
            },
            'webhook': {
                'name': 'Webhook',
                'description': 'Call an external webhook',
                'config_schema': {
                    'url': {'type': 'string', 'required': True, 'label': 'URL'},
                    'method': {
                        'type': 'select',
                        'required': True,
                        'label': 'Method',
                        'options': ['POST', 'PUT', 'PATCH']
                    },
                    'headers': {'type': 'object', 'required': False, 'label': 'Headers'}
                }
            }
        }


def trigger_workflow_event(event: str, data: Dict[str, Any], project_id: int = None):
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
