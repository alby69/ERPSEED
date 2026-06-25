import json
from backend import create_app
from backend.extensions import db
from backend.services.template_service import TemplateService

def seed_gdo_models():
    app = create_app()
    with app.app_context():
        # Use TemplateService to install it
        ts = TemplateService()
        # Assuming project ID 1 exists
        project_id = 1
        # In this environment, we use 'gdo_reconciliation' as ID (matches filename)
        try:
            res = ts.install_template('gdo_reconciliation', project_id)
            print(res["message"])
        except Exception as e:
            print(f"Error seeding models: {e}")

if __name__ == "__main__":
    seed_gdo_models()
