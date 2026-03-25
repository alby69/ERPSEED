"""
Module Service - Service per gestione moduli a livello di sistema.
"""
from typing import List, Optional, Dict, Any
from backend.extensions import db
from backend.core.models.module_definition import ModuleDefinition
from backend.core.models.tenant import Tenant


class ModuleServiceError(Exception):
    """Base exception for module service."""
    pass


class ModuleNotFoundError(ModuleServiceError):
    """Modulo non trovato nel sistema."""
    pass


class ModuleDependencyError(ModuleServiceError):
    """Dipendenza non soddisfatta."""
    pass


class PlanNotCompatibleError(ModuleServiceError):
    """Piano corrente non supporta il modulo."""
    pass


class LicenseInvalidError(ModuleServiceError):
    """Licenza non valida."""
    pass


class ModuleService:
    """Service per gestire moduli a livello di sistema."""

    @staticmethod
    def get_available_modules() -> List[ModuleDefinition]:
        """Restituisce tutti i moduli disponibili e attivi."""
        return ModuleDefinition.query.filter_by(is_active=True).order_by(
            ModuleDefinition.menu_position
        ).all()

    @staticmethod
    def get_module_by_id(module_id: str) -> Optional[ModuleDefinition]:
        """Restituisce un modulo per ID."""
        return ModuleDefinition.query.filter_by(
            module_id=module_id,
            is_active=True
        ).first()

    @staticmethod
    def get_modules_by_category(category: str) -> List[ModuleDefinition]:
        """Restituisce moduli per categoria."""
        return ModuleDefinition.query.filter_by(
            category=category,
            is_active=True
        ).order_by(ModuleDefinition.menu_position).all()

    @staticmethod
    def get_core_modules() -> List[ModuleDefinition]:
        """Restituisce moduli core."""
        return ModuleService.get_modules_by_category('core')

    @staticmethod
    def get_builtin_modules() -> List[ModuleDefinition]:
        """Restituisce moduli builtin."""
        return ModuleService.get_modules_by_category('builtin')

    @staticmethod
    def get_premium_modules() -> List[ModuleDefinition]:
        """Restituisce moduli premium."""
        return ModuleService.get_modules_by_category('premium')

    @staticmethod
    def check_plan_compatibility(tenant_plan: str, module: ModuleDefinition) -> bool:
        """
        Verifica se il piano del tenant è compatibile con il modulo.

        Piani in ordine crescente: starter < professional < enterprise
        """
        plan_hierarchy = {
            'starter': 0,
            'professional': 1,
            'enterprise': 2
        }

        tenant_level = plan_hierarchy.get(tenant_plan, 0)
        required_level = plan_hierarchy.get(module.plan_required, 0)

        return tenant_level >= required_level

    @staticmethod
    def check_dependencies(tenant_id: int, module: ModuleDefinition) -> List[str]:
        """
        Verifica le dipendenze di un modulo.
        Restituisce lista di dipendenze mancanti.
        """
        from backend.core.models.tenant_module import TenantModule

        missing = []
        for dep_id in (module.dependencies or []):
            dep_module = TenantModule.query.filter_by(
                tenant_id=tenant_id,
                module_id=dep_id,
                is_enabled=True
            ).first()

            if not dep_module:
                missing.append(dep_id)

        return missing

    @staticmethod
    def register_module(
        module_id: str,
        name: str,
        description: str,
        category: str,
        version: str = "1.0.0",
        is_free: bool = True,
        price: float = None,
        plan_required: str = "starter",
        dependencies: List[str] = None,
        icon: str = "box",
        menu_position: int = 100
    ) -> ModuleDefinition:
        """Registra un nuovo modulo nel sistema."""
        existing = ModuleDefinition.query.filter_by(module_id=module_id).first()

        if existing:
            existing.name = name
            existing.description = description
            existing.category = category
            existing.version = version
            existing.is_free = is_free
            existing.price = price
            existing.plan_required = plan_required
            existing.dependencies = dependencies or []
            existing.icon = icon
            existing.menu_position = menu_position
            module = existing
        else:
            module = ModuleDefinition(
                module_id=module_id,
                name=name,
                description=description,
                category=category,
                version=version,
                is_free=is_free,
                price=price,
                plan_required=plan_required,
                dependencies=dependencies or [],
                core_version_min="1.0.0",
                icon=icon,
                menu_position=menu_position,
                is_active=True
            )
            db.session.add(module)

        db.session.commit()
        return module

    @staticmethod
    def unregister_module(module_id: str) -> bool:
        """Disattiva un modulo dal sistema (soft delete)."""
        module = ModuleDefinition.query.filter_by(module_id=module_id).first()

        if not module:
            return False

        module.is_active = False
        db.session.commit()
        return True
