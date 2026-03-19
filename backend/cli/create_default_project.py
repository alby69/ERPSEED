import sys
from backend import create_app, db

# NOTA: Le importazioni dei modelli sono dedotte dalla struttura del progetto.
# I percorsi reali potrebbero variare leggermente (es. backend.auth.models).
try:
    from backend.models import User, Project
except ImportError:
    print("ERRORE: Impossibile trovare i modelli User, Project o UserProjectAssociation.")
    print("Assicurati che i modelli esistano e che i percorsi di importazione siano corretti.")
    sys.exit(1)


def create_default_project(project_name, admin_email):
    """
    Crea un progetto di default e vi assegna l'utente amministratore.
    Lo script è idempotente: non crea duplicati se eseguito più volte.
    """
    app = create_app()
    with app.app_context():
        # 1. Trova l'utente admin
        admin_user = User.query.filter_by(email=admin_email).first()
        if not admin_user:
            print(f"Errore: Utente admin '{admin_email}' non trovato. Crealo prima con lo script 'create_admin'.")
            return

        # 2. Controlla se il progetto esiste già
        project = Project.query.filter_by(name=project_name).first()

        if not project:
            # 3. Se non esiste, lo crea
            print(f"Progetto '{project_name}' non trovato. Lo creo...")
            project = Project(name=project_name, description="Progetto di default creato automaticamente.")
            db.session.add(project)
            db.session.flush()  # Per ottenere il project.id prima del commit
        else:
            print(f"Progetto '{project_name}' già esistente.")

        # 4. Controlla se l'utente è già associato al progetto
        association = UserProjectAssociation.query.filter_by(user_id=admin_user.id, project_id=project.id).first()
        if association:
            print(f"L'utente '{admin_email}' è già membro del progetto '{project_name}'. Nessuna azione necessaria.")
        else:
            # 5. Se non lo è, crea l'associazione
            print(f"Associo l'utente '{admin_email}' al progetto '{project_name}' con ruolo 'admin'...")
            new_association = UserProjectAssociation(user_id=admin_user.id, project_id=project.id, role='admin')
            db.session.add(new_association)

        db.session.commit()
        print("✅ Operazione completata con successo.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Utilizzo: python -m backend.create_default_project \"<nome_progetto>\"")
        sys.exit(1)
    
    create_default_project(project_name=sys.argv[1], admin_email="admin@erpseed.org")