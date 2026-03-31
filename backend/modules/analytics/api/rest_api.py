from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from sqlalchemy import select, func, desc
import json

from backend.models import SysChart, SysDashboard, SysModel, ChartLibraryConfig
from backend.extensions import db
from backend.core.schemas.schemas import SysChartSchema, SysDashboardSchema, ChartLibraryConfigSchema
from backend.core.utils.utils import get_table_object
from backend.modules.dynamic_api.service import get_dynamic_api_service as DynamicApiService
from backend.core.services.generic_service import generic_service
from backend.core.utils.utils import paginate, serialize_value
from backend.modules.analytics.service import get_analytics_service

dynamic_service = DynamicApiService()

blp = Blueprint("analytics", __name__, description="BI & Analytics Operations")


def get_analytics_svc():
    from backend.modules.analytics.service.api import AnalyticsService
    return AnalyticsService()


# --- CRUD per Chart Libraries ---
@blp.route("/chart-libraries")
class ChartLibraryList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, ChartLibraryConfigSchema(many=True))
    def get(self):
        """Lista tutte le librerie grafiche configurate."""
        result = get_analytics_svc().execute({"command": "ListChartLibraries"})
        if not result.get("success"):
            return []
        return result["data"]["items"]

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(ChartLibraryConfigSchema)
    @blp.response(201, ChartLibraryConfigSchema)
    def post(self, library_data):
        """Crea o aggiorna configurazione libreria."""
        payload = dict(library_data) if hasattr(library_data, 'items') else library_data
        result = get_analytics_svc().execute({
            "command": "CreateChartLibrary",
            **payload
        })
        
        if not result.get("success"):
            abort(400, message=result.get("error", "Failed to create chart library"))

        return result["data"], 201


@blp.route("/chart-libraries/<int:library_id>")
class ChartLibraryResource(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, ChartLibraryConfigSchema)
    def get(self, library_id):
        result = get_analytics_svc().execute({"command": "GetChartLibrary", "entity_id": library_id})
        if not result.get("success"):
            abort(404, message=result.get("error", "Chart library not found"))
        return result["data"]

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(ChartLibraryConfigSchema)
    @blp.response(200, ChartLibraryConfigSchema)
    def put(self, library_data, library_id):
        payload = dict(library_data) if hasattr(library_data, 'items') else library_data
        result = get_analytics_svc().execute({
            "command": "UpdateChartLibrary",
            "entity_id": library_id,
            **payload
        })
        if not result.get("success"):
            abort(404, message=result.get("error", "Chart library not found"))
        return result["data"]

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(204)
    def delete(self, library_id):
        result = get_analytics_svc().execute({"command": "DeleteChartLibrary", "entity_id": library_id})
        if not result.get("success"):
            abort(404, message=result.get("error", "Chart library not found"))
        return ""


@blp.route("/chart-libraries/default")
class ChartLibraryDefault(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, ChartLibraryConfigSchema)
    def get(self):
        """Restituisce la libreria grafica predefinita."""
        default_lib = ChartLibraryConfig.query.filter_by(is_default=True).first()
        if not default_lib:
            return {"library_name": "chartjs", "is_default": True, "is_active": True}
        return default_lib


# --- CRUD per Grafici ---
@blp.route("/sys-charts")
class SysChartList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, SysChartSchema(many=True))
    def get(self):
        result = get_analytics_svc().execute({"command": "ListCharts"})
        if not result.get("success"):
            return []
        return result["data"]["items"]

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(SysChartSchema)
    @blp.response(201, SysChartSchema)
    def post(self, chart_data):
        payload = dict(chart_data) if hasattr(chart_data, 'items') else chart_data
        result = get_analytics_svc().execute({
            "command": "CreateChart",
            **payload
        })

        if not result.get("success"):
            abort(400, message=result.get("error", "Failed to create chart"))

        return result["data"], 201


@blp.route("/sys-charts/<int:chart_id>")
class SysChartResource(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, SysChartSchema)
    def get(self, chart_id):
        result = get_analytics_svc().execute({"command": "GetChart", "entity_id": chart_id})
        if not result.get("success"):
            abort(404, message=result.get("error", "Chart not found"))
        return result["data"]

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(SysChartSchema)
    @blp.response(200, SysChartSchema)
    def put(self, chart_data, chart_id):
        payload = dict(chart_data) if hasattr(chart_data, 'items') else chart_data
        result = get_analytics_svc().execute({
            "command": "UpdateChart",
            "entity_id": chart_id,
            **payload
        })
        if not result.get("success"):
            abort(404, message=result.get("error", "Chart not found"))
        return result["data"]

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(204)
    def delete(self, chart_id):
        result = get_analytics_svc().execute({"command": "DeleteChart", "entity_id": chart_id})
        if not result.get("success"):
            abort(404, message=result.get("error", "Chart not found"))
        return ""


