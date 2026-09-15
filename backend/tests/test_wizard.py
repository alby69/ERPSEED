import os
import unittest

os.environ["JWT_SECRET_KEY"] = "this-is-a-32-character-long-secret-key-for-testing"

from backend import create_app
from backend.extensions import db
from backend.models import Project, SysModel
from backend.modules.wizard.services import domain_analysis_service, wizard_provisioning_service


class WizardTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("sqlite:///:memory:")
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        from backend.models import User
        user = User(email='admin@example.com', role='admin')
        db.session.add(user)
        db.session.flush()

        self.project = Project(name='test_project', title='Test Project', owner_id=user.id)
        db.session.add(self.project)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_domain_analysis_service(self):
        payload = {
            "company_name": "Logistica Express",
            "industry": "Trasporti",
            "has_inventory": True,
            "has_purchases": True,
            "has_projects": False,
            "custom_description": "Ho una flotta di furgoni che svolgono consegne giornaliere"
        }
        spec = domain_analysis_service.analyze_domain(payload)

        self.assertEqual(spec["company_name"], "Logistica Express")
        self.assertIn("inventory", spec["modules"])
        self.assertIn("purchases", spec["modules"])

        entity_names = [e["name"] for e in spec["entities"]]
        self.assertIn("Customer", entity_names)
        self.assertIn("Vehicle", entity_names)

    def test_wizard_provisioning_service(self):
        domain_spec = {
            "company_name": "AutoNoleggio Pro",
            "modules": ["sales", "inventory"],
            "entities": [
                {
                    "name": "RentalUnit",
                    "table": "rental_units",
                    "title": "Unità a Noleggio",
                    "fields": [
                        {"name": "code", "type": "string", "title": "Codice", "required": True},
                        {"name": "is_available", "type": "boolean", "title": "Disponibile", "required": False}
                    ]
                }
            ]
        }

        res = wizard_provisioning_service.provision_domain(domain_spec, project_id=self.project.id)
        self.assertTrue(res["success"])

        sys_model = SysModel.query.filter_by(projectId=self.project.id, name="rental_units").first()
        self.assertIsNotNone(sys_model)
        field_names = [f.name for f in sys_model.fields]
        self.assertIn("code", field_names)
        self.assertIn("is_available", field_names)


if __name__ == "__main__":
    unittest.main()
