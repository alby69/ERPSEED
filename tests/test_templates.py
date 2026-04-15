import unittest
import json
from . import create_app
from extensions import db
from models import Project, SysModel, SysField
from modules.system_tools.services.template_service import TemplateService

class TemplateTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Create a test user and project
        from models import User
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
        self.assertEqual(templates[0]['id'], 'crm_base')

    def test_install_template(self):
        service = TemplateService()
        result = service.install_template('crm_base', self.project.id)

        self.assertTrue(result['success'])
        self.assertGreater(len(result['models']), 0)

        # Verify models were actually created
        models = SysModel.query.filter_by(projectId=self.project.id).all()
        self.assertEqual(len(models), 3) # customer, lead, activity

        # Verify fields for 'customer'
        customer = SysModel.query.filter_by(projectId=self.project.id, name='crm_customers').first()
        self.assertIsNotNone(customer)
        self.assertGreater(len(customer.fields), 0)

        field_names = [f.name for f in customer.fields]
        self.assertIn('name', field_names)
        self.assertIn('email', field_names)

if __name__ == '__main__':
    unittest.main()
