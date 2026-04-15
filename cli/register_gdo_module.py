from . import create_app
from extensions import db
from core.models.module import Module
from models import Project

def register_gdo_module():
    app = create_app()
    with app.app_context():
        # Create or update the module
        module = Module.query.filter_by(name="gdo_reconciliation").first()
        if not module:
            module = Module(
                name="gdo_reconciliation",
                title="Riconciliazione GDO",
                description="Modulo per la riconciliazione automatica degli incassi di cassa con i versamenti bancari.",
                type="custom",
                status="published",
                category="builtin",
                icon="account-book",
                version="1.0.0",
                menu_position=50
            )
            db.session.add(module)
            print("Created GDO Reconciliation module.")
        else:
            module.title = "Riconciliazione GDO"
            module.status = "published"
            print("Updated GDO Reconciliation module.")

        # Assign to the first project if exists for testing
        project = Project.query.first()
        if project and project not in module.projects:
            module.projects.append(project)
            print(f"Assigned module to project: {project.name}")

        db.session.commit()

if __name__ == "__main__":
    register_gdo_module()
