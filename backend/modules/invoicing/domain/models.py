from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List


@dataclass
class SalesInvoiceLine:
    id: Optional[int] = None
    tenant_id: int = 0
    invoice_id: int = 0
    product_id: int = 0
    description: str = ""
    quantity: float = 1.0
    unit_price: float = 0.0
    discount_percent: float = 0.0
    tax_percent: float = 0.0
    tax_id: Optional[int] = None
    total: float = 0.0

    def calculate_total(self) -> float:
        subtotal = self.quantity * self.unit_price
        discount = subtotal * (self.discount_percent / 100)
        taxable = subtotal - discount
        tax = taxable * (self.tax_percent / 100)
        self.total = taxable + tax
        return self.total

    def to_dict(self) -> dict:
        return {
            "id": self.id, "tenant_id": self.tenant_id, "invoice_id": self.invoice_id,
            "product_id": self.product_id, "description": self.description,
            "quantity": self.quantity, "unit_price": self.unit_price,
            "discount_percent": self.discount_percent, "tax_percent": self.tax_percent,
            "tax_id": self.tax_id, "total": self.total,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SalesInvoiceLine":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class SalesInvoice:
    id: Optional[int] = None
    tenant_id: int = 0
    invoice_number: str = ""
    invoice_type: str = "AR"
    party_id: int = 0
    sales_order_id: Optional[int] = None
    date: date = field(default_factory=date.today)
    due_date: Optional[date] = None
    description: str = ""
    notes: str = ""
    subtotal: float = 0.0
    tax_amount: float = 0.0
    total: float = 0.0
    status: str = "draft"
    journal_entry_id: Optional[int] = None
    created_by: Optional[int] = None
    lines: List[SalesInvoiceLine] = field(default_factory=list)

    def calculate_totals(self):
        self.subtotal = sum(line.calculate_total() for line in self.lines)
        self.tax_amount = sum(
            (line.quantity * line.unit_price * (1 - line.discount_percent / 100)) * (line.tax_percent / 100)
            for line in self.lines if line.tax_percent > 0
        )
        self.total = self.subtotal + self.tax_amount
        return self.total

    def to_dict(self) -> dict:
        return {
            "id": self.id, "tenant_id": self.tenant_id, "invoice_number": self.invoice_number,
            "invoice_type": self.invoice_type, "party_id": self.party_id,
            "sales_order_id": self.sales_order_id,
            "date": self.date.isoformat() if self.date else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "description": self.description, "notes": self.notes,
            "subtotal": self.subtotal, "tax_amount": self.tax_amount, "total": self.total,
            "status": self.status, "journal_entry_id": self.journal_entry_id,
            "created_by": self.created_by,
            "lines": [l.to_dict() for l in self.lines],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SalesInvoice":
        lines = [SalesInvoiceLine.from_dict(l) for l in data.get("lines", [])]
        instance = cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__ and k != "lines"})
        instance.lines = lines
        return instance
