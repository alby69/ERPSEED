from backend import create_app
from backend.extensions import db
from backend.create_admin import create_admin
from backend.seed_kpi import seed_kpi

def reset_db():
    print("Initializing database reset...")
    app = create_app()
    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()
        
        print("Creating all tables...")
        db.create_all()
        
        print("Seeding admin user...")
        create_admin('admin@example.com', 'admin123')
        
        print("Seeding KPIs...")
        seed_kpi()
        
        print("\n✅ Database reset complete! You can now restart your server.")

if __name__ == "__main__":
    reset_db()