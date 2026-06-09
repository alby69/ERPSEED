import logging
from datetime import date, datetime
from typing import Optional, List

from backend.extensions import db
from backend.plugins.accounting.models import Invoice, InvoiceLine
from backend.models.sales import SalesOrder, SalesOrderLine

logger = logging.getLogger(__name__)


def _invoice_to_dict(inv) -> dict:
    return {
        "id": inv.id,
        "tenant_id": inv.tenant_id,
        "invoice_number": inv.invoice_number,
        "invoice_type": inv.invoice_type,
        "party_id": inv.party_id,
        "sales_order_id": inv.sales_order_id,
        "date": inv.date.isoformat() if inv.date else None,
        "due_date": inv.due_date.isoformat() if inv.due_date else None,
        "description": inv.description,
        "notes": inv.notes,
        "subtotal": inv.subtotal,
        "tax_amount": inv.tax_amount,
        "total": inv.total,
        "status": inv.status,
        "journal_entry_id": inv.journal_entry_id,
        "created_by": inv.created_by,
        "created_at": inv.created_at.isoformat() if inv.created_at else None,
        "updated_at": inv.updated_at.isoformat() if inv.updated_at else None,
        "lines": [
            {
                "id": l.id, "product_id": l.product_id,
                "description": l.description, "quantity": l.quantity,
                "unit_price": l.unit_price, "discount_percent": l.discount_percent,
                "tax_percent": l.tax_percent, "amount": l.amount,
            }
            for l in inv.lines
        ],
    }


