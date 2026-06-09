import time
import json
from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity

from backend.extensions import db
from backend.models import Report, ReportExecution

blp = Blueprint("report_designer", __name__, description="Report Designer API")


KNOWN_SOURCES = {
    "products": {"table": "products", "label": "Prodotti", "columns": ["id", "name", "code", "sku", "barcode", "unit_price", "category", "is_active", "current_stock", "unit_of_measure"]},
    "sales_orders": {"table": "sales_orders", "label": "Ordini Vendita", "columns": ["id", "number", "order_date", "total_amount", "status", "soggetto_id"]},
    "purchase_orders": {"table": "purchase_orders", "label": "Ordini Acquisto", "columns": ["id", "order_number", "order_date", "total_amount", "status", "soggetto_id"]},
    "soggetti": {"table": "soggetti", "label": "Soggetti", "columns": ["id", "nome", "cognome", "ragione_sociale", "codice_fiscale", "partita_iva", "tipo_soggetto"]},
    "invoices": {"table": "invoices", "label": "Fatture", "columns": ["id", "number", "invoice_date", "total", "status", "soggetto_id"]},
    "inventory_stock": {"table": "product_stock", "label": "Giacenze", "columns": ["id", "product_id", "quantity", "location_id"]},
    "business_projects": {"table": "business_projects", "label": "Progetti", "columns": ["id", "code", "name", "status", "budget_amount", "estimated_hours", "start_date", "end_date"]},
    "timesheets": {"table": "timesheets", "label": "Timesheet", "columns": ["id", "employee_id", "date", "status", "notes"]},
    "production_orders": {"table": "production_orders", "label": "ODP", "columns": ["id", "number", "product_id", "quantity", "quantity_produced", "status", "planned_start_date", "planned_end_date"]},
}


def report_to_dict(r):
    return {
        "id": r.id, "tenant_id": r.tenant_id, "code": r.code, "name": r.name,
        "description": r.description, "category": r.category, "report_type": r.report_type,
        "config": r.config, "is_public": r.is_public, "owner_id": r.owner_id,
        "created_at": r.created_at.isoformat() if r.created_at else None,
        "updated_at": r.updated_at.isoformat() if r.updated_at else None,
    }


# ========== Sources (discovery) ==========

