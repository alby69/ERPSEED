from backend import create_app
from backend.extensions import db
from backend.models import SysModel, SysField, Project, User
from backend.core.utils.utils import generate_create_table_sql
from sqlalchemy import text

def seed_kpi(app=None):
    if app is None:
        app = create_app()
    with app.app_context():
        model_name = "dashboard_kpi"

        # Check if it already exists
        if SysModel.query.filter_by(name=model_name).first():
            print(f"The model '{model_name}' already exists in the database.")
            return

        print(f"Creating model '{model_name}'...")

        # 1. Find or create a system Project to contain the KPIs
        admin_user = User.query.filter_by(role='admin').first()
        project = Project.query.filter_by(name='system_core').first()

        if not project:
            project = Project(
                name='system_core',
                title='System Core',
                description='System project for KPIs and basic configurations',
                owner_id=admin_user.id if admin_user else 1 # Fallback ID
            )
            db.session.add(project)
            db.session.commit()

            # Create the DB schema for the project
            db.session.execute(text(f'CREATE SCHEMA IF NOT EXISTS "project_{project.id}"'))

        # 2. Create the Model definition (SysModel)
        kpi_model = SysModel(
            name=model_name,
            title="Dashboard KPIs",
            description="KPIs for the main dashboard",
            permissions='{"read": ["admin", "user"], "write": ["admin"]}',
            project_id=project.id
        )
        db.session.add(kpi_model)
        db.session.commit()

        # 2. Create the Fields (SysField)
        fields_data = [
            {"name": "label", "title": "Label", "type": "string", "required": True, "order": 1},
            {"name": "value", "title": "Value", "type": "string", "required": True, "order": 2},
            {"name": "trend", "title": "Trend", "type": "string", "required": False, "order": 3},
            {"name": "color", "title": "Color", "type": "string", "required": False, "order": 4},
            {"name": "icon", "title": "Icon", "type": "string", "required": False, "order": 5}
        ]

        for f in fields_data:
            field = SysField(model_id=kpi_model.id, **f)
            db.session.add(field)

        db.session.commit()

        # Reload the model to ensure relationships are updated
        db.session.refresh(kpi_model)

        # 3. Create the physical table in the DB
        print("Creating physical table...")
        schema_name = f"project_{project.id}"
        sql = generate_create_table_sql(kpi_model, schema=schema_name)
        db.session.execute(text(sql))

        # 4. Insert sample data
        print("Inserting sample data...")
        insert_sql = f"""
        INSERT INTO "{schema_name}"."{model_name}" ("label", "value", "trend", "color", "icon") VALUES
        ('Sales', '€ 12,500', '+15%', 'primary', 'dollar-sign'),
        ('Orders', '45', '+5%', 'success', 'shopping-cart'),
        ('Customers', '120', '+2%', 'info', 'users'),
        ('Tickets', '5', '-1', 'warning', 'alert-circle');
        """
        db.session.execute(text(insert_sql))
        db.session.commit()

        print("Done! The dashboard now has the necessary data.")

if __name__ == "__main__":
    seed_kpi()