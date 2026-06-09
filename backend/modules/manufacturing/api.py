from datetime import date
from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required

from backend.extensions import db
from backend.models import BillOfMaterial, BOMLine, WorkCycle, WorkPhase, ProductionOrder, ProductionOrderMaterial, Product

blp = Blueprint("manufacturing", __name__, description="Manufacturing API")


# --- helpers ---

def bom_to_dict(bom):
    return {
        "id": bom.id, "tenant_id": bom.tenant_id, "product_id": bom.product_id,
        "code": bom.code, "name": bom.name, "version": bom.version,
        "status": bom.status, "total_quantity": bom.total_quantity, "notes": bom.notes,
        "lines": [{
            "id": l.id, "product_id": l.product_id, "product_name": l.product.name if l.product else None,
            "quantity": l.quantity, "unit_of_measure": l.unit_of_measure,
            "scrap_percentage": l.scrap_percentage, "position": l.position, "notes": l.notes,
        } for l in (bom.lines or [])],
        "product_name": bom.product.name if bom.product else None,
        "created_at": bom.created_at.isoformat() if bom.created_at else None,
    }

def work_cycle_to_dict(wc):
    return {
        "id": wc.id, "tenant_id": wc.tenant_id,
        "code": wc.code, "name": wc.name, "description": wc.description,
        "total_setup_time": wc.total_setup_time, "total_run_time": wc.total_run_time,
        "status": wc.status,
        "phases": [{
            "id": p.id, "phase_number": p.phase_number, "name": p.name,
            "description": p.description, "setup_time": p.setup_time,
            "run_time": p.run_time, "machine": p.machine, "resource_type": p.resource_type,
        } for p in (wc.phases or [])],
        "created_at": wc.created_at.isoformat() if wc.created_at else None,
    }

def production_order_to_dict(po):
    return {
        "id": po.id, "tenant_id": po.tenant_id, "number": po.number,
        "product_id": po.product_id, "product_name": po.product.name if po.product else None,
        "bom_id": po.bom_id, "work_cycle_id": po.work_cycle_id,
        "quantity": po.quantity, "quantity_produced": po.quantity_produced,
        "planned_start_date": po.planned_start_date.isoformat() if po.planned_start_date else None,
        "planned_end_date": po.planned_end_date.isoformat() if po.planned_end_date else None,
        "actual_start_date": po.actual_start_date.isoformat() if po.actual_start_date else None,
        "actual_end_date": po.actual_end_date.isoformat() if po.actual_end_date else None,
        "status": po.status, "notes": po.notes,
        "materials": [{
            "id": m.id, "product_id": m.product_id,
            "product_name": m.product.name if m.product else None,
            "required_quantity": m.required_quantity, "consumed_quantity": m.consumed_quantity,
        } for m in (po.materials or [])],
        "created_at": po.created_at.isoformat() if po.created_at else None,
    }

def generate_po_number(tenant_id):
    year = date.today().year
    prefix = f"ODP-{year}"
    last = ProductionOrder.query.filter(
        ProductionOrder.tenant_id == tenant_id,
        ProductionOrder.number.like(f"{prefix}%")
    ).order_by(ProductionOrder.number.desc()).first()
    last_num = int(last.number.split("-")[-1]) + 1 if last else 1
    return f"{prefix}-{last_num:05d}"


# ============== BOM ==============

@blp.route("/api/v1/manufacturing/bom")
class BOMList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        product_id = request.args.get("product_id", type=int)
        status = request.args.get("status")
        q = BillOfMaterial.query.filter_by(tenant_id=tenant_id, deleted_at=None)
        if product_id: q = q.filter_by(product_id=product_id)
        if status: q = q.filter_by(status=status)
        return [bom_to_dict(b) for b in q.order_by(BillOfMaterial.created_at.desc()).all()]

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        data = request.get_json() or {}
        if not data.get("product_id") or not data.get("code"):
            abort(400, message="product_id and code are required")
        lines_data = data.pop("lines", [])
        bom = BillOfMaterial(tenant_id=tenant_id, **{k: v for k, v in data.items() if k in (
            "product_id", "code", "name", "version", "status", "total_quantity", "notes")})
        db.session.add(bom)
        db.session.flush()
        for i, ld in enumerate(lines_data):
            line = BOMLine(tenant_id=tenant_id, bom_id=bom.id,
                           product_id=ld["product_id"], quantity=ld.get("quantity", 1),
                           unit_of_measure=ld.get("unit_of_measure"),
                           scrap_percentage=ld.get("scrap_percentage", 0),
                           position=ld.get("position", i), notes=ld.get("notes"))
            db.session.add(line)
        db.session.commit()
        return bom_to_dict(BillOfMaterial.query.get(bom.id)), 201


