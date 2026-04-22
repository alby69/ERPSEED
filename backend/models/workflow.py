"""
Workflow Models.

Defines workflow automation structures:
- Workflow: Main automation definition
- WorkflowStep: Individual steps in a workflow
- WorkflowExecution: Runtime execution logs
"""
import json
from datetime import datetime
from backend.extensions import db


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

    def to_graph(self):
        """Convert workflow to a graph representation (nodes and edges) for the visual editor."""
        nodes = []
        edges = []

        # Trigger node
        nodes.append({
            "id": "trigger",
            "type": "trigger",
            "data": {"label": f"Trigger: {self.trigger_event}"},
            "position": {"x": 250, "y": 0}
        })

        steps = self.get_steps()
        prev_node_id = "trigger"

        for i, step in enumerate(steps):
            node_id = f"step_{step.id}"
            nodes.append({
                "id": node_id,
                "type": step.step_type,
                "data": {
                    "label": step.name,
                    "config": step.get_config(),
                    "stepId": step.id
                },
                "position": {"x": 250, "y": (i + 1) * 100}
            })

            edges.append({
                "id": f"edge_{prev_node_id}_{node_id}",
                "source": prev_node_id,
                "target": node_id
            })
            prev_node_id = node_id

        return {"nodes": nodes, "edges": edges}

    def from_graph(self, graph_data):
        """Update workflow steps from a graph representation."""
        # This is a simplified version. A real implementation would handle branches and conditions.
        nodes = graph_data.get("nodes", [])

        # Identify steps and their order based on connections or position
        # For now, we assume a linear sequence based on nodes excluding trigger
        step_nodes = [n for n in nodes if n["type"] != "trigger"]

        # Remove existing steps and recreate? Or update?
        # Recreating is simpler for this POC
        from backend.extensions import db
        for step in self.steps:
            db.session.delete(step)

        for i, node in enumerate(step_nodes):
            new_step = WorkflowStep(
                workflowId=self.id,
                name=node["data"].get("label", f"Step {i}"),
                step_type=node["type"],
                order=i
            )
            new_step.set_config(node["data"].get("config", {}))
            db.session.add(new_step)

        db.session.commit()


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
