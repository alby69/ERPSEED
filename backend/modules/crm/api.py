from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required

from backend.extensions import db
from backend.models import Lead, Opportunity

blp = Blueprint("crm", __name__, description="CRM API")


def lead_to_dict(l):
    return {
        "id": l.id, "tenant_id": l.tenant_id,
        "first_name": l.first_name, "last_name": l.last_name,
        "company": l.company, "email": l.email, "phone": l.phone,
        "source": l.source, "status": l.status, "notes": l.notes,
        "assigned_to": l.assigned_to,
        "created_at": l.created_at.isoformat() if l.created_at else None,
        "updated_at": l.updated_at.isoformat() if l.updated_at else None,
    }


def opp_to_dict(o):
    return {
        "id": o.id, "tenant_id": o.tenant_id,
        "lead_id": o.lead_id, "name": o.name, "party_id": o.party_id,
        "expected_revenue": o.expected_revenue, "probability": o.probability,
        "stage": o.stage,
        "expected_close_date": o.expected_close_date.isoformat() if o.expected_close_date else None,
        "notes": o.notes, "assigned_to": o.assigned_to,
        "created_at": o.created_at.isoformat() if o.created_at else None,
        "updated_at": o.updated_at.isoformat() if o.updated_at else None,
    }


# ========== Leads ==========

@blp.route("/api/v1/crm/leads")
class LeadList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        status = request.args.get("status")
        query = Lead.query.filter_by(tenant_id=tenant_id, deleted_at=None)
        if status:
            query = query.filter_by(status=status)
        query = query.order_by(Lead.id.desc())
        return [lead_to_dict(l) for l in query.all()]

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        data = request.get_json() or {}
        if not data.get("first_name") or not data.get("last_name"):
            abort(400, message="first_name and last_name are required")
        l = Lead(
            tenant_id=tenant_id,
            first_name=data["first_name"], last_name=data["last_name"],
            company=data.get("company"), email=data.get("email"),
            phone=data.get("phone"), source=data.get("source"),
            status=data.get("status", "new"), notes=data.get("notes"),
            assigned_to=data.get("assigned_to"),
        )
        db.session.add(l)
        db.session.commit()
        return lead_to_dict(l), 201


@blp.route("/api/v1/crm/leads/<int:lead_id>")
class LeadDetail(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, lead_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        l = Lead.query.filter_by(id=lead_id, tenant_id=tenant_id, deleted_at=None).first()
        if not l: abort(404, message="Lead not found")
        return lead_to_dict(l)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def put(self, lead_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        l = Lead.query.filter_by(id=lead_id, tenant_id=tenant_id, deleted_at=None).first()
        if not l: abort(404, message="Lead not found")
        for f in ("first_name", "last_name", "company", "email", "phone", "source", "status", "notes", "assigned_to"):
            if f in request.get_json():
                setattr(l, f, request.get_json()[f])
        db.session.commit()
        return lead_to_dict(l)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def delete(self, lead_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        l = Lead.query.filter_by(id=lead_id, tenant_id=tenant_id, deleted_at=None).first()
        if not l: abort(404, message="Lead not found")
        db.session.delete(l)
        db.session.commit()
        return {"message": "Deleted"}, 204


# ========== Opportunities ==========

@blp.route("/api/v1/crm/opportunities")
class OpportunityList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        stage = request.args.get("stage")
        query = Opportunity.query.filter_by(tenant_id=tenant_id, deleted_at=None)
        if stage:
            query = query.filter_by(stage=stage)
        query = query.order_by(Opportunity.id.desc())
        return [opp_to_dict(o) for o in query.all()]

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        data = request.get_json() or {}
        if not data.get("name"):
            abort(400, message="name is required")
        o = Opportunity(
            tenant_id=tenant_id,
            lead_id=data.get("lead_id"), name=data["name"],
            party_id=data.get("party_id"),
            expected_revenue=float(data.get("expected_revenue", 0)),
            probability=int(data.get("probability", 0)),
            stage=data.get("stage", "qualification"),
            expected_close_date=data.get("expected_close_date"),
            notes=data.get("notes"), assigned_to=data.get("assigned_to"),
        )
        db.session.add(o)
        db.session.commit()
        return opp_to_dict(o), 201


@blp.route("/api/v1/crm/opportunities/<int:opp_id>")
class OpportunityDetail(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, opp_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        o = Opportunity.query.filter_by(id=opp_id, tenant_id=tenant_id, deleted_at=None).first()
        if not o: abort(404, message="Opportunity not found")
        return opp_to_dict(o)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def put(self, opp_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        o = Opportunity.query.filter_by(id=opp_id, tenant_id=tenant_id, deleted_at=None).first()
        if not o: abort(404, message="Opportunity not found")
        for f in ("name", "expected_revenue", "probability", "stage", "expected_close_date", "notes", "assigned_to"):
            if f in request.get_json():
                setattr(o, f, request.get_json()[f])
        db.session.commit()
        return opp_to_dict(o)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def delete(self, opp_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        o = Opportunity.query.filter_by(id=opp_id, tenant_id=tenant_id, deleted_at=None).first()
        if not o: abort(404, message="Opportunity not found")
        db.session.delete(o)
        db.session.commit()
        return {"message": "Deleted"}, 204


@blp.route("/api/v1/crm/pipeline-summary")
class PipelineSummary(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        stages = ["qualification", "proposal", "negotiation", "won", "lost"]
        result = []
        for stage in stages:
            opps = Opportunity.query.filter_by(tenant_id=tenant_id, stage=stage, deleted_at=None).all()
            result.append({
                "stage": stage,
                "count": len(opps),
                "total_revenue": sum(o.expected_revenue for o in opps),
            })
        return result