class InvoiceRepository:
    def create(self, invoice_domain) -> dict:
        inv = Invoice(
            tenant_id=invoice_domain.tenant_id,
            invoice_type="AR",
            party_id=invoice_domain.party_id,
            sales_order_id=invoice_domain.sales_order_id,
            date=invoice_domain.date or date.today(),
            due_date=invoice_domain.due_date,
            description=invoice_domain.description,
            notes=invoice_domain.notes,
            subtotal=invoice_domain.subtotal,
            tax_amount=invoice_domain.tax_amount,
            total=invoice_domain.total,
            status="draft",
            created_by=invoice_domain.created_by,
        )
        inv.invoice_number = self._generate_number(inv.tenant_id)
        db.session.add(inv)
        db.session.flush()

        for line_domain in invoice_domain.lines:
            line = InvoiceLine(
                tenant_id=inv.tenant_id,
                invoice_id=inv.id,
                product_id=line_domain.product_id,
                description=line_domain.description,
                quantity=line_domain.quantity,
                unit_price=line_domain.unit_price,
                discount_percent=line_domain.discount_percent,
                tax_percent=line_domain.tax_percent,
                amount=line_domain.total,
            )
            db.session.add(line)

        db.session.commit()
        return _invoice_to_dict(inv)

    def create_from_sales_order(self, tenant_id: int, sales_order_id: int,
                                user_id: Optional[int] = None,
                                invoice_date: Optional[date] = None,
                                due_date: Optional[date] = None,
                                description: str = "", notes: str = "") -> dict:
        so = SalesOrder.query.filter_by(id=sales_order_id, tenant_id=tenant_id).first()
        if not so:
            return {"error": "Sales order not found"}
        if so.status not in ("confirmed", "completed"):
            return {"error": f"Cannot invoice order in status '{so.status}'"}

        existing = Invoice.query.filter_by(tenant_id=tenant_id, sales_order_id=sales_order_id).filter(
            Invoice.status.in_(["draft", "sent"])
        ).first()
        if existing:
            return {"error": f"Order already has an active invoice ({existing.invoice_number})"}

        so_lines = SalesOrderLine.query.filter_by(order_id=sales_order_id).all()
        if not so_lines:
            return {"error": "Sales order has no lines"}

        inv_date = invoice_date or date.today()
        inv = Invoice(
            tenant_id=tenant_id,
            invoice_type="AR",
            party_id=so.customer_id,
            sales_order_id=sales_order_id,
            date=inv_date,
            due_date=due_date,
            description=description or f"Fattura per Ordine {so.number}",
            notes=notes,
            status="draft",
            created_by=user_id,
        )
        inv.invoice_number = self._generate_number(tenant_id)
        db.session.add(inv)
        db.session.flush()

        subtotal = 0.0
        for so_line in so_lines:
            line_total = so_line.quantity * so_line.unit_price
            line = InvoiceLine(
                tenant_id=tenant_id,
                invoice_id=inv.id,
                product_id=so_line.product_id,
                description=so_line.description,
                quantity=so_line.quantity,
                unit_price=so_line.unit_price,
                amount=line_total,
            )
            db.session.add(line)
            subtotal += line_total

        inv.subtotal = subtotal
        inv.total = subtotal
        db.session.commit()
        return _invoice_to_dict(inv)

    def update(self, invoice_id: int, tenant_id: int, data: dict) -> Optional[dict]:
        inv = Invoice.query.filter_by(id=invoice_id, tenant_id=tenant_id, status="draft").first()
        if not inv:
            return None
        for field in ("date", "due_date", "description", "notes"):
            if field in data:
                setattr(inv, field, data[field])
        if "lines" in data:
            InvoiceLine.query.filter_by(invoice_id=inv.id).delete()
            subtotal = 0.0
            for line_data in data["lines"]:
                line = InvoiceLine(
                    tenant_id=tenant_id, invoice_id=inv.id,
                    product_id=line_data.get("product_id"),
                    description=line_data.get("description", ""),
                    quantity=line_data.get("quantity", 1),
                    unit_price=line_data.get("unit_price", 0),
                    discount_percent=line_data.get("discount_percent", 0),
                    tax_percent=line_data.get("tax_percent", 0),
                    amount=0.0,
                )
                subtotal_item = line.quantity * line.unit_price
                discount = subtotal_item * (line.discount_percent / 100)
                taxable = subtotal_item - discount
                tax = taxable * (line.tax_percent / 100)
                line.amount = taxable + tax
                db.session.add(line)
                subtotal += line.amount
            inv.subtotal = subtotal
            inv.tax_amount = sum(
                (l.quantity * l.unit_price * (1 - (l.discount_percent or 0) / 100)) * ((l.tax_percent or 0) / 100)
                for l in inv.lines
            )
            inv.total = inv.subtotal + inv.tax_amount
        db.session.commit()
        return _invoice_to_dict(inv)

    def issue(self, invoice_id: int, tenant_id: int, user_id: Optional[int] = None) -> dict:
        inv = Invoice.query.filter_by(id=invoice_id, tenant_id=tenant_id).first()
        if not inv:
            return {"error": "Invoice not found"}
        if inv.status != "draft":
            return {"error": f"Cannot issue invoice in status '{inv.status}'"}
        inv.status = "sent"
        db.session.commit()
        return _invoice_to_dict(inv)

    def cancel(self, invoice_id: int, tenant_id: int, reason: str = "") -> dict:
        inv = Invoice.query.filter_by(id=invoice_id, tenant_id=tenant_id).first()
        if not inv:
            return {"error": "Invoice not found"}
        if inv.status in ("paid", "cancelled"):
            return {"error": f"Cannot cancel invoice in status '{inv.status}'"}
        inv.status = "cancelled"
        inv.notes = (inv.notes or "") + f"\nAnnullato: {reason}" if reason else ""
        db.session.commit()
        return _invoice_to_dict(inv)

    def mark_paid(self, invoice_id: int, tenant_id: int, amount: float, payment_date: date) -> dict:
        inv = Invoice.query.filter_by(id=invoice_id, tenant_id=tenant_id).first()
        if not inv:
            return {"error": "Invoice not found"}
        if inv.status not in ("sent",):
            return {"error": f"Cannot pay invoice in status '{inv.status}'"}
        inv.status = "paid"
        db.session.commit()
        return _invoice_to_dict(inv)

    def find_by_id(self, invoice_id: int, tenant_id: int) -> Optional[dict]:
        inv = Invoice.query.filter_by(id=invoice_id, tenant_id=tenant_id).first()
        if not inv:
            return None
        return _invoice_to_dict(inv)

    def find_all(self, tenant_id: int, status: Optional[str] = None,
                 party_id: Optional[int] = None, search: Optional[str] = None,
                 page: int = 1, per_page: int = 20) -> dict:
        query = Invoice.query.filter_by(tenant_id=tenant_id)
        if status:
            query = query.filter_by(status=status)
        if party_id:
            query = query.filter_by(party_id=party_id)
        if search:
            q = f"%{search}%"
            query = query.filter(
                db.or_(Invoice.invoice_number.ilike(q), Invoice.description.ilike(q))
            )
        query = query.order_by(Invoice.date.desc(), Invoice.id.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return {
            "items": [_invoice_to_dict(inv) for inv in pagination.items],
            "total": pagination.total,
            "page": page,
            "per_page": per_page,
            "pages": (pagination.total + per_page - 1) // per_page if per_page > 0 else 0,
        }

    def _generate_number(self, tenant_id: int) -> str:
        year = date.today().year
        prefix = f"FT-{year}"
        last = Invoice.query.filter(
            Invoice.tenant_id == tenant_id,
            Invoice.invoice_number.like(f"{prefix}%")
        ).order_by(Invoice.invoice_number.desc()).first()
        if last:
            last_num = int(last.invoice_number.split("-")[-1])
            new_num = last_num + 1
        else:
            new_num = 1
        return f"{prefix}-{new_num:05d}"
