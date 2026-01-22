from backend import create_app
from backend.extensions import db
from backend.models import User
import sys

def create_admin(email, password):
    email = email.lower()
    app = create_app()
    with app.app_context():
        # Controlla se l'utente esiste già
        user = User.query.filter_by(email=email).first()
        if user:
            print(f"Utente {email} trovato. Aggiornamento permessi a Admin...")
            user.role = "admin"
            user.is_active = True
            db.session.commit()
            return

        user = User(
            email=email,
            first_name="Admin",
            last_name="User",
            role="admin",
            is_active=True
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        print(f"Utente Admin {email} creato con successo!")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python -m backend.create_admin <email> <password>")
    else:
        create_admin(sys.argv[1], sys.argv[2])