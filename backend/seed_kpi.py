from backend import create_app
from backend.extensions import db
from backend.models import SysModel, SysField
from backend.utils import generate_create_table_sql
from sqlalchemy import text

def seed_kpi():
    app = create_app()
    with app.app_context():
        model_name = "dashboard_kpi"
        
        # Controlla se esiste già
        if SysModel.query.filter_by(name=model_name).first():
            print(f"Il modello '{model_name}' esiste già nel database.")
            return

        print(f"Creazione modello '{model_name}'...")
        
        # 1. Crea la definizione del Modello (SysModel)
        kpi_model = SysModel(
            name=model_name,
            title="Dashboard KPIs",
            description="KPI per la dashboard principale",
            permissions='{"read": ["admin", "user"], "write": ["admin"]}'
        )
        db.session.add(kpi_model)
        db.session.commit()

        # 2. Crea i Campi (SysField)
        fields_data = [
            {"name": "label", "title": "Etichetta", "type": "string", "required": True, "order": 1},
            {"name": "value", "title": "Valore", "type": "string", "required": True, "order": 2},
            {"name": "trend", "title": "Trend", "type": "string", "required": False, "order": 3},
            {"name": "color", "title": "Colore", "type": "string", "required": False, "order": 4},
            {"name": "icon", "title": "Icona", "type": "string", "required": False, "order": 5}
        ]

        for f in fields_data:
            field = SysField(model_id=kpi_model.id, **f)
            db.session.add(field)
        
        db.session.commit()
        
        # Ricarica il modello per assicurarsi che le relazioni siano aggiornate
        db.session.refresh(kpi_model)

        # 3. Crea la tabella fisica nel DB
        print("Creazione tabella fisica...")
        sql = generate_create_table_sql(kpi_model)
        db.session.execute(text(sql))
        
        # 4. Inserisci dati di esempio
        print("Inserimento dati di esempio...")
        insert_sql = f"""
        INSERT INTO "{model_name}" ("label", "value", "trend", "color", "icon") VALUES 
        ('Vendite', '€ 12.500', '+15%', 'primary', 'dollar-sign'),
        ('Ordini', '45', '+5%', 'success', 'shopping-cart'),
        ('Clienti', '120', '+2%', 'info', 'users'),
        ('Ticket', '5', '-1', 'warning', 'alert-circle');
        """
        db.session.execute(text(insert_sql))
        db.session.commit()
        
        print("Fatto! La dashboard ora ha i dati necessari.")

if __name__ == "__main__":
    seed_kpi()