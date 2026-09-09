"""
Script to register or replace CashRec module in ERPSEED database.
"""

from backend.__init__ import create_app
from backend.extensions import db
from backend.models import Module  # adjust if Module model exists or raw insert is used

def register_cashrec():
    app = create_app()
    with app.app_context():
        try:
            # Check if Module model exists or execute direct SQL
            from backend.core.models.module import Module as SysModule
            module = SysModule.query.filter_by(name="gdo_reconciliation").first()
            if module:
                module.name = "cashrec"
                module.title = "Riconciliazione Casse (CashRec)"
                module.description = "Modulo client-side per la riconciliazione delle casse con algoritmi avanzati."
                module.icon = "account-book"
            else:
                module = SysModule.query.filter_by(name="cashrec").first()
                if not module:
                    module = SysModule(
                        name="cashrec",
                        title="Riconciliazione Casse (CashRec)",
                        description="Modulo client-side per la riconciliazione delle casse con algoritmi avanzati.",
                        type="custom",
                        category="builtin",
                        icon="account-book",
                        is_active=True
                    )
                    db.session.add(module)
            db.session.commit()
            print("Successfully registered CashRec module.")
        except Exception as e:
            db.session.rollback()
            print(f"Error registering CashRec module: {e}")

if __name__ == "__main__":
    register_cashrec()
