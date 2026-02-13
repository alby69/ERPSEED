"""
Workflow Routes.

API endpoints for workflow automation management.
"""
from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity

from .workflows import Workflow, WorkflowStep, WorkflowExecution, WorkflowLog
from .workflow_service import WorkflowService
from .extensions import db
from .webhooks import WebhookEvent

blp = Blueprint("workflows", __name__, url_prefix="/workflows", description="Workflow Automation")


@blp.route("")
class WorkflowList(MethodView):
    """Workflow list and creation."""
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        """List all workflows."""
        project_id = request.args.get('project_id', type=int)
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        
        workflows = WorkflowService.get_workflows(project_id, active_only)
        
        result = []
        for w in workflows:
            result.append({
                'id': w.id,
                'name': w.name,
                'description': w.description,
                'trigger_event': w.trigger_event,
                'is_active': w.is_active,
                'project_id': w.project_id,
                'steps_count': w.steps.count(),
                'created_at': w.created_at.isoformat() if w.created_at else None
            })
        
        return result
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        """Create a new workflow."""
        data = request.get_json()
        
        if not data.get('name'):
            abort(400, message="Name is required")
        if not data.get('trigger_event'):
            abort(400, message="Trigger event is required")
        
        if data['trigger_event'] not in WebhookEvent.get_all_events() and data['trigger_event'] != '*':
            abort(400, message=f"Invalid trigger event: {data['trigger_event']}")
        
        user_id = get_jwt_identity()
        
        workflow = WorkflowService.create_workflow(
            name=data['name'],
            trigger_event=data['trigger_event'],
            description=data.get('description'),
            project_id=data.get('project_id'),
            user_id=user_id
        )
        
        return {
            'id': workflow.id,
            'name': workflow.name,
            'description': workflow.description,
            'trigger_event': workflow.trigger_event,
            'is_active': workflow.is_active,
            'project_id': workflow.project_id,
            'created_at': workflow.created_at.isoformat() if workflow.created_at else None
        }, 201


@blp.route("/<int:workflow_id>")
class WorkflowResource(MethodView):
    """Single workflow operations."""
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, workflow_id):
        """Get workflow details with steps."""
        workflow = Workflow.query.get_or_404(workflow_id)
        
        steps = []
        for s in workflow.get_steps():
            steps.append({
                'id': s.id,
                'order': s.order,
                'step_type': s.step_type,
                'name': s.name,
                'config': s.get_config()
            })
        
        return {
            'id': workflow.id,
            'name': workflow.name,
            'description': workflow.description,
            'trigger_event': workflow.trigger_event,
            'is_active': workflow.is_active,
            'project_id': workflow.project_id,
            'steps': steps,
            'created_at': workflow.created_at.isoformat() if workflow.created_at else None,
            'updated_at': workflow.updated_at.isoformat() if workflow.updated_at else None
        }
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def put(self, workflow_id):
        """Update workflow."""
        data = request.get_json()
        
        if 'trigger_event' in data:
            if data['trigger_event'] not in WebhookEvent.get_all_events() and data['trigger_event'] != '*':
                abort(400, message=f"Invalid trigger event: {data['trigger_event']}")
        
        workflow = WorkflowService.update_workflow(workflow_id, data)
        
        return {
            'id': workflow.id,
            'name': workflow.name,
            'description': workflow.description,
            'trigger_event': workflow.trigger_event,
            'is_active': workflow.is_active,
            'project_id': workflow.project_id
        }
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def delete(self, workflow_id):
        """Delete workflow."""
        WorkflowService.delete_workflow(workflow_id)
        return '', 204


@blp.route("/<int:workflow_id>/steps")
class WorkflowSteps(MethodView):
    """Manage workflow steps."""
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self, workflow_id):
        """Add a step to workflow."""
        data = request.get_json()
        
        if not data.get('step_type'):
            abort(400, message="Step type is required")
        if not data.get('name'):
            abort(400, message="Step name is required")
        
        valid_types = ['condition', 'action', 'notification', 'delay', 'webhook']
        if data['step_type'] not in valid_types:
            abort(400, message=f"Invalid step type. Must be one of: {valid_types}")
        
        workflow = Workflow.query.get_or_404(workflow_id)
        
        max_order = db.session.query(db.func.max(WorkflowStep.order)).filter_by(
            workflow_id=workflow_id
        ).scalar() or -1
        
        step = WorkflowService.add_step(
            workflow_id=workflow_id,
            step_type=data['step_type'],
            name=data['name'],
            config=data.get('config', {}),
            order=data.get('order', max_order + 1)
        )
        
        return {
            'id': step.id,
            'order': step.order,
            'step_type': step.step_type,
            'name': step.name,
            'config': step.get_config()
        }, 201


