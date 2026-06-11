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
            "data": {"label": f"Trigger: {self.trigger_event}", "triggerEvent": self.trigger_event},
            "position": {"x": 250, "y": 0}
        })

        steps = self.get_steps()

        for i, step in enumerate(steps):
            node_id = f"step_{step.id}"
            config = step.get_config()
            canvas = config.get("_canvas", {}) if isinstance(config, dict) else {}
            on_true = config.get("on_true", []) if isinstance(config, dict) else []
            on_false = config.get("on_false", []) if isinstance(config, dict) else []
            position = canvas.get("position") or {"x": 250, "y": (i + 1) * 100}

            nodes.append({
                "id": node_id,
                "type": step.step_type,
                "data": {
                    "label": step.name,
                    "config": {
                        **{k: v for k, v in config.items() if k not in ("_canvas", "on_true", "on_false")},
                        "_canvas": canvas,
                    },
                    "stepId": step.id,
                },
                "position": position,
            })

            if on_true or on_false:
                for target_id in on_true:
                    edges.append({
                        "id": f"edge_{node_id}_{target_id}_true",
                        "source": node_id,
                        "target": target_id,
                        "type": "smoothstep",
                        "data": {"branch": "true"},
                        "label": "True",
                    })
                for target_id in on_false:
                    edges.append({
                        "id": f"edge_{node_id}_{target_id}_false",
                        "source": node_id,
                        "target": target_id,
                        "type": "smoothstep",
                        "data": {"branch": "false"},
                        "label": "False",
                    })
            elif i == 0:
                edges.append({
                    "id": f"edge_trigger_{node_id}",
                    "source": "trigger",
                    "target": node_id,
                    "type": "smoothstep",
                })
            else:
                prev_node_id = f"step_{steps[i - 1].id}"
                edges.append({
                    "id": f"edge_{prev_node_id}_{node_id}",
                    "source": prev_node_id,
                    "target": node_id,
                    "type": "smoothstep",
                })

        return {"nodes": nodes, "edges": edges}

    def from_graph(self, graph_data):
        """Update workflow steps from a graph representation."""
        nodes = graph_data.get("nodes", []) or []
        edges = graph_data.get("edges", []) or []

        trigger_node = next((n for n in nodes if n.get("type") == "trigger"), None)
        if trigger_node:
            trigger_event = trigger_node.get("data", {}).get("triggerEvent")
            if trigger_event:
                self.trigger_event = trigger_event

        step_nodes = sorted(
            [n for n in nodes if n.get("type") != "trigger"],
            key=lambda node: (
                node.get("position", {}).get("y", 0),
                node.get("position", {}).get("x", 0),
            ),
        )

        from backend.extensions import db
        current_steps = self.get_steps()
        for step in current_steps:
            db.session.delete(step)
        db.session.flush()

        created_steps = {}

        for i, node in enumerate(step_nodes):
            node_id = node.get("id") or f"step-{i}"
            node_data = node.get("data", {}) or {}
            node_config = node_data.get("config", {}) or {}
            canvas_config = {
                "node_id": node_id,
                "position": node.get("position", {"x": 250, "y": (i + 1) * 100}),
            }

            new_step = WorkflowStep(
                workflowId=self.id,
                name=node_data.get("label", f"Step {i}"),
                step_type=node.get("type"),
                order=i,
            )
            new_step.set_config({
                **node_config,
                "_canvas": canvas_config,
            })
            db.session.add(new_step)
            created_steps[node_id] = new_step

        outgoing = {node_id: {"true": [], "false": []} for node_id in created_steps}
        for edge in edges:
            source = edge.get("source")
            target = edge.get("target")
            if source not in outgoing or target not in created_steps:
                continue

            branch = edge.get("data", {}).get("branch")
            if branch == "false":
                outgoing[source]["false"].append(target)
            else:
                outgoing[source]["true"].append(target)

        for node_id, step in created_steps.items():
            config = step.get_config()
            config["on_true"] = outgoing[node_id]["true"]
            config["on_false"] = outgoing[node_id]["false"]
            step.set_config(config)

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
