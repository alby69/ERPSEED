"""
System API - Endpoints per informazioni di sistema.
"""

from flask import g
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_smorest import Blueprint

from backend.models import User
from backend.core.services.module_service import ModuleService
from backend.core.services.tenant_module_service import TenantModuleService
from backend.plugins.registry import ModuleRegistry

blp = Blueprint("system", __name__, url_prefix="/api/v1/system")


@blp.route("/modules-info")
class SystemModulesInfo(MethodView):
    @blp.response(200)
    @jwt_required()
    def get(self):
        """
        Restituisce informazioni completo moduli per UI.
        Include stato, menu, widget per il tenant corrente.
        """
        user = User.query.get(get_jwt_identity())
        tenant_id = user.tenant_id

        # Moduli abilitati per tenant
        enabled_ids = set(TenantModuleService.get_enabled_module_ids(tenant_id))

        result = {
            "available_modules": [],
            "enabled_modules": list(enabled_ids),
            "menu": [],
            "widgets": [],
        }

        # Costruisci info moduli
        all_modules = ModuleService.get_available_modules()

        for mod in all_modules:
            module_info = {
                "id": mod.module_id,
                "name": mod.name,
                "description": mod.description,
                "category": mod.category,
                "icon": mod.icon,
                "is_enabled": mod.module_id in enabled_ids,
                "is_free": mod.is_free,
                "price": float(mod.price) if mod.price else None,
                "plan_required": mod.plan_required,
            }
            result["available_modules"].append(module_info)

            # Se abilitato, aggiungi al menu
            if mod.module_id in enabled_ids:
                # Get plugin menu items
                plugin = ModuleRegistry.get(mod.module_id)
                if plugin and hasattr(plugin, "get_menu_items"):
                    try:
                        items = plugin.get_menu_items(tenant_id)
                        result["menu"].extend(items)
                    except Exception as e:
                        print(f"Error getting menu items for {mod.module_id}: {e}")

                # Get plugin widgets
                if plugin and hasattr(plugin, "get_widgets"):
                    try:
                        w = plugin.get_widgets(tenant_id)
                        result["widgets"].extend(w)
                    except Exception as e:
                        print(f"Error getting widgets for {mod.module_id}: {e}")

        # Ordina menu per position
        result["menu"].sort(key=lambda x: x.get("menu_position", 100))

        return result


@blp.route("/check-module/<string:module_id>")
class CheckModule(MethodView):
    @blp.response(200)
    @jwt_required()
    def get(self, module_id):
        """
        Verifica se un modulo è abilitato per il tenant corrente.
        """
        user = User.query.get(get_jwt_identity())

        is_enabled = TenantModuleService.is_module_enabled(user.tenant_id, module_id)

        return {"module_id": module_id, "is_enabled": is_enabled}