# --- CRUD per Dashboard ---
@blp.route("/sys-dashboards")
class SysDashboardList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, SysDashboardSchema(many=True))
    def get(self):
        try:
            query = SysDashboard.query
            items, headers = paginate(query)
            return items, 200, headers
        except Exception as e:
            import logging

            logging.warning(f"Dashboard query failed (returning empty list): {e}")
            return [], 200, {}

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(SysDashboardSchema)
    @blp.response(201, SysDashboardSchema)
    def post(self, dashboard_data):
        return generic_service.create_resource(SysDashboard, dashboard_data)


@blp.route("/sys-dashboards/<int:dashboard_id>")
class SysDashboardResource(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, SysDashboardSchema)
    def get(self, dashboard_id):
        return generic_service.get_resource(
            SysDashboard, dashboard_id, not_found_message="Dashboard not found"
        )

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(SysDashboardSchema)
    @blp.response(200, SysDashboardSchema)
    def put(self, dashboard_data, dashboard_id):
        return generic_service.update_resource(
            SysDashboard, dashboard_id, dashboard_data, not_found_message="Dashboard not found"
        )


# --- Motore di Query Analytics ---
@blp.route("/analytics/chart-data/<int:chart_id>")
class ChartData(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, {"type": "object"})
    def get(self, chart_id):
        """Esegue la query di aggregazione per un grafico specifico."""
        chart = SysChart.query.get_or_404(chart_id)

        # Recupera il modello sorgente
        sys_model = SysModel.query.get(chart.model_id)
        if not sys_model:
            abort(404, message="Source model not found")

        # Verifica permessi di lettura sul modello dati
        dynamic_service.check_permissions(sys_model, "read")

        schema_name = f"project_{sys_model.project_id}"
        table = get_table_object(sys_model.name, schema=schema_name)

        # --- Helper per filtri data ---
        def apply_date_filter(q):
            date_from = request.args.get("date_from")
            date_to = request.args.get("date_to")

            date_col = None
            if "date" in table.c:
                date_col = table.c.date
            elif "created_at" in table.c:
                date_col = table.c.created_at

            if date_col is not None:
                if date_from:
                    q = q.where(date_col >= date_from)
                if date_to:
                    q = q.where(func.date(date_col) <= date_to)
            return q

        # --- Helper per filtri dinamici ---
        def apply_dynamic_filters(q):
            for key, value in request.args.items():
                if key.startswith("filter_"):
                    field_name = key[7:]
                    if field_name in table.c and value:
                        q = q.where(table.c[field_name] == value)
            return q

        # Gestione Widget Tabella (Ultimi N record)
        if chart.type == "table":
            query = select(table)

            # Filtri e Limite
            limit = 5
            if chart.filters:
                try:
                    filters = json.loads(chart.filters)
                    limit = int(filters.get("limit", 5))
                    for k, v in filters.items():
                        if k in table.c:
                            query = query.where(table.c[k] == v)
                except:
                    pass

            # Applica filtro data globale
            query = apply_date_filter(query)

            # Applica filtri dinamici
            query = apply_dynamic_filters(query)

            # Ordinamento (Usa x_axis come campo di ordinamento, default id desc)
            sort_col = table.c.id
            if chart.x_axis and chart.x_axis in table.c:
                sort_col = table.c[chart.x_axis]

            query = query.order_by(desc(sort_col)).limit(limit)
            results = db.session.execute(query).mappings().all()

            # Serializza i risultati (gestione date, ecc. è automatica con flask jsonify solitamente, ma per sicurezza convertiamo in dict)
            data = []
            for row in results:
                row_dict = {k: serialize_value(v) for k, v in dict(row).items()}
                data.append(row_dict)

            # Restituisce struttura specifica per tabella
            return {"type": "table", "data": data, "columns": [c.name for c in table.c]}

        # Determina la funzione di aggregazione
        agg_func = None
        if chart.aggregation == "sum":
            agg_func = func.sum
        elif chart.aggregation == "avg":
            agg_func = func.avg
        elif chart.aggregation == "min":
            agg_func = func.min
        elif chart.aggregation == "max":
            agg_func = func.max
        elif chart.aggregation == "count":
            agg_func = func.count
        else:
            agg_func = func.count  # Default

        # Costruisci la query: SELECT x_axis, AGG(y_axis) FROM table GROUP BY x_axis
        x_col = table.c[chart.x_axis]
        y_col = (
            table.c[chart.y_axis] if chart.y_axis != "*" else table.c.id
        )  # Count * fallback

        query = select(x_col.label("label"), agg_func(y_col).label("value"))

        # Applica filtri salvati (se presenti)
        if chart.filters:
            try:
                filters = json.loads(chart.filters)
                for k, v in filters.items():
                    if k in table.c:
                        query = query.where(table.c[k] == v)
            except:
                pass

        # Applica filtro data globale
        query = apply_date_filter(query)

        # Applica filtri dinamici
        query = apply_dynamic_filters(query)

        query = query.group_by(x_col).order_by(desc("value"))

        results = db.session.execute(query).mappings().all()

        # Formatta per il frontend (es. Chart.js)
        return {
            "labels": [str(r["label"]) for r in results],
            "datasets": [
                {
                    "label": f"{chart.aggregation.upper()} of {chart.y_axis}",
                    "data": [
                        float(r["value"]) if r["value"] is not None else 0
                        for r in results
                    ],
                }
            ],
        }
