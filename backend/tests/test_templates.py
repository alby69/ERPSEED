import os
import unittest

os.environ["JWT_SECRET_KEY"] = "this-is-a-32-character-long-secret-key-for-testing"

from backend import create_app
from backend.extensions import db
from backend.models import Project, SysModel
from backend.modules.system_tools.services.template_service import TemplateService


class TemplateTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("sqlite:///:memory:")
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        from backend.models import User
        user = User(email='test@example.com', role='admin')
        db.session.add(user)
        db.session.flush()

        self.project = Project(name='test_proj', title='Test Project', owner_id=user.id)
        db.session.add(self.project)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_list_templates(self):
        service = TemplateService()
        templates = service.list_templates()
        self.assertGreater(len(templates), 0)
        template_ids = [t['id'] for t in templates]
        self.assertIn('crm_base', template_ids)
        self.assertIn('commercial', template_ids)
        self.assertIn('manufacturing', template_ids)
        self.assertIn('services', template_ids)

    def test_apply_commercial_yaml_template(self):
        service = TemplateService()
        result = service.apply_template('commercial', projectId=self.project.id)

        self.assertTrue(result['success'])
        self.assertEqual(result['template_id'], 'commercial')
        self.assertIn('sales', result['modules'])

        # Verify created SysModels
        quotations_model = SysModel.query.filter_by(projectId=self.project.id, name='commercial_quotations').first()
        self.assertIsNotNone(quotations_model)
        field_names = [f.name for f in quotations_model.fields]
        self.assertIn('code', field_names)
        self.assertIn('customer_name', field_names)

    def test_apply_manufacturing_yaml_template(self):
        service = TemplateService()
        result = service.apply_template('manufacturing', projectId=self.project.id)

        self.assertTrue(result['success'])
        self.assertEqual(result['template_id'], 'manufacturing')
        self.assertIn('manufacturing', result['modules'])

        quality_model = SysModel.query.filter_by(projectId=self.project.id, name='quality_inspections').first()
        self.assertIsNotNone(quality_model)


if __name__ == '__main__':
    unittest.main()
