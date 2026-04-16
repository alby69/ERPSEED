"""
Seed Modules - Inizializza i moduli nel database.
"""
import yaml
from pathlib import Path
from extensions import db
from core.services.module_service import ModuleService
from core.services.tenant_module_service import TenantModuleService


def load_module_config():
    """Carica configurazione moduli da file YAML."""
    config_path = Path('/app/config/modules.yml')

    if not config_path.exists():
        config_path = Path(__file__).parent.parent.parent / 'config' / 'modules.yml'

    if not config_path.exists():
        # Try relative to current working directory
        config_path = Path('config/modules.yml')

    if not config_path.exists():
        return None

    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def seed_modules():
    """Inizializza moduli nel database."""
    print("Seeding modules...")

    config = load_module_config()

    if not config:
        print("No modules configuration found")
        return

    # Get module definitions (exclude 'plans' key)
    module_configs = {k: v for k, v in config.items() if k != 'plans'}

    if not module_configs:
        print("No modules configuration found")
        return

    for module_id, mod_def in module_configs.items():
        try:
            ModuleService.register_module(
                module_id=module_id,
                name=mod_def.get('name', module_id),
                description=mod_def.get('description', ''),
                category=mod_def.get('category', 'builtin'),
                version=mod_def.get('version', '1.0.0'),
                is_free=mod_def.get('is_free', True),
                price=mod_def.get('price'),
                plan_required=mod_def.get('plan_required', 'starter'),
                dependencies=mod_def.get('dependencies', []),
                icon=mod_def.get('icon', 'box'),
                menu_position=mod_def.get('menu_position', 100)
            )
            print(f"  - Registered module: {module_id}")
        except Exception as e:
            print(f"  - Error registering module {module_id}: {e}")

    print("Modules seeded successfully!")


def seed_modules_for_tenant(tenant_id: int, plan: str = 'starter'):
    """
    Abilita i moduli base per un nuovo tenant.

    Args:
        tenant_id: ID del tenant
        plan: Piano del tenant
    """
    print(f"Seeding modules for tenant {tenant_id} with plan '{plan}'...")

    # Abilita automaticamente i moduli inclusi nel piano
    try:
        enabled = TenantModuleService.enable_modules_for_new_tenant(tenant_id, plan)
        print(f"  - Enabled {len(enabled)} modules for tenant")
    except Exception as e:
        print(f"  - Error seeding tenant modules: {e}")


def get_plan_modules(plan: str) -> list:
    """
    Restituisce i moduli inclusi in un piano.

    Args:
        plan: Nome del piano

    Returns:
        Lista di ID moduli
    """
    config = load_module_config()
    plans = config.get('plans', {})

    if plan not in plans:
        return []

    plan_config = plans[plan]
    modules = plan_config.get('modules', [])

    if modules == "*":
        # Tutti i moduli
        return list(config.get('modules', {}).keys())

    return modules


if __name__ == '__main__':
    # Run seed when executed directly
    from . import create_app
    app = create_app()

    with app.app_context():
        seed_modules()
        # Also seed modules for the default tenant
        from extensions import db
        from core.models.tenant import Tenant
        tenant = Tenant.query.first()
        if tenant:
            seed_modules_for_tenant(tenant.id, 'starter')
