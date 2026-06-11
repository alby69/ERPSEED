from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from datetime import date

from backend.extensions import db
from backend.models import BusinessProject, Timesheet, TimesheetLine

blp = Blueprint("project_management", __name__, description="Project Management API")


# --- helpers ---

def project_to_dict(p):
    return {
        "id": p.id, "tenant_id": p.tenant_id, "code": p.code, "name": p.name,
        "description": p.description, "client_id": p.client_id, "manager_id": p.manager_id,
        "start_date": p.start_date.isoformat() if p.start_date else None,
        "end_date": p.end_date.isoformat() if p.end_date else None,
        "status": p.status,
        "estimated_hours": p.estimated_hours, "budget_amount": p.budget_amount,
        "hourly_rate": p.hourly_rate,
        "created_at": p.created_at.isoformat() if p.created_at else None,
    }

def timesheet_to_dict(t):
    return {
        "id": t.id, "tenant_id": t.tenant_id, "employee_id": t.employee_id,
        "date": t.date.isoformat() if t.date else None,
        "status": t.status, "notes": t.notes,
        "lines": [{
            "id": l.id, "project_id": l.project_id, "hours": l.hours,
            "description": l.description,
        } for l in (t.lines or [])],
        "created_at": t.created_at.isoformat() if t.created_at else None,
    }


# ========== Projects ==========

@blp.route("/api/v1/project-management/projects")
class BusinessProjectList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        status = request.args.get("status")
        q = BusinessProject.query.filter_by(tenant_id=tenant_id, deleted_at=None)
        if status: q = q.filter_by(status=status)
        return [project_to_dict(p) for p in q.order_by(BusinessProject.created_at.desc()).all()]

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        data = request.get_json() or {}
        if not data.get("code") or not data.get("name"):
            abort(400, message="code and name are required")
        p = BusinessProject(tenant_id=tenant_id, **{k: v for k, v in data.items() if k in (
            "code", "name", "description", "client_id", "manager_id", "start_date", "end_date",
            "status", "estimated_hours", "budget_amount", "hourly_rate")})
        db.session.add(p)
        db.session.commit()
        return project_to_dict(p), 201


