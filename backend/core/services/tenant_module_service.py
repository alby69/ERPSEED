"""
Tenant Module Service - Service per gestione moduli a livello di tenant.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from backend.extensions import db
from backend.core.models.tenant_module import TenantModule
from backend.core.models.tenant import Tenant
from backend.core.services.module_service import (
    ModuleService, 
    ModuleNotFoundError,
    ModuleDependencyError,
    PlanNotCompatibleError,
    LicenseInvalidError
)


class TenantModuleService:
    """Service per gestire moduli a livello di tenant."""
    
    @staticmethod
    def get_enabled_modules(tenant_id: int) -> List[TenantModule]:
        """Restituisce i moduli attivi per un tenant."""
        return TenantModule.query.filter_by(
            tenant_id=tenant_id, 
            is_enabled=True
        ).all()
    
    @staticmethod
    def get_enabled_module_ids(tenant_id: int) -> List[str]:
        """Restituisce gli ID dei moduli attivi per un tenant."""
        modules = TenantModule.query.filter_by(
            tenant_id=tenant_id,
            is_enabled=True
        ).all()
        return [tm.module_id for tm in modules]
    
    @staticmethod
    def is_module_enabled(tenant_id: int, module_id: str) -> bool:
        """Verifica se un modulo è attivo per un tenant."""
        tm = TenantModule.query.filter_by(
            tenant_id=tenant_id,
            module_id=module_id,
            is_enabled=True
        ).first()
        return tm is not None
    
    @staticmethod
    def get_tenant_module(tenant_id: int, module_id: str) -> Optional[TenantModule]:
        """Restituisce la configurazione del modulo per un tenant."""
        return TenantModule.query.filter_by(
            tenant_id=tenant_id,
            module_id=module_id
        ).first()
    
    @staticmethod
    def enable_module(
        tenant_id: int, 
        module_id: str,
        license_key: str = None,
        config: dict = None
    ) -> TenantModule:
        """Attiva un modulo per un tenant."""
        # Verifica che il modulo esista
        module_def = ModuleService.get_module_by_id(module_id)
        if not module_def:
            raise ModuleNotFoundError(f"Modulo {module_id} non trovato")
        
        # Verifica piano
        tenant = Tenant.query.get(tenant_id)
        if not tenant:
            raise ValueError(f"Tenant {tenant_id} non trovato")
        
        if not ModuleService.check_plan_compatibility(tenant.plan, module_def):
            raise PlanNotCompatibleError(
                f"Piano '{tenant.plan}' non supporta il modulo '{module_def.name}'. "
                f"Piano richiesto: '{module_def.plan_required}'"
            )
        
        # Verifica dipendenze
        missing_deps = ModuleService.check_dependencies(tenant_id, module_def)
        if missing_deps:
            raise ModuleDependencyError(
                f"Modulo richiede dipendenze non attive: {', '.join(missing_deps)}"
            )
        
        # Valida licenza se modulo premium
        if not module_def.is_free and license_key:
            if not TenantModuleService._validate_license(license_key, tenant_id, module_id):
                raise LicenseInvalidError("Licenza non valida")
        
        # Crea o aggiorna
        tm = TenantModule.query.filter_by(
            tenant_id=tenant_id,
            module_id=module_id
        ).first()
        
        now = datetime.utcnow()
        
        if tm:
            tm.is_enabled = True
            tm.enabled_at = now
            tm.disabled_at = None
            tm.license_key = license_key
            tm.config = config or {}
        else:
            tm = TenantModule(
                tenant_id=tenant_id,
                module_id=module_id,
                is_enabled=True,
                enabled_at=now,
                license_key=license_key,
                config=config or {}
            )
            db.session.add(tm)
        
        db.session.commit()
        
        # Hook: notifica plugin system
        try:
            from backend.plugins.registry import PluginRegistry
            PluginRegistry.enable(module_id)
        except Exception as e:
            print(f"Warning: Could not enable plugin {module_id}: {e}")
        
        return tm
    
    @staticmethod
    def disable_module(tenant_id: int, module_id: str) -> bool:
        """Disattiva un modulo per un tenant."""
        # Non permettere disattivazione moduli core
        module_def = ModuleService.get_module_by_id(module_id)
        if module_def and module_def.category == 'core':
            raise ValueError("I moduli core non possono essere disattivati")
        
        tm = TenantModule.query.filter_by(
            tenant_id=tenant_id,
            module_id=module_id
        ).first()
        
        if not tm or not tm.is_enabled:
            return False
        
        # Verifica che altri moduli non dipendano da questo
        enabled = TenantModuleService.get_enabled_modules(tenant_id)
        for enabled_mod in enabled:
            if enabled_mod.module_id == module_id:
                continue
            
            mod_def = ModuleService.get_module_by_id(enabled_mod.module_id)
            if mod_def and module_id in (mod_def.dependencies or []):
                raise ModuleDependencyError(
                    f"Impossibile disattivare: '{mod_def.name}' dipende da '{module_def.name}'"
                )
        
        tm.is_enabled = False
        tm.disabled_at = datetime.utcnow()
        db.session.commit()
        
        # Hook: notifica plugin system
        try:
            from backend.plugins.registry import PluginRegistry
            PluginRegistry.disable(module_id)
        except Exception as e:
            print(f"Warning: Could not disable plugin {module_id}: {e}")
        
        return True
    
    @staticmethod
    def get_module_config(tenant_id: int, module_id: str) -> dict:
        """Restituisce la configurazione di un modulo per un tenant."""
        tm = TenantModule.query.filter_by(
            tenant_id=tenant_id,
            module_id=module_id
        ).first()
        return tm.config if tm and tm.config else {}
    
    @staticmethod
    def update_module_config(tenant_id: int, module_id: str, config: dict) -> dict:
        """Aggiorna la configurazione di un modulo."""
        tm = TenantModule.query.filter_by(
            tenant_id=tenant_id,
            module_id=module_id
        ).first()
        
        if not tm:
            raise ModuleNotFoundError(
                f"Modulo {module_id} non attivo per questo tenant"
            )
        
        # Merge config
        current_config = tm.config or {}
        current_config.update(config)
        tm.config = current_config
        db.session.commit()
        
        return tm.config
    
    @staticmethod
    def _validate_license(license_key: str, tenant_id: int, module_id: str) -> bool:
        """
        Valida licenza per modulo premium.
        Implementazione base - può essere estesa.
        """
        # Basic validation: license key should not be empty
        # In production, this would validate against a license server
        if not license_key or len(license_key) < 10:
            return False
        
        # Could add: check against license server, validate signature, etc.
        return True
    
    @staticmethod
    def enable_modules_for_new_tenant(tenant_id: int, plan: str = 'starter') -> List[TenantModule]:
        """
        Abilita i moduli base per un nuovo tenant in base al piano.
        """
        enabled_modules = []
        
        # Core modules always enabled
        core_modules = ModuleService.get_core_modules()
        for mod in core_modules:
            tm = TenantModuleService.enable_module(tenant_id, mod.module_id)
            enabled_modules.append(tm)
        
        # Builtin modules based on plan
        builtin_modules = ModuleService.get_builtin_modules()
        for mod in builtin_modules:
            if ModuleService.check_plan_compatibility(plan, mod):
                tm = TenantModuleService.enable_module(tenant_id, mod.module_id)
                enabled_modules.append(tm)
        
        return enabled_modules
