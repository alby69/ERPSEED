"""
Seed iniziale per il database.
Crea l'utente owner e il primo tenant.
"""
from . import create_app
from extensions import db
from models import User
from core.models import Tenant, TenantMember
from core.models.modulo import Modulo, ModuloAttivato
from modules.entities import Soggetto, Ruolo, Indirizzo, Contatto


def init_db():
    print("Initializing database...")
    app = create_app()

    with app.app_context():
        print("Creating tables...")
        db.create_all()

        # Create owner user
        print("Creating owner user...")
        owner = User(
            email='admin@erpseed.org',
            first_name='Admin',
            last_name='Admin',
            role='owner',
            is_active=True
        )
        owner.set_password('admin123')
        db.session.add(owner)
        db.session.flush()

        # Create default tenant (ERP del owner)
        print("Creating default tenant...")
        tenant = Tenant(
            name='ERPSeed Main',
            slug='flaskerp-main',
            email='admin@erpseed.org',
            piano='starter',
            stato='attivo',
            owner_id=owner.id,
            config={}
        )
        db.session.add(tenant)
        db.session.flush()

        # Add owner as member of tenant with admin role
        print("Adding owner to tenant...")
        member = TenantMember(
            tenant_id=tenant.id,
            user_id=owner.id,
            ruolo='admin',
            stato='attivo',
            accepted_at=db.func.now()
        )
        db.session.add(member)

        # Create core modules
        print("Creating core modules...")

        # Core module
        core_modulo = Modulo(
            nome='core',
            versione='1.0.0_20260219',
            titolo='Core Entities',
            descrizione='Entità core del sistema: Soggetto, Ruolo, Indirizzo, Contatto',
            autore='ERPSeed',
            tipo='core',
            stato='attivo',
            dipendenze=[],
            config_schema={},
            definizione='{}'
        )
        db.session.add(core_modulo)

        # Activate core module for the tenant
        attivazione = ModuloAttivato(
            tenant_id=tenant.id,
            modulo_id=None,  # Will be set after flush
            config_tenant={},
            attivato_da_id=owner.id,
            stato='attivo'
        )
        db.session.flush()

        # Set modulo_id for attivazione
        attivazione.modulo_id = core_modulo.id
        db.session.add(attivazione)

        # Create default roles for the tenant
        print("Creating default roles...")
        ruoli_default = [
            ('cliente', 'Cliente', 'Cliente finale'),
            ('fornitore', 'Fornitore', 'Fornitore di beni/servizi'),
            ('dipendente', 'Dipendente', 'Dipendente dell\'azienda'),
            ('autista', 'Autista', 'Autista per consegne'),
            ('consulente', 'Consulente', 'Consulente esterno'),
        ]

        for codice, nome, descrizione in ruoli_default:
            ruolo = Ruolo(
                codice=codice,
                nome=nome,
                descrizione=descrizione,
                stato='attivo',
                predefinito=True,
                tenant_id=tenant.id
            )
            db.session.add(ruolo)

        db.session.commit()

        print("\n" + "="*50)
        print("Database initialized successfully!")
        print("="*50)
        print(f"\nOwner User:")
        print(f"  Email: admin@erpseed.org")
        print(f"  Password: admin123")
        print(f"\nDefault Tenant:")
        print(f"  Name: {tenant.name}")
        print(f"  Slug: {tenant.slug}")
        print(f"  Plan: {tenant.piano}")
        print("="*50)

        return True


if __name__ == "__main__":
    init_db()
