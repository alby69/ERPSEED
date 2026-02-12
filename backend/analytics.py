from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from sqlalchemy import select, func, desc
import json

from .models import SysChart, SysDashboard, SysModel
from .extensions import db
from .schemas import SysChartSchema, SysDashboardSchema
from .dynamic_api import get_table_object, check_model_permissions
from .utils import paginate, serialize_value

blp = Blueprint("analytics", __name__, description="BI & Analytics Operations")

# --- CRUD per Grafici ---
@blp.route("/sys-charts")
class SysChartList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, SysChartSchema(many=True))
    def get(self):
        query = SysChart.query
        items, headers = paginate(query)
        return items, 200, headers

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(SysChartSchema)
    @blp.response(201, SysChartSchema)
    def post(self, chart_data):
        chart = SysChart(**chart_data)
        db.session.add(chart)
        db.session.commit()
        return chart

@blp.route("/sys-charts/<int:chart_id>")
class SysChartResource(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, SysChartSchema)
    def get(self, chart_id):
        return SysChart.query.get_or_404(chart_id)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(204)
    def delete(self, chart_id):
        chart = SysChart.query.get_or_404(chart_id)
        db.session.delete(chart)
        db.session.commit()
        return ""

# --- CRUD per Dashboard ---
@blp.route("/sys-dashboards")
class SysDashboardList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, SysDashboardSchema(many=True))
    def get(self):
        query = SysDashboard.query
        items, headers = paginate(query)
        return items, 200, headers

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(SysDashboardSchema)
    @blp.response(201, SysDashboardSchema)
    def post(self, dashboard_data):
        dashboard = SysDashboard(**dashboard_data)
        db.session.add(dashboard)
        db.session.commit()
        return dashboard

@blp.route("/sys-dashboards/<int:dashboard_id>")
class SysDashboardResource(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, SysDashboardSchema)
    def get(self, dashboard_id):
        return SysDashboard.query.get_or_404(dashboard_id)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(SysDashboardSchema)
    @blp.response(200, SysDashboardSchema)
    def put(self, dashboard_data, dashboard_id):
        dashboard = SysDashboard.query.get_or_404(dashboard_id)
        for key, value in dashboard_data.items():
            setattr(dashboard, key, value)
        db.session.commit()
        return dashboard

# --- Motore di Query Analytics ---
@blp.route("/analytics/chart-data/<int:chart_id>")
class ChartData(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, chart_id):
        """Esegue la query di aggregazione per un grafico specifico."""
        chart = SysChart.query.get_or_404(chart_id)
        
        # Recupera il modello sorgente
        sys_model = SysModel.query.get(chart.model_id)
        if not sys_model:
            abort(404, message="Source model not found")
            
        # Verifica permessi di lettura sul modello dati
        check_model_permissions(sys_model, 'read') # project_id is not needed here, check is inside
        
        schema_name = f"project_{sys_model.project_id}"
        table = get_table_object(sys_model.name, schema=schema_name)

        # --- Helper per filtri data ---
        def apply_date_filter(q):
            date_from = request.args.get('date_from')
            date_to = request.args.get('date_to')
            
            date_col = None
            if 'date' in table.c:
                date_col = table.c.date
            elif 'created_at' in table.c:
                date_col = table.c.created_at
            
            if date_col is not None:
                if date_from:
                    q = q.where(date_col >= date_from)
                if date_to:
                    q = q.where(func.date(date_col) <= date_to)
            return q

        # Gestione Widget Tabella (Ultimi N record)
        if chart.type == 'table':
            query = select(table)
            
            # Filtri e Limite
            limit = 5
            if chart.filters:
                try:
                    filters = json.loads(chart.filters)
                    limit = int(filters.get('limit', 5))
                    for k, v in filters.items():
                        if k in table.c:
                            query = query.where(table.c[k] == v)
                except:
                    pass
            
            # Applica filtro data globale
            query = apply_date_filter(query)
            
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
        if chart.aggregation == 'sum':
            agg_func = func.sum
        elif chart.aggregation == 'avg':
            agg_func = func.avg
        elif chart.aggregation == 'min':
            agg_func = func.min
        elif chart.aggregation == 'max':
            agg_func = func.max
        elif chart.aggregation == 'count':
            agg_func = func.count
        else:
            agg_func = func.count # Default

        # Costruisci la query: SELECT x_axis, AGG(y_axis) FROM table GROUP BY x_axis
        x_col = table.c[chart.x_axis]
        y_col = table.c[chart.y_axis] if chart.y_axis != '*' else table.c.id # Count * fallback
        
        query = select(x_col.label('label'), agg_func(y_col).label('value'))
        
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

        query = query.group_by(x_col).order_by(desc('value'))
        
        results = db.session.execute(query).mappings().all()
        
        # Formatta per il frontend (es. Chart.js)
        return {
            "labels": [str(r['label']) for r in results],
            "datasets": [{
                "label": f"{chart.aggregation.upper()} of {chart.y_axis}",
                "data": [float(r['value']) if r['value'] is not None else 0 for r in results]
            }]
        }