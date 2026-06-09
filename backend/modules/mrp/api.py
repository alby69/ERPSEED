from datetime import datetime, date
from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required

from backend.extensions import db
from backend.models import (
    MRPRun, MRPSuggestion, Product, ProductStock,
    BillOfMaterial, BOMLine, SalesOrder, SalesOrderLine,
    ProductionOrder, ProductionOrderMaterial,
)

blp = Blueprint("mrp", __name__, description="MRP API")


def mrp_run_to_dict(run):
    return {
        "id": run.id, "run_date": run.run_date.isoformat() if run.run_date else None,
        "status": run.status, "total_suggestions": run.total_suggestions, "notes": run.notes,
        "created_at": run.created_at.isoformat() if run.created_at else None,
    }

def suggestion_to_dict(s):
    return {
        "id": s.id, "mrp_run_id": s.mrp_run_id,
        "product_id": s.product_id, "product_name": s.product.name if s.product else None,
        "suggestion_type": s.suggestion_type,
        "required_quantity": s.required_quantity,
        "available_quantity": s.available_quantity,
        "suggested_quantity": s.suggested_quantity,
        "source": s.source, "source_id": s.source_id,
        "due_date": s.due_date.isoformat() if s.due_date else None,
        "status": s.status,
    }


@blp.route("/api/v1/mrp/runs")
class MRPRunList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        runs = MRPRun.query.filter_by(tenant_id=tenant_id).order_by(MRPRun.run_date.desc()).limit(20).all()
        return [mrp_run_to_dict(r) for r in runs]

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        """Run MRP calculation."""
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        data = request.get_json() or {}

        run = MRPRun(tenant_id=tenant_id, run_date=datetime.utcnow(), status="running",
                     notes=data.get("notes"))
        db.session.add(run)
        db.session.flush()

        try:
            suggestions = []

            # 1. Get demand from sales orders (planned + confirmed)
            sales_orders = SalesOrder.query.filter(
                SalesOrder.tenant_id == tenant_id,
                SalesOrder.status.in_(["draft", "confirmed"]),
                SalesOrder.deleted_at == None,
            ).all()

            for so in sales_orders:
                for sol in (so.lines or []):
                    suggestions.append({
                        "product_id": sol.product_id,
                        "required_quantity": sol.quantity or 1,
                        "source": "sales_order",
                        "source_id": so.id,
                        "due_date": data.get("horizon_date"),
                    })

            # 2. Get demand from production orders (planned + released)
            prod_orders = ProductionOrder.query.filter(
                ProductionOrder.tenant_id == tenant_id,
                ProductionOrder.status.in_(["planned", "released"]),
                ProductionOrder.deleted_at == None,
            ).all()

            for po in prod_orders:
                suggestions.append({
                    "product_id": po.product_id,
                    "required_quantity": po.quantity,
                    "source": "production_order",
                    "source_id": po.id,
                    "due_date": po.planned_start_date,
                })
                # Also demand from BOM materials
                if po.materials:
                    for mat in po.materials:
                        suggestions.append({
                            "product_id": mat.product_id,
                            "required_quantity": mat.required_quantity,
                            "source": "production_order_material",
                            "source_id": po.id,
                            "due_date": po.planned_start_date,
                        })

            # Aggregate by product and compute net requirements
            from collections import defaultdict
            agg = defaultdict(lambda: {"required": 0, "sources": []})
            for s in suggestions:
                pid = s["product_id"]
                agg[pid]["required"] += s["required_quantity"]
                agg[pid]["sources"].append(s)

            created = 0
            for pid, vals in agg.items():
                # Get available stock
                stock = ProductStock.query.filter_by(
                    tenant_id=tenant_id, product_id=pid, deleted_at=None
                ).first()
                available = stock.quantity if stock else 0.0

                required = vals["required"]
                net = required - available
                if net <= 0:
                    continue

                # Determine if purchase or produce (has active BOM?)
                bom = BillOfMaterial.query.filter_by(
                    tenant_id=tenant_id, product_id=pid, status="active", deleted_at=None
                ).first()

                s_type = "produce" if bom else "purchase"

                sug = MRPSuggestion(
                    tenant_id=tenant_id, mrp_run_id=run.id,
                    product_id=pid, suggestion_type=s_type,
                    required_quantity=required, available_quantity=available,
                    suggested_quantity=net,
                    source="mrp_calculation",
                    due_date=data.get("horizon_date"),
                )
                db.session.add(sug)
                created += 1

            run.total_suggestions = created
            run.status = "completed"
            db.session.commit()

            return {
                "run_id": run.id,
                "suggestions_created": created,
                "status": "completed",
            }

        except Exception as e:
            run.status = "failed"
            run.notes = str(e)
            db.session.commit()
            abort(500, message=str(e))


@blp.route("/api/v1/mrp/runs/<int:run_id>")
class MRPRunDetail(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, run_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        run = MRPRun.query.filter_by(id=run_id, tenant_id=tenant_id).first()
        if not run: abort(404)
        result = mrp_run_to_dict(run)
        result["suggestions"] = [suggestion_to_dict(s) for s in (run.suggestions or [])]
        return result


@blp.route("/api/v1/mrp/suggestions/<int:sug_id>")
class MRPSuggestionDetail(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def put(self, sug_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        sug = MRPSuggestion.query.filter_by(id=sug_id, tenant_id=tenant_id).first()
        if not sug: abort(404)
        for f in ("status", "suggested_quantity", "due_date"):
            if f in request.get_json(): setattr(sug, f, request.get_json()[f])
        db.session.commit()
        return suggestion_to_dict(sug)