@blp.route("/api/v1/manufacturing/bom/<int:bom_id>")
class BOMDetail(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, bom_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        bom = BillOfMaterial.query.filter_by(id=bom_id, tenant_id=tenant_id, deleted_at=None).first()
        if not bom: abort(404)
        return bom_to_dict(bom)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def put(self, bom_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        bom = BillOfMaterial.query.filter_by(id=bom_id, tenant_id=tenant_id, deleted_at=None).first()
        if not bom: abort(404)
        data = request.get_json() or {}
        for f in ("code", "name", "version", "status", "total_quantity", "notes"):
            if f in data: setattr(bom, f, data[f])
        if "lines" in data:
            BOMLine.query.filter_by(bom_id=bom.id).delete()
            for i, ld in enumerate(data["lines"]):
                line = BOMLine(tenant_id=tenant_id, bom_id=bom.id,
                               product_id=ld["product_id"], quantity=ld.get("quantity", 1),
                               unit_of_measure=ld.get("unit_of_measure"),
                               scrap_percentage=ld.get("scrap_percentage", 0),
                               position=ld.get("position", i), notes=ld.get("notes"))
                db.session.add(line)
        db.session.commit()
        return bom_to_dict(BillOfMaterial.query.get(bom.id))

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def delete(self, bom_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        bom = BillOfMaterial.query.filter_by(id=bom_id, tenant_id=tenant_id, deleted_at=None).first()
        if not bom: abort(404)
        db.session.delete(bom)
        db.session.commit()
        return {"message": "Deleted"}, 204


# ============== Work Cycles ==============

@blp.route("/api/v1/manufacturing/work-cycles")
class WorkCycleList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        q = WorkCycle.query.filter_by(tenant_id=tenant_id, deleted_at=None)
        return [work_cycle_to_dict(wc) for wc in q.order_by(WorkCycle.created_at.desc()).all()]

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        data = request.get_json() or {}
        if not data.get("code") or not data.get("name"):
            abort(400, message="code and name are required")
        phases_data = data.pop("phases", [])
        wc = WorkCycle(tenant_id=tenant_id, **{k: v for k, v in data.items() if k in (
            "code", "name", "description", "total_setup_time", "total_run_time", "status")})
        db.session.add(wc)
        db.session.flush()
        for pd in phases_data:
            phase = WorkPhase(tenant_id=tenant_id, work_cycle_id=wc.id,
                              phase_number=pd["phase_number"], name=pd["name"],
                              description=pd.get("description"),
                              setup_time=pd.get("setup_time", 0), run_time=pd.get("run_time", 0),
                              machine=pd.get("machine"), resource_type=pd.get("resource_type"))
            db.session.add(phase)
        db.session.commit()
        return work_cycle_to_dict(WorkCycle.query.get(wc.id)), 201


@blp.route("/api/v1/manufacturing/work-cycles/<int:wc_id>")
class WorkCycleDetail(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, wc_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        wc = WorkCycle.query.filter_by(id=wc_id, tenant_id=tenant_id, deleted_at=None).first()
        if not wc: abort(404)
        return work_cycle_to_dict(wc)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def put(self, wc_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        wc = WorkCycle.query.filter_by(id=wc_id, tenant_id=tenant_id, deleted_at=None).first()
        if not wc: abort(404)
        data = request.get_json() or {}
        for f in ("code", "name", "description", "total_setup_time", "total_run_time", "status"):
            if f in data: setattr(wc, f, data[f])
        if "phases" in data:
            WorkPhase.query.filter_by(work_cycle_id=wc.id).delete()
            for pd in data["phases"]:
                phase = WorkPhase(tenant_id=tenant_id, work_cycle_id=wc.id,
                                  phase_number=pd["phase_number"], name=pd["name"],
                                  description=pd.get("description"),
                                  setup_time=pd.get("setup_time", 0), run_time=pd.get("run_time", 0),
                                  machine=pd.get("machine"), resource_type=pd.get("resource_type"))
                db.session.add(phase)
        db.session.commit()
        return work_cycle_to_dict(WorkCycle.query.get(wc.id))

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def delete(self, wc_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        wc = WorkCycle.query.filter_by(id=wc_id, tenant_id=tenant_id, deleted_at=None).first()
        if not wc: abort(404)
        db.session.delete(wc)
        db.session.commit()
        return {"message": "Deleted"}, 204


# ============== Production Orders ==============

@blp.route("/api/v1/manufacturing/production-orders")
class ProductionOrderList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        status = request.args.get("status")
        q = ProductionOrder.query.filter_by(tenant_id=tenant_id, deleted_at=None)
        if status: q = q.filter_by(status=status)
        return [production_order_to_dict(po) for po in q.order_by(ProductionOrder.created_at.desc()).all()]

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        data = request.get_json() or {}
        if not data.get("product_id") or not data.get("quantity"):
            abort(400, message="product_id and quantity are required")
        materials_data = data.pop("materials", [])
        po = ProductionOrder(
            tenant_id=tenant_id,
            number=generate_po_number(tenant_id),
            **{k: v for k, v in data.items() if k in (
                "product_id", "bom_id", "work_cycle_id", "quantity", "quantity_produced",
                "planned_start_date", "planned_end_date", "notes")})
        db.session.add(po)
        db.session.flush()
        for md in materials_data:
            mat = ProductionOrderMaterial(tenant_id=tenant_id, production_order_id=po.id,
                                          product_id=md["product_id"],
                                          required_quantity=md["required_quantity"],
                                          consumed_quantity=md.get("consumed_quantity", 0))
            db.session.add(mat)
        db.session.commit()
        return production_order_to_dict(ProductionOrder.query.get(po.id)), 201


@blp.route("/api/v1/manufacturing/production-orders/<int:po_id>")
class ProductionOrderDetail(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, po_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        po = ProductionOrder.query.filter_by(id=po_id, tenant_id=tenant_id, deleted_at=None).first()
        if not po: abort(404)
        return production_order_to_dict(po)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def put(self, po_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        po = ProductionOrder.query.filter_by(id=po_id, tenant_id=tenant_id, deleted_at=None).first()
        if not po: abort(404)
        data = request.get_json() or {}
        for f in ("product_id", "bom_id", "work_cycle_id", "quantity", "quantity_produced",
                  "planned_start_date", "planned_end_date", "actual_start_date", "actual_end_date",
                  "status", "notes"):
            if f in data: setattr(po, f, data[f])
        if "materials" in data:
            ProductionOrderMaterial.query.filter_by(production_order_id=po.id).delete()
            for md in data["materials"]:
                mat = ProductionOrderMaterial(tenant_id=tenant_id, production_order_id=po.id,
                                              product_id=md["product_id"],
                                              required_quantity=md["required_quantity"],
                                              consumed_quantity=md.get("consumed_quantity", 0))
                db.session.add(mat)
        db.session.commit()
        return production_order_to_dict(ProductionOrder.query.get(po.id))

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def delete(self, po_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        po = ProductionOrder.query.filter_by(id=po_id, tenant_id=tenant_id, deleted_at=None).first()
        if not po: abort(404)
        db.session.delete(po)
        db.session.commit()
        return {"message": "Deleted"}, 204


# ============== Status transition helpers ==============

@blp.route("/api/v1/manufacturing/production-orders/<int:po_id>/release")
class ProductionOrderRelease(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self, po_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        po = ProductionOrder.query.filter_by(id=po_id, tenant_id=tenant_id, deleted_at=None).first()
        if not po: abort(404)
        if po.status != "planned": abort(400, message="Only planned orders can be released")
        po.status = "released"
        db.session.commit()
        return production_order_to_dict(po)


@blp.route("/api/v1/manufacturing/production-orders/<int:po_id>/start")
class ProductionOrderStart(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self, po_id):
        from datetime import datetime
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        po = ProductionOrder.query.filter_by(id=po_id, tenant_id=tenant_id, deleted_at=None).first()
        if not po: abort(404)
        if po.status not in ("released", "planned"): abort(400, message="Cannot start order in current status")
        po.status = "in_progress"
        po.actual_start_date = datetime.utcnow()
        db.session.commit()
        return production_order_to_dict(po)


@blp.route("/api/v1/manufacturing/production-orders/<int:po_id>/complete")
class ProductionOrderComplete(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self, po_id):
        from datetime import datetime
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        po = ProductionOrder.query.filter_by(id=po_id, tenant_id=tenant_id, deleted_at=None).first()
        if not po: abort(404)
        if po.status != "in_progress": abort(400, message="Only in_progress orders can be completed")
        po.status = "completed"
        po.actual_end_date = datetime.utcnow()
        po.quantity_produced = request.get_json().get("quantity_produced", po.quantity) if request.get_json() else po.quantity
        db.session.commit()
        return production_order_to_dict(po)
