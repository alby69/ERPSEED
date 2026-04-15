"""
Workflow Models.

Defines workflow automation structures:
- Workflow: Main automation definition
- WorkflowStep: Individual steps in a workflow
- WorkflowExecution: Runtime execution logs
"""
import json
from datetime import datetime
from extensions import db


class Workflow(db.Model):
    """Workflow automation definition."""
    __tablename__ = 'workflows'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    trigger_event = db.Column(db.String(100), nullable=False)  # Event that triggers the workflow
    is_active = db.Column(db.Boolean, default=True)
    projectId = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    steps = db.relationship('WorkflowStep', back_populates='workflow', lazy='dynamic', cascade='all, delete-orphan')
    executions = db.relationship('WorkflowExecution', back_populates='workflow', lazy='dynamic', cascade='all, delete-orphan')
    creator = db.relationship('User')
    project = db.relationship('Project')

    def __repr__(self):
        return f'<Workflow {self.name}: {self.trigger_event}>'

    def get_steps(self):
        """Get ordered list of steps."""
        return self.steps.order_by(WorkflowStep.order).all()


class WorkflowStep(db.Model):
    """Individual step in a workflow."""
    __tablename__ = 'workflow_steps'

    id = db.Column(db.Integer, primary_key=True)
    workflowId = db.Column(db.Integer, db.ForeignKey('workflows.id'), nullable=False)
    order = db.Column(db.Integer, default=0)
    step_type = db.Column(db.String(50), nullable=False)  # condition, action, notification, delay
    name = db.Column(db.String(150), nullable=False)
    config = db.Column(db.Text)  # JSON configuration for the step

    workflow = db.relationship('Workflow', back_populates='steps')

    def __repr__(self):
        return f'<WorkflowStep {self.name}: {self.step_type}>'

    def get_config(self):
        """Get parsed config."""
        try:
            return json.loads(self.config) if self.config else {}
        except:
            return {}

    def set_config(self, config):
        """Set config from dict."""
        self.config = json.dumps(config)


class WorkflowExecution(db.Model):
    """Workflow execution log."""
    __tablename__ = 'workflow_executions'

    id = db.Column(db.Integer, primary_key=True)
    workflowId = db.Column(db.Integer, db.ForeignKey('workflows.id'), nullable=False)
    trigger_event = db.Column(db.String(100), nullable=False)
    trigger_data = db.Column(db.Text)  # JSON data that triggered the workflow
    status = db.Column(db.String(20), default='running')  # running, completed, failed, cancelled
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    error_message = db.Column(db.Text)

    workflow = db.relationship('Workflow', back_populates='executions')

    def __repr__(self):
        return f'<WorkflowExecution {self.id}: {self.status}>'

    def get_trigger_data(self):
        """Get parsed trigger data."""
        try:
            return json.loads(self.trigger_data) if self.trigger_data else {}
        except:
            return {}

    def set_trigger_data(self, data):
        """Set trigger data."""
        self.trigger_data = json.dumps(data)

    @property
    def is_running(self):
        return self.status == 'running'

    @property
    def is_completed(self):
        return self.status == 'completed'


class WorkflowLog(db.Model):
    """Detailed log for each step execution."""
    __tablename__ = 'workflow_logs'

    id = db.Column(db.Integer, primary_key=True)
    execution_id = db.Column(db.Integer, db.ForeignKey('workflow_executions.id'), nullable=False)
    stepId = db.Column(db.Integer, db.ForeignKey('workflow_steps.id'), nullable=True)
    step_name = db.Column(db.String(150))
    status = db.Column(db.String(20), default='pending')  # pending, running, success, failed, skipped
    input_data = db.Column(db.Text)
    output_data = db.Column(db.Text)
    error_message = db.Column(db.Text)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)

    execution = db.relationship('WorkflowExecution')
    step = db.relationship('WorkflowStep')

    def __repr__(self):
        return f'<WorkflowLog {self.step_name}: {self.status}>'

    def get_input_data(self):
        try:
            return json.loads(self.input_data) if self.input_data else {}
        except:
            return {}

    def set_input_data(self, data):
        self.input_data = json.dumps(data)

    def get_output_data(self):
        try:
            return json.loads(self.output_data) if self.output_data else {}
        except:
            return {}

    def set_output_data(self, data):
        self.output_data = json.dumps(data)


class ScheduledTask(db.Model):
    """Scheduled/cron tasks for automation."""
    __tablename__ = 'scheduled_tasks'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    task_type = db.Column(db.String(50), nullable=False)  # webhook, email, script
    schedule = db.Column(db.String(100))  # Cron expression or interval
    config = db.Column(db.Text)  # JSON configuration
    is_active = db.Column(db.Boolean, default=True)
    projectId = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    last_run = db.Column(db.DateTime)
    next_run = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    creator = db.relationship('User')
    project = db.relationship('Project')

    def __repr__(self):
        return f'<ScheduledTask {self.name}>'

    def get_config(self):
        try:
            return json.loads(self.config) if self.config else {}
        except:
            return {}

    def set_config(self, config):
        self.config = json.dumps(config)
