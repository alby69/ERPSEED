import sys
from werkzeug.security import generate_password_hash
from backend import create_app, db
from sqlalchemy import text

# NOTA: I percorsi di importazione sono stati corretti per riflettere la
# posizione effettiva dei modelli dopo il refactoring.
try:
    # I modelli User e Project sono definiti nel file models.py principale.
    from backend.models import User, Project, SysModel, SysField
    from backend.shared.utils.utils import generate_create_table_sql
    # Le funzioni di seeding per altri moduli.
    # NOTA: L'associazione utente-progetto viene gestita tramite la relazione 'members' del modello Project.
    from backend.domain.builder.models import create_system_archetypes
    from backend.marketplace.models import create_default_categories
except ImportError as e:
    print(f"ERRORE: Impossibile importare i modelli necessari. Dettagli: {e}")
    print("Assicurati che i modelli esistano e che i percorsi di importazione siano corretti.")
    sys.exit(1)

def seed_dashboard_kpi(project):
    """Crea il SysModel e i dati per i KPI della dashboard."""
    model_name = "dashboard_kpi"
    
    # Controlla se esiste già per questo progetto
    if SysModel.query.filter_by(name=model_name, project_id=project.id).first():
        print(f"   - Modello '{model_name}' già esistente nel progetto.")
        return

    print(f"   - Creazione modello '{model_name}'...")
    
    kpi_model = SysModel(
        name=model_name,
        technical_name=f"dashboard.{model_name}",
        table_name=model_name,
        title="Dashboard KPIs",
        description="KPIs for the main dashboard",
        permissions='{"read": ["admin", "user"], "write": ["admin"]}',
        project_id=project.id,
        status='published'
    )
    db.session.add(kpi_model)
    db.session.flush()

    fields_data = [
        {"name": "label", "technical_name": "label", "title": "Label", "type": "string", "required": True, "ui_order": 1},
        {"name": "value", "technical_name": "value", "title": "Value", "type": "string", "required": True, "ui_order": 2},
        {"name": "trend", "technical_name": "trend", "title": "Trend", "type": "string", "required": False, "ui_order": 3},
        {"name": "color", "technical_name": "color", "title": "Color", "type": "string", "required": False, "ui_order": 4},
        {"name": "icon", "technical_name": "icon", "title": "Icon", "type": "string", "required": False, "ui_order": 5}
    ]

    for f_data in fields_data:
        field = SysField(model_id=kpi_model.id, **f_data)
        db.session.add(field)
    
    db.session.flush()
    db.session.refresh(kpi_model)

    print("   - Creazione tabella fisica per i KPI...")
    schema_name = f"project_{project.id}"
    sql = generate_create_table_sql(kpi_model, schema=schema_name)
    db.session.execute(text(sql))

def setup_initial_data():
    """
    Comando unico per inizializzare il database con tutti i dati fondamentali.
    Questo script è idempotente e può essere eseguito più volte in sicurezza.
    
    Cosa fa:
    1. Crea l'utente amministratore di default (se non esiste).
    2. Crea il progetto di default (se non esiste).
    3. Associa l'admin al progetto di default (se non associato).
    4. Popola i dati di sistema (archetipi del builder, categorie del marketplace).
    """
    app = create_app()
    with app.app_context():
        admin_email = "admin@erpseed.org"
        admin_pass = "admin123"
        project_name = "Progetto Default"

        print("--- Inizio Setup Iniziale Database ---")

        # 1. Crea Utente Admin
        admin_user = User.query.filter_by(email=admin_email).first()
        if not admin_user:
            print(f"1. Creazione utente admin: {admin_email}...")
            admin_user = User(email=admin_email, password=generate_password_hash(admin_pass), role='admin')
            db.session.add(admin_user)
            db.session.commit()
            admin_user = User.query.filter_by(email=admin_email).first() # Ricarica per avere l'ID
            print("   ✅ Utente admin creato.")
        else:
            print("1. Utente admin già esistente.")

        # 2. Crea Progetto di Default
        project = Project.query.filter_by(name=project_name).first()
        if not project:
            print(f"2. Creazione progetto: '{project_name}'...")
            project = Project(
                name=project_name,
                title=project_name,  # Il titolo è obbligatorio
                owner_id=admin_user.id,  # L'owner è obbligatorio
                description="Progetto di default creato automaticamente."
            )
            db.session.add(project)
            db.session.flush()  # Ottiene il project.id prima del commit
            print("   ✅ Progetto di default creato.")
        else:
            print(f"2. Progetto '{project_name}' già esistente.")

        # 3. Associa Admin al Progetto
        # La relazione User-Project è una many-to-many semplice. L'associazione
        # si crea aggiungendo l'utente alla lista 'members' del progetto.
        if admin_user not in project.members:
            print(f"3. Associazione utente '{admin_email}' al progetto '{project_name}'...")
            project.members.append(admin_user)
            print("   ✅ Associazione completata.")
        else:
            print(f"3. Utente '{admin_email}' già associato al progetto.")

        # 4. Crea dati di sistema
        print("4. Creazione dati di sistema (archetipi e categorie)...")
        create_system_archetypes()
        create_default_categories()
        print("   ✅ Dati di sistema creati/verificati.")

        # 5. Crea KPI di default per la dashboard
        print("5. Creazione modello e dati KPI per la dashboard...")
        seed_dashboard_kpi(project)
        print("   - Inserimento dati di esempio per i KPI...")
        schema_name = f"project_{project.id}"
        insert_sql = f"""
        INSERT INTO "{schema_name}"."dashboard_kpi" (label, value, trend, color, icon) VALUES 
        ('Sales', '€ 12,500', '+15%', 'primary', 'dollar-sign'),
        ('Orders', '45', '+5%', 'success', 'shopping-cart'),
        ('Customers', '120', '+2%', 'info', 'users'),
        ('Tickets', '5', '-1', 'warning', 'alert-circle');
        """
        db.session.execute(text(insert_sql))
        print("   ✅ Dati KPI creati.")

        db.session.commit()
        print("\n--- ✅ Setup Iniziale Database Completato con Successo ---")

if __name__ == "__main__":
    setup_initial_data()