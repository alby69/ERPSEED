from datetime import date, datetime
from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required

from backend.extensions import db
from backend.models import VatRegisterEntry, VatLiquidation, IntrastatDeclaration, TaxRate, Invoice

blp = Blueprint("vat", __name__, description="VAT & Intrastat API")


# ========== Helpers ==========

def entry_to_dict(e):
    return {
        "id": e.id, "register_type": e.register_type,
        "entry_number": e.entry_number, "entry_date": e.entry_date.isoformat() if e.entry_date else None,
        "document_number": e.document_number, "document_date": e.document_date.isoformat() if e.document_date else None,
        "soggetto_id": e.soggetto_id, "soggetto_name": e.soggetto_name, "soggetto_vat": e.soggetto_vat,
        "invoice_id": e.invoice_id,
        "taxable_amount": e.taxable_amount, "vat_amount": e.vat_amount,
        "vat_rate": e.vat_rate, "vat_code": e.vat_code, "tax_nature": e.tax_nature,
        "fiscal_year": e.fiscal_year, "period": e.period,
        "is_liquidation": e.is_liquidation, "notes": e.notes,
        "created_at": e.created_at.isoformat() if e.created_at else None,
    }

def liquidation_to_dict(l):
    return {
        "id": l.id, "fiscal_year": l.fiscal_year, "period": l.period, "type": l.type,
        "sales_taxable": l.sales_taxable, "sales_vat": l.sales_vat,
        "purchases_taxable": l.purchases_taxable, "purchases_vat": l.purchases_vat,
        "net_vat": l.net_vat, "previous_credit": l.previous_credit,
        "to_pay": l.to_pay, "to_credit": l.to_credit,
        "status": l.status, "notes": l.notes,
        "computed_at": l.computed_at.isoformat() if l.computed_at else None,
        "paid_at": l.paid_at.isoformat() if l.paid_at else None,
        "created_at": l.created_at.isoformat() if l.created_at else None,
    }

def intrastat_to_dict(d):
    return {
        "id": d.id, "fiscal_year": d.fiscal_year, "period": d.period,
        "type": d.type, "is_quarterly": d.is_quarterly,
        "soggetto_id": d.soggetto_id, "soggetto_partita_iva": d.soggetto_partita_iva,
        "soggetto_nazione": d.soggetto_nazione,
        "amount": d.amount, "vat_amount": d.vat_amount, "nature": d.nature,
        "delivery_terms": d.delivery_terms, "transport": d.transport, "notes": d.notes,
        "status": d.status, "submitted_at": d.submitted_at.isoformat() if d.submitted_at else None,
        "created_at": d.created_at.isoformat() if d.created_at else None,
    }


# ========== VAT Register ==========

@blp.route("/api/v1/vat/register")
class VatRegisterList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        register_type = request.args.get("register_type", "sales")
        period = request.args.get("period")
        fiscal_year = request.args.get("fiscal_year", type=int)
        q = VatRegisterEntry.query.filter_by(
            tenant_id=tenant_id, deleted_at=None, register_type=register_type)
        if period: q = q.filter_by(period=period)
        if fiscal_year: q = q.filter_by(fiscal_year=fiscal_year)
        return [entry_to_dict(e) for e in q.order_by(VatRegisterEntry.entry_number.asc()).all()]

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        data = request.get_json() or {}
        if not data.get("register_type") or not data.get("entry_date"):
            abort(400, message="register_type and entry_date are required")

        entry_date = data["entry_date"]
        if isinstance(entry_date, str): entry_date = date.fromisoformat(entry_date)
        fiscal_year = data.get("fiscal_year", entry_date.year)
        period = data.get("period", entry_date.strftime("%Y-%m"))
        register_type = data["register_type"]

        # Auto-number
        last = VatRegisterEntry.query.filter_by(
            tenant_id=tenant_id, register_type=register_type, fiscal_year=fiscal_year
        ).order_by(VatRegisterEntry.entry_number.desc()).first()
        entry_number = (last.entry_number + 1) if last else 1

        e = VatRegisterEntry(
            tenant_id=tenant_id, entry_number=entry_number,
            fiscal_year=fiscal_year, period=period,
            **{k: v for k, v in data.items() if k in (
                "register_type", "entry_date", "document_number", "document_date",
                "soggetto_id", "soggetto_name", "soggetto_vat", "invoice_id",
                "taxable_amount", "vat_amount", "vat_rate", "vat_code", "tax_nature",
                "is_liquidation", "notes")})
        db.session.add(e)
        db.session.commit()
        return entry_to_dict(e), 201


