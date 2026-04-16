"""
Workflow Routes.

API endpoints for workflow automation management.
"""
from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields

from backend.models.workflow import Workflow, WorkflowStep, WorkflowExecution, WorkflowLog
from backend.modules.automation.services.workflow_service import WorkflowService
from backend.extensions import db
from backend.core.services.generic_service import generic_service
from backend.core.utils.utils import paginate
from backend.models.webhook import WebhookEvent
from backend.modules.automation.services.workflow_executor import WorkflowEngine

blp = Blueprint("workflows", __name__, url_prefix="/workflows", description="Workflow Automation")

# --- Schemas ---

class AnyJsonSchema(Schema):
    class Meta:
        unknown = "INCLUDE"

class WorkflowLogSchema(Schema):
    id = fields.Int(dump_only=True)
    step_name = fields.Str()
    status = fields.Str()
    input_data = fields.Dict(attribute="get_input_data", dump_only=True)
    output_data = fields.Dict(attribute="get_output_data", dump_only=True)
    error_message = fields.Str()
    started_at = fields.DateTime(allow_none=True)
    completed_at = fields.DateTime(allow_none=True)

class WorkflowExecutionSchema(Schema):
    id = fields.Int(dump_only=True)
    trigger_event = fields.Str()
    status = fields.Str()
    started_at = fields.DateTime(allow_none=True, dump_only=True)
    completed_at = fields.DateTime(allow_none=True, dump_only=True)
    error_message = fields.Str()

class WorkflowExecutionDetailSchema(WorkflowExecutionSchema):
    workflow_id = fields.Int()
    trigger_data = fields.Dict(attribute="get_trigger_data", dump_only=True)
    logs = fields.List(fields.Nested(WorkflowLogSchema), dump_only=True)

class WorkflowStepSchema(Schema):
    id = fields.Int(dump_only=True)
    order = fields.Int()
    step_type = fields.Str()
    name = fields.Str()
    config = fields.Dict()

class WorkflowListSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()
    description = fields.Str(allow_none=True)
    trigger_event = fields.Str()
    is_active = fields.Bool()
    project_id = fields.Int(allow_none=True)
    steps_count = fields.Function(lambda obj: obj.steps.count(), dump_only=True)
    created_at = fields.DateTime(dump_only=True, allow_none=True)

class WorkflowDetailSchema(WorkflowListSchema):
    steps = fields.List(fields.Nested(WorkflowStepSchema), dump_only=True)
    updated_at = fields.DateTime(dump_only=True, allow_none=True)

class WorkflowCreateSchema(Schema):
    name = fields.Str(required=True)
    trigger_event = fields.Str(required=True)
    description = fields.Str()
    project_id = fields.Int()

class WorkflowUpdateSchema(Schema):
    name = fields.Str()
    description = fields.Str()
    trigger_event = fields.Str()
    is_active = fields.Bool()
    project_id = fields.Int()

class WorkflowStepCreateSchema(Schema):
    step_type = fields.Str(required=True)
    name = fields.Str(required=True)
    config = fields.Dict(load_default={})
    order = fields.Int()

class TriggerListSchema(Schema):
    triggers = fields.List(fields.Str())
    categories = fields.Dict(keys=fields.Str(), values=fields.List(fields.Str()))

class WorkflowTestResponseSchema(Schema):
    execution_id = fields.Int()
    status = fields.Str()
    error = fields.Str(allow_none=True)

# --- Routes ---

@blp.route("")
class WorkflowList(MethodView):
    """Workflow list and creation."""

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, WorkflowListSchema(many=True))
    def get(self):
        """List all workflows."""
        project_id = request.args.get('project_id', type=int)
        active_only = request.args.get('active_only', 'true').lower() == 'true'

        query = WorkflowService.get_workflows(project_id, active_only)
        items, headers = paginate(query)

        return items, 200, headers

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(WorkflowCreateSchema)
    @blp.response(201, WorkflowListSchema)
    def post(self, data):
        """Create a new workflow."""
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

        return workflow


@blp.route("/<int:workflow_id>")
class WorkflowResource(MethodView):
    """Single workflow operations."""

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, WorkflowDetailSchema)
    def get(self, workflow_id):
        """Get workflow details with steps."""
        return generic_service.get_resource(Workflow, workflow_id)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(WorkflowUpdateSchema)
    @blp.response(200, WorkflowListSchema)
    def put(self, data, workflow_id):
        """Update workflow."""
        if 'trigger_event' in data:
            if data['trigger_event'] not in WebhookEvent.get_all_events() and data['trigger_event'] != '*':
                abort(400, message=f"Invalid trigger event: {data['trigger_event']}")

        workflow = WorkflowService.update_workflow(workflow_id, data)
        return workflow

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
    @blp.arguments(WorkflowStepCreateSchema)
    @blp.response(201, WorkflowStepSchema)
    def post(self, data, workflow_id):
        """Add a step to workflow."""
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

        return step


@blp.route("/steps/<int:step_id>")
class WorkflowStepResource(MethodView):
    """Single step operations."""

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(WorkflowStepSchema)
    @blp.response(200, WorkflowStepSchema)
    def put(self, data, step_id):
        """Update a step."""
        step = generic_service.get_resource(WorkflowStep, step_id)
        if 'name' in data:
            step.name = data['name']
        if 'config' in data:
            step.set_config(data['config'])
        if 'order' in data:
            step.order = data['order']

        db.session.commit()

        return step

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def delete(self, step_id):
        """Delete a step."""
        generic_service.delete_resource(WorkflowStep, step_id)
        return '', 204


@blp.route("/<int:workflow_id>/executions")
class WorkflowExecutions(MethodView):
    """Workflow execution history."""

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, WorkflowExecutionSchema(many=True))
    def get(self, workflow_id):
        """Get workflow execution history."""
        query = WorkflowService.get_workflow_executions(workflow_id)
        items, headers = paginate(query)
        return items, 200, headers


@blp.route("/executions/<int:execution_id>")
class WorkflowExecutionDetail(MethodView):
    """Single execution details."""

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, WorkflowExecutionDetailSchema)
    def get(self, execution_id):
        """Get execution details with step logs."""
        return generic_service.get_resource(WorkflowExecution, execution_id)


@blp.route("/<int:workflow_id>/test")
class WorkflowTest(MethodView):
    """Test workflow execution."""

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(AnyJsonSchema)
    @blp.response(200, WorkflowTestResponseSchema)
    def post(self, data, workflow_id):
        """Test run a workflow with provided data."""

        workflow = Workflow.query.get_or_404(workflow_id)

        execution = WorkflowExecution()
        execution.workflow_id=workflow_id
        execution.trigger_event='test'
        execution.trigger_data=json.dumps(data)
        execution.status='running'
        db.session.add(execution)
        db.session.commit()

        import datetime

        try:
            result = WorkflowEngine.run(workflow.id, 'test', data) # type: ignore
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
    @blp.response(200, TriggerListSchema)
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
    @blp.response(200)
    def get(self):
        """Get list of available step types."""
        return WorkflowService.get_step_types()


import json
