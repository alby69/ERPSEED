import unittest
import json
from backend import create_app
from backend.extensions import db
from backend.models.workflow import Workflow, WorkflowStep
from backend.services.workflow_executor import WorkflowEngine

class WorkflowTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_workflow_execution(self):
        # Create a simple workflow
        wf = Workflow(name="Test Workflow", trigger_event="test.event", is_active=True)
        db.session.add(wf)
        db.session.commit()

        # Add a set_field step
        step = WorkflowStep(
            workflow_id=wf.id,
            name="Set status",
            step_type="action",
            order=1,
            config=json.dumps({"action_type": "set_field", "field": "status", "value": "processed"})
        )
        db.session.add(step)
        db.session.commit()

        # Run workflow
        trigger_data = {"id": 1, "status": "new"}
        execution = WorkflowEngine.run(wf.id, "test.event", trigger_data)

        self.assertIsNotNone(execution)
        self.assertEqual(execution.status, "completed")

        # Check logs
        from backend.models.workflow import WorkflowLog
        logs = WorkflowLog.query.filter_by(execution_id=execution.id).all()
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0].status, "success")

if __name__ == '__main__':
    unittest.main()