@blp.route("/api/v1/vat/register/<int:entry_id>")
class VatRegisterEntryDetail(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, entry_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        e = VatRegisterEntry.query.filter_by(id=entry_id, tenant_id=tenant_id, deleted_at=None).first()
        if not e: abort(404)
        return entry_to_dict(e)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def put(self, entry_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        e = VatRegisterEntry.query.filter_by(id=entry_id, tenant_id=tenant_id, deleted_at=None).first()
        if not e: abort(404)
        for f in ("document_number", "document_date", "soggetto_id", "soggetto_name", "soggetto_vat",
                  "taxable_amount", "vat_amount", "vat_rate", "vat_code", "tax_nature",
                  "is_liquidation", "notes"):
            if f in request.get_json(): setattr(e, f, request.get_json()[f])
        db.session.commit()
        return entry_to_dict(e)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def delete(self, entry_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        e = VatRegisterEntry.query.filter_by(id=entry_id, tenant_id=tenant_id, deleted_at=None).first()
        if not e: abort(404)
        db.session.delete(e)
        db.session.commit()
        return {"message": "Deleted"}, 204


@blp.route("/api/v1/vat/register/generate")
class VatRegisterGenerate(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        """Generate VAT register entries from invoices in a period."""
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        data = request.get_json() or {}
        period = data.get("period")
        register_type = data.get("register_type", "sales")
        if not period: abort(400, message="period (YYYY-MM) is required")

        year = int(period.split("-")[0])
        month = int(period.split("-")[1])

        # Map register type to invoice filters
        invoice_type_map = {"sales": "AR", "purchases": "AP"}
        invoice_type = invoice_type_map.get(register_type)
        if not invoice_type: abort(400, message=f"Unsupported register type: {register_type}")

        invoices = Invoice.query.filter(
            Invoice.tenant_id == tenant_id,
            Invoice.invoice_type == invoice_type,
            db.extract("year", Invoice.date) == year,
            db.extract("month", Invoice.date) == month,
            Invoice.status != "cancelled",
        ).all()

        if not invoices:
            abort(400, message="No invoices found for this period")

        created = 0
        for inv in invoices:
            existing = VatRegisterEntry.query.filter_by(
                tenant_id=tenant_id, register_type=register_type,
                invoice_id=inv.id, deleted_at=None).first()
            if existing: continue

            inv_date = inv.date
            if isinstance(inv_date, str): inv_date = date.fromisoformat(inv_date)

            last = VatRegisterEntry.query.filter_by(
                tenant_id=tenant_id, register_type=register_type, fiscal_year=year
            ).order_by(VatRegisterEntry.entry_number.desc()).first()
            entry_number = (last.entry_number + 1) if last else 1

            entry = VatRegisterEntry(
                tenant_id=tenant_id, register_type=register_type,
                entry_number=entry_number, entry_date=inv_date,
                document_number=inv.invoice_number, document_date=inv_date,
                soggetto_id=inv.party_id,
                invoice_id=inv.id,
                taxable_amount=inv.total - (inv.tax_amount or 0) if inv.total and inv.tax_amount else inv.total or 0,
                vat_amount=inv.tax_amount or 0,
                fiscal_year=year, period=period,
            )
            db.session.add(entry)
            created += 1

        db.session.commit()
        return {"created": created, "period": period, "register_type": register_type}


# ========== VAT Liquidation ==========

@blp.route("/api/v1/vat/liquidations")
class VatLiquidationList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        q = VatLiquidation.query.filter_by(tenant_id=tenant_id)
        return [liquidation_to_dict(l) for l in q.order_by(VatLiquidation.fiscal_year.desc(), VatLiquidation.period.desc()).all()]

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        data = request.get_json() or {}
        if not data.get("period") or not data.get("fiscal_year"):
            abort(400, message="period and fiscal_year are required")

        # Compute from register entries
        period = data["period"]
        fiscal_year = int(data["fiscal_year"])

        sales = db.session.query(
            db.func.coalesce(db.func.sum(VatRegisterEntry.taxable_amount), 0),
            db.func.coalesce(db.func.sum(VatRegisterEntry.vat_amount), 0),
        ).filter(
            VatRegisterEntry.tenant_id == tenant_id,
            VatRegisterEntry.fiscal_year == fiscal_year,
            VatRegisterEntry.period == period,
            VatRegisterEntry.register_type == "sales",
            VatRegisterEntry.deleted_at == None,
        ).first()

        purchases = db.session.query(
            db.func.coalesce(db.func.sum(VatRegisterEntry.taxable_amount), 0),
            db.func.coalesce(db.func.sum(VatRegisterEntry.vat_amount), 0),
        ).filter(
            VatRegisterEntry.tenant_id == tenant_id,
            VatRegisterEntry.fiscal_year == fiscal_year,
            VatRegisterEntry.period == period,
            VatRegisterEntry.register_type == "purchases",
            VatRegisterEntry.deleted_at == None,
        ).first()

        lt = VatLiquidation(
            tenant_id=tenant_id, fiscal_year=fiscal_year, period=period,
            type=data.get("type", "monthly"),
            sales_taxable=float(sales[0]), sales_vat=float(sales[1]),
            purchases_taxable=float(purchases[0]), purchases_vat=float(purchases[1]),
            net_vat=float(sales[1]) - float(purchases[1]),
            previous_credit=float(data.get("previous_credit", 0)),
            to_pay=max(0, float(sales[1]) - float(purchases[1])),
            to_credit=max(0, float(purchases[1]) - float(sales[1])),
            status="computed", computed_at=datetime.utcnow(),
        )
        db.session.add(lt)
        db.session.commit()
        return liquidation_to_dict(lt), 201


@blp.route("/api/v1/vat/liquidations/<int:lid_id>")
class VatLiquidationDetail(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, lid_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        l = VatLiquidation.query.filter_by(id=lid_id, tenant_id=tenant_id).first()
        if not l: abort(404)
        return liquidation_to_dict(l)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def put(self, lid_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        l = VatLiquidation.query.filter_by(id=lid_id, tenant_id=tenant_id).first()
        if not l: abort(404)
        for f in ("previous_credit", "status", "paid_at", "notes", "to_pay", "to_credit"):
            if f in request.get_json(): setattr(l, f, request.get_json()[f])
        db.session.commit()
        return liquidation_to_dict(l)


# ========== Intrastat ==========

@blp.route("/api/v1/vat/intrastat")
class IntrastatList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        fiscal_year = request.args.get("fiscal_year", type=int)
        period = request.args.get("period")
        type_ = request.args.get("type")
        q = IntrastatDeclaration.query.filter_by(tenant_id=tenant_id)
        if fiscal_year: q = q.filter_by(fiscal_year=fiscal_year)
        if period: q = q.filter_by(period=period)
        if type_: q = q.filter_by(type=type_)
        return [intrastat_to_dict(d) for d in q.order_by(IntrastatDeclaration.fiscal_year.desc(), IntrastatDeclaration.period.desc()).all()]

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        data = request.get_json() or {}
        if not data.get("fiscal_year") or not data.get("period") or not data.get("type") or not data.get("soggetto_id"):
            abort(400, message="fiscal_year, period, type, and soggetto_id are required")
        d = IntrastatDeclaration(tenant_id=tenant_id, **{k: v for k, v in data.items() if k in (
            "fiscal_year", "period", "type", "is_quarterly", "soggetto_id",
            "soggetto_partita_iva", "soggetto_nazione", "amount", "vat_amount",
            "nature", "delivery_terms", "transport", "notes", "status")})
        db.session.add(d)
        db.session.commit()
        return intrastat_to_dict(d), 201


@blp.route("/api/v1/vat/intrastat/<int:d_id>")
class IntrastatDetail(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, d_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        d = IntrastatDeclaration.query.filter_by(id=d_id, tenant_id=tenant_id).first()
        if not d: abort(404)
        return intrastat_to_dict(d)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def put(self, d_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        d = IntrastatDeclaration.query.filter_by(id=d_id, tenant_id=tenant_id).first()
        if not d: abort(404)
        for f in ("amount", "vat_amount", "nature", "delivery_terms", "transport", "notes", "status"):
            if f in request.get_json(): setattr(d, f, request.get_json()[f])
        db.session.commit()
        return intrastat_to_dict(d)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def delete(self, d_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        d = IntrastatDeclaration.query.filter_by(id=d_id, tenant_id=tenant_id).first()
        if not d: abort(404)
        db.session.delete(d)
        db.session.commit()
        return {"message": "Deleted"}, 204


@blp.route("/api/v1/vat/intrastat/<int:d_id>/submit")
class IntrastatSubmit(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self, d_id):
        tenant_id = request.headers.get("X-Tenant-ID", 1, type=int)
        d = IntrastatDeclaration.query.filter_by(id=d_id, tenant_id=tenant_id).first()
        if not d: abort(404)
        d.status = "submitted"
        d.submitted_at = datetime.utcnow()
        db.session.commit()
        return intrastat_to_dict(d)
