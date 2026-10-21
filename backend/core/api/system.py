"""
System API - Endpoints per informazioni di sistema e ricerca globale.
"""

from flask import g
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_smorest import Blueprint

from backend.models import User, SysModel
from backend.core.services.module_service import ModuleService
from backend.core.services.tenant_module_service import TenantModuleService
from backend.plugins.registry import ModuleRegistry

blp = Blueprint("system", __name__, url_prefix="/api/v1/system")
global_blp = Blueprint("global_search", __name__, url_prefix="/api/v1/global")


@blp.route("/modules-info")
class SystemModulesInfo(MethodView):
    @jwt_required()
    def get(self):
        """
        Restituisce informazioni completo moduli per UI.
        Include stato, menu, widget per il tenant corrente.
        """
        user = User.query.get(get_jwt_identity())
        tenant_id = user.tenant_id if user else None

        # Moduli abilitati per tenant
        enabled_ids = set(TenantModuleService.get_enabled_module_ids(tenant_id)) # type: ignore

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
                        items = plugin.get_menu_items(tenant_id) # type: ignore
                        result["menu"].extend(items)
                    except Exception as e:
                        print(f"Error getting menu items for {mod.module_id}: {e}")

                # Get plugin widgets
                if plugin and hasattr(plugin, "get_widgets"):
                    try:
                        w = plugin.get_widgets(tenant_id) # type: ignore
                        result["widgets"].extend(w)
                    except Exception as e:
                        print(f"Error getting widgets for {mod.module_id}: {e}")

        # Ordina menu per position
        result["menu"].sort(key=lambda x: x.get("menu_position", 100))

        return result


@blp.route("/resolve-model/<string:model_name>")
class ResolveModelProject(MethodView):
    @jwt_required()
    def get(self, model_name):
        """
        Returns the project where the given dynamic model is defined.
        Useful for system models (like dashboard_kpi) that may not belong
        to the currently active project.
        """
        model = SysModel.query.filter_by(name=model_name).first()
        if not model:
            return {"found": False, "projectId": None}
        return {"found": True, "projectId": model.projectId}


@blp.route("/check-module/<string:module_id>")
class CheckModule(MethodView):
    @jwt_required()
    def get(self, module_id):
        """
        Verifica se un modulo è abilitato per il tenant corrente.
        """
        user = User.query.get(get_jwt_identity())

        is_enabled = TenantModuleService.is_module_enabled(user.tenant_id if user else None, module_id) # type: ignore

        return {"module_id": module_id, "is_enabled": is_enabled}


@blp.route("/search")
class GlobalSearch(MethodView):
    @jwt_required()
    def get(self):
        """
        Esegue una ricerca globale su Soggetti, Prodotti, Ordini di Vendita e Fatture.
        Restituisce un array di risultati tipizzati.
        """
        from flask import request
        from backend.models import Product, SalesOrder, Soggetto
        try:
            from backend.plugins.accounting.models import Invoice
        except ImportError:
            Invoice = None

        query_str = request.args.get("q", "").strip()
        limit = request.args.get("limit", 10, type=int)

        if not query_str or len(query_str) < 2:
            return {"results": []}

        user = User.query.get(get_jwt_identity())
        tenant_id = user.tenant_id if user else None

        results = []
        search_pattern = f"%{query_str}%"

        # 1. Soggetti
        try:
            soggetti = (
                Soggetto.query.filter(
                    Soggetto.tenant_id == tenant_id,
                    Soggetto.ragione_sociale.ilike(search_pattern),
                )
                .limit(limit)
                .all()
            )
            for s in soggetti:
                results.append(
                    {
                        "type": "subject",
                        "id": s.id,
                        "label": s.ragione_sociale,
                        "url": f"/subjects/{s.id}",
                    }
                )
        except Exception:
            pass

        # 2. Prodotti
        try:
            products = (
                Product.query.filter(
                    Product.tenant_id == tenant_id,
                    (Product.name.ilike(search_pattern) | Product.sku.ilike(search_pattern)),
                )
                .limit(limit)
                .all()
            )
            for p in products:
                results.append(
                    {
                        "type": "product",
                        "id": p.id,
                        "label": f"{p.sku} - {p.name}" if p.sku else p.name,
                        "url": f"/products/{p.id}",
                    }
                )
        except Exception:
            pass

        # 3. Ordini di Vendita
        try:
            orders = (
                SalesOrder.query.filter(
                    SalesOrder.tenant_id == tenant_id,
                    (SalesOrder.number.ilike(search_pattern) | SalesOrder.customer_reference.ilike(search_pattern)),
                )
                .limit(limit)
                .all()
            )
            for o in orders:
                results.append(
                    {
                        "type": "sales_order",
                        "id": o.id,
                        "label": f"Ordine #{o.number or o.id}",
                        "url": f"/sales/orders/{o.id}",
                    }
                )
        except Exception:
            pass

        # 4. Fatture
        if Invoice:
            try:
                invoices = (
                    Invoice.query.filter(
                        Invoice.tenant_id == tenant_id,
                        Invoice.number.ilike(search_pattern),
                    )
                    .limit(limit)
                    .all()
                )
                for inv in invoices:
                    results.append(
                        {
                            "type": "invoice",
                            "id": inv.id,
                            "label": f"Fattura #{inv.number or inv.id}",
                            "url": f"/invoices/{inv.id}",
                        }
                    )
            except Exception:
                pass

        return {"results": results[:limit]}


@global_blp.route("/search")
class GlobalSearchDirect(MethodView):
    @jwt_required()
    def get(self):
        """
        Esegue una ricerca globale tramite l'endpoint dedicato /api/v1/global/search.
        """
        return GlobalSearch().get()