@blp.route("/steps/<int:step_id>")
class WorkflowStepResource(MethodView):
    """Single step operations."""
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def put(self, step_id):
        """Update a step."""
        data = request.get_json()
        
        step = WorkflowStep.query.get_or_404(step_id)
        
        if 'name' in data:
            step.name = data['name']
        if 'config' in data:
            step.set_config(data['config'])
        if 'order' in data:
            step.order = data['order']
        
        db.session.commit()
        
        return {
            'id': step.id,
            'order': step.order,
            'step_type': step.step_type,
            'name': step.name,
            'config': step.get_config()
        }
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def delete(self, step_id):
        """Delete a step."""
        step = WorkflowStep.query.get_or_404(step_id)
        db.session.delete(step)
        db.session.commit()
        return '', 204


@blp.route("/<int:workflow_id>/executions")
class WorkflowExecutions(MethodView):
    """Workflow execution history."""
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, workflow_id):
        """Get workflow execution history."""
        limit = request.args.get('limit', 50, type=int)
        
        executions = WorkflowService.get_workflow_executions(workflow_id, limit)
        
        result = []
        for e in executions:
            result.append({
                'id': e.id,
                'trigger_event': e.trigger_event,
                'status': e.status,
                'started_at': e.started_at.isoformat() if e.started_at else None,
                'completed_at': e.completed_at.isoformat() if e.completed_at else None,
                'error_message': e.error_message
            })
        
        return result


@blp.route("/executions/<int:execution_id>")
class WorkflowExecutionDetail(MethodView):
    """Single execution details."""
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, execution_id):
        """Get execution details with step logs."""
        execution = WorkflowExecution.query.get_or_404(execution_id)
        
        logs = WorkflowLog.query.filter_by(execution_id=execution_id).order_by(
            WorkflowLog.started_at
        ).all()
        
        log_list = []
        for log in logs:
            log_list.append({
                'id': log.id,
                'step_name': log.step_name,
                'status': log.status,
                'input_data': log.get_input_data(),
                'output_data': log.get_output_data(),
                'error_message': log.error_message,
                'started_at': log.started_at.isoformat() if log.started_at else None,
                'completed_at': log.completed_at.isoformat() if log.completed_at else None
            })
        
        return {
            'id': execution.id,
            'workflow_id': execution.workflow_id,
            'trigger_event': execution.trigger_event,
            'trigger_data': execution.get_trigger_data(),
            'status': execution.status,
            'started_at': execution.started_at.isoformat() if execution.started_at else None,
            'completed_at': execution.completed_at.isoformat() if execution.completed_at else None,
            'error_message': execution.error_message,
            'logs': log_list
        }


@blp.route("/<int:workflow_id>/test")
class WorkflowTest(MethodView):
    """Test workflow execution."""
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self, workflow_id):
        """Test run a workflow with provided data."""
        data = request.get_json() or {}
        
        workflow = Workflow.query.get_or_404(workflow_id)
        
        execution = WorkflowExecution(
            workflow_id=workflow_id,
            trigger_event='test',
            trigger_data=json.dumps(data),
            status='running'
        )
        db.session.add(execution)
        db.session.commit()
        
        import datetime
        from .workflow_service import WorkflowService as WS
        
        try:
            result = WS._execute_workflow(workflow, 'test', data)
            execution.status = 'completed'
        except Exception as e:
            execution.status = 'failed'
            execution.error_message = str(e)
        
        execution.completed_at = datetime.datetime.utcnow()
        db.session.commit()
        
        return {
            'execution_id': execution.id,
            'status': execution.status,
            'error': execution.error_message
        }


@blp.route("/triggers")
class WorkflowTriggers(MethodView):
    """Available trigger events."""
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        """Get list of available trigger events."""
        return {
            'triggers': WebhookEvent.get_all_events(),
            'categories': WebhookEvent.get_categories()
        }


@blp.route("/step-types")
class WorkflowStepTypes(MethodView):
    """Available step types."""
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        """Get list of available step types."""
        return WorkflowService.get_step_types()


import json