@blp.route("/api/v1/report-designer/sources")
class ReportSources(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        return [{"key": k, "label": v["label"], "columns": v["columns"]} for k, v in KNOWN_SOURCES.items()]


# ========== Reports CRUD ==========

@blp.route("/api/v1/report-designer/reports")
class ReportList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        category = request.args.get("category")
        q = Report.query.filter_by(tenant_id=tenant_id, deleted_at=None)
        if category: q = q.filter_by(category=category)
        return [report_to_dict(r) for r in q.order_by(Report.created_at.desc()).all()]

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        data = request.get_json() or {}
        if not data.get("code") or not data.get("name"):
            abort(400, message="code and name are required")
        r = Report(tenant_id=tenant_id, **{k: v for k, v in data.items() if k in (
            "code", "name", "description", "category", "report_type", "config", "is_public", "owner_id")})
        db.session.add(r)
        db.session.commit()
        return report_to_dict(r), 201


@blp.route("/api/v1/report-designer/reports/<int:report_id>")
class ReportDetail(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, report_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        r = Report.query.filter_by(id=report_id, tenant_id=tenant_id, deleted_at=None).first()
        if not r: abort(404)
        return report_to_dict(r)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def put(self, report_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        r = Report.query.filter_by(id=report_id, tenant_id=tenant_id, deleted_at=None).first()
        if not r: abort(404)
        for f in ("name", "description", "category", "report_type", "config", "is_public"):
            if f in request.get_json(): setattr(r, f, request.get_json()[f])
        db.session.commit()
        return report_to_dict(r)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def delete(self, report_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        r = Report.query.filter_by(id=report_id, tenant_id=tenant_id, deleted_at=None).first()
        if not r: abort(404)
        db.session.delete(r)
        db.session.commit()
        return {"message": "Deleted"}, 204


# ========== Execution ==========

@blp.route("/api/v1/report-designer/reports/<int:report_id>/execute")
class ReportExecute(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self, report_id):
        from datetime import datetime
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        r = Report.query.filter_by(id=report_id, tenant_id=tenant_id, deleted_at=None).first()
        if not r: abort(404)

        config = (r.config or {}) if isinstance(r.config, dict) else {}
        params = request.get_json() or {}
        override_filters = params.get("filters")

        start = time.time()
        try:
            source_key = config.get("source")
            if not source_key or source_key not in KNOWN_SOURCES:
                abort(400, message=f"Unknown source: {source_key}")

            source = KNOWN_SOURCES[source_key]
            table_name = source["table"]
            columns = config.get("columns", source["columns"])
            filters = override_filters or config.get("filters", [])
            order_by = config.get("order_by")
            limit = config.get("limit", 500)
            group_by = config.get("group_by")

            # Build SQL safely using SQLAlchemy text
            col_exprs = []
            table = db.Table(table_name, db.MetaData(), autoload_with=db.engine, keep_existing=True)

            if group_by:
                for g in group_by:
                    col_exprs.append(table.columns.get(g))
                for col in columns:
                    col_exprs.append(table.columns.get(col))
            else:
                for col in columns:
                    col_exprs.append(table.columns.get(col))

            col_exprs = [c for c in col_exprs if c is not None]
            if not col_exprs:
                abort(400, message="No valid columns selected")

            query = db.select(col_exprs)

            # Apply filters
            for f in filters:
                field = f.get("field")
                operator = f.get("operator", "eq")
                value = f.get("value")
                col = table.columns.get(field)
                if col:
                    if operator == "eq":
                        query = query.where(col == value)
                    elif operator == "neq":
                        query = query.where(col != value)
                    elif operator == "gt":
                        query = query.where(col > value)
                    elif operator == "gte":
                        query = query.where(col >= value)
                    elif operator == "lt":
                        query = query.where(col < value)
                    elif operator == "lte":
                        query = query.where(col <= value)
                    elif operator == "like":
                        query = query.where(col.like(f"%{value}%"))
                    elif operator == "in":
                        query = query.where(col.in_(value if isinstance(value, list) else [value]))
                    elif operator == "is_null":
                        query = query.where(col.is_(None))
                    elif operator == "is_not_null":
                        query = query.where(col.isnot(None))

            if group_by:
                for g in group_by:
                    col = table.columns.get(g)
                    if col: query = query.group_by(col)

            if order_by:
                for ob in (order_by if isinstance(order_by, list) else [order_by]):
                    field = ob.get("field") if isinstance(ob, dict) else ob
                    direction = ob.get("direction", "asc") if isinstance(ob, dict) else "asc"
                    col = table.columns.get(field)
                    if col:
                        query = query.order_by(col.asc() if direction == "asc" else col.desc())

            query = query.limit(limit)

            result = db.session.execute(query).fetchall()
            rows = [dict(zip(columns, row)) for row in result]
            elapsed = int((time.time() - start) * 1000)

            # Save execution log
            exec_log = ReportExecution(
                tenant_id=tenant_id, report_id=r.id,
                parameters=params, row_count=len(rows),
                execution_time_ms=elapsed, status="completed",
            )
            db.session.add(exec_log)
            db.session.commit()

            return {
                "data": rows,
                "row_count": len(rows),
                "execution_time_ms": elapsed,
                "columns": columns,
            }

        except Exception as e:
            elapsed = int((time.time() - start) * 1000)
            exec_log = ReportExecution(
                tenant_id=tenant_id, report_id=r.id,
                parameters=params, row_count=0,
                execution_time_ms=elapsed, status="failed",
                error_message=str(e),
            )
            db.session.add(exec_log)
            db.session.commit()
            abort(500, message=str(e))


# ========== Execution History ==========

@blp.route("/api/v1/report-designer/reports/<int:report_id>/history")
class ReportExecutionHistory(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, report_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        r = Report.query.filter_by(id=report_id, tenant_id=tenant_id, deleted_at=None).first()
        if not r: abort(404)
        executions = ReportExecution.query.filter_by(report_id=r.id, tenant_id=tenant_id)\
            .order_by(ReportExecution.created_at.desc()).limit(20).all()
        return [{
            "id": e.id, "parameters": e.parameters, "row_count": e.row_count,
            "execution_time_ms": e.execution_time_ms, "status": e.status,
            "error_message": e.error_message,
            "created_at": e.created_at.isoformat() if e.created_at else None,
        } for e in executions]