@blp.route("/api/v1/project-management/projects/<int:project_id>")
class BusinessProjectDetail(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, project_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        p = BusinessProject.query.filter_by(id=project_id, tenant_id=tenant_id, deleted_at=None).first()
        if not p: abort(404)
        return project_to_dict(p)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def put(self, project_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        p = BusinessProject.query.filter_by(id=project_id, tenant_id=tenant_id, deleted_at=None).first()
        if not p: abort(404)
        for f in ("name", "description", "client_id", "manager_id", "start_date", "end_date",
                  "status", "estimated_hours", "budget_amount", "hourly_rate"):
            if f in request.get_json(): setattr(p, f, request.get_json()[f])
        db.session.commit()
        return project_to_dict(p)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def delete(self, project_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        p = BusinessProject.query.filter_by(id=project_id, tenant_id=tenant_id, deleted_at=None).first()
        if not p: abort(404)
        db.session.delete(p)
        db.session.commit()
        return {"message": "Deleted"}, 204


# ========== Timesheets ==========

@blp.route("/api/v1/project-management/timesheets")
class TimesheetList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        employee_id = request.args.get("employee_id", type=int)
        date_from = request.args.get("date_from")
        date_to = request.args.get("date_to")
        status = request.args.get("status")
        q = Timesheet.query.filter_by(tenant_id=tenant_id, deleted_at=None)
        if employee_id: q = q.filter_by(employee_id=employee_id)
        if status: q = q.filter_by(status=status)
        if date_from: q = q.filter(Timesheet.date >= date_from)
        if date_to: q = q.filter(Timesheet.date <= date_to)
        return [timesheet_to_dict(t) for t in q.order_by(Timesheet.date.desc()).all()]

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        data = request.get_json() or {}
        if not data.get("employee_id") or not data.get("date"):
            abort(400, message="employee_id and date are required")
        lines_data = data.pop("lines", [])
        date_val = data.get("date")
        if isinstance(date_val, str):
            from datetime import date as date_cls
            data["date"] = date_cls.fromisoformat(date_val)
        t = Timesheet(tenant_id=tenant_id, **{k: v for k, v in data.items() if k in ("employee_id", "date", "status", "notes")})
        db.session.add(t)
        db.session.flush()
        for ld in lines_data:
            line = TimesheetLine(tenant_id=tenant_id, timesheet_id=t.id,
                                 project_id=ld.get("project_id"),
                                 hours=ld.get("hours", 0), description=ld.get("description"))
            db.session.add(line)
        db.session.commit()
        return timesheet_to_dict(Timesheet.query.get(t.id)), 201


@blp.route("/api/v1/project-management/timesheets/<int:ts_id>")
class TimesheetDetail(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, ts_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        t = Timesheet.query.filter_by(id=ts_id, tenant_id=tenant_id, deleted_at=None).first()
        if not t: abort(404)
        return timesheet_to_dict(t)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def put(self, ts_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        t = Timesheet.query.filter_by(id=ts_id, tenant_id=tenant_id, deleted_at=None).first()
        if not t: abort(404)
        data = request.get_json() or {}
        for f in ("employee_id", "date", "status", "notes"):
            if f in data: setattr(t, f, data[f])
        if "lines" in data:
            TimesheetLine.query.filter_by(timesheet_id=t.id).delete()
            for ld in data["lines"]:
                line = TimesheetLine(tenant_id=tenant_id, timesheet_id=t.id,
                                     project_id=ld.get("project_id"),
                                     hours=ld.get("hours", 0), description=ld.get("description"))
                db.session.add(line)
        db.session.commit()
        return timesheet_to_dict(Timesheet.query.get(t.id))

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def delete(self, ts_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        t = Timesheet.query.filter_by(id=ts_id, tenant_id=tenant_id, deleted_at=None).first()
        if not t: abort(404)
        db.session.delete(t)
        db.session.commit()
        return {"message": "Deleted"}, 204


@blp.route("/api/v1/project-management/timesheets/<int:ts_id>/submit")
class TimesheetSubmit(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self, ts_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        t = Timesheet.query.filter_by(id=ts_id, tenant_id=tenant_id, deleted_at=None).first()
        if not t: abort(404)
        if t.status != "draft": abort(400, message="Only draft timesheets can be submitted")
        t.status = "submitted"
        db.session.commit()
        return timesheet_to_dict(t)


@blp.route("/api/v1/project-management/timesheets/<int:ts_id>/approve")
class TimesheetApprove(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self, ts_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        t = Timesheet.query.filter_by(id=ts_id, tenant_id=tenant_id, deleted_at=None).first()
        if not t: abort(404)
        if t.status != "submitted": abort(400, message="Only submitted timesheets can be approved")
        t.status = "approved"
        db.session.commit()
        return timesheet_to_dict(t)


# ========== Summary ==========

@blp.route("/api/v1/project-management/summary")
class ProjectManagementSummary(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        projects = BusinessProject.query.filter_by(tenant_id=tenant_id, deleted_at=None).all()
        total_budget = sum(p.budget_amount or 0 for p in projects)
        total_hours = sum(p.estimated_hours or 0 for p in projects)
        active = sum(1 for p in projects if p.status == "active")

        timesheets = Timesheet.query.filter_by(tenant_id=tenant_id, deleted_at=None).all()
        logged_hours = db.session.query(db.func.coalesce(db.func.sum(TimesheetLine.hours), 0))\
            .join(Timesheet, TimesheetLine.timesheet_id == Timesheet.id)\
            .filter(Timesheet.tenant_id == tenant_id, Timesheet.deleted_at == None).scalar()

        return {
            "total_projects": len(projects),
            "active_projects": active,
            "total_budget": total_budget,
            "total_estimated_hours": total_hours,
            "total_logged_hours": float(logged_hours or 0),
        }
