"""
Domain Models for Purchases Service.
"""
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, Dict, Any, List


@dataclass
class PurchaseOrderLine:
    id: Optional[int] = None
    tenant_id: int = 0
    order_id: int = 0
    product_id: int = 0
    description: str = ""
    quantity: float = 0.0
    unit_price: float = 0.0
    discount_percent: float = 0.0
    tax_id: Optional[int] = None
    uom_id: Optional[int] = None
    expected_delivery_date: Optional[date] = None
    total_price: float = 0.0
    quantity_received: float = 0.0

    def calculate_total(self) -> float:
        discount_factor = max(0.0, 1.0 - (self.discount_percent / 100.0))
        self.total_price = self.quantity * self.unit_price * discount_factor
        return self.total_price

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "order_id": self.order_id,
            "product_id": self.product_id,
            "description": self.description,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "discount_percent": self.discount_percent,
            "tax_id": self.tax_id,
            "uom_id": self.uom_id,
            "expected_delivery_date": self.expected_delivery_date.isoformat() if self.expected_delivery_date else None,
            "total_price": self.total_price,
            "quantity_received": self.quantity_received,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PurchaseOrderLine":
        edd = data.get("expected_delivery_date")
        if edd and isinstance(edd, str):
            edd = date.fromisoformat(edd)
        line = cls(
            id=data.get("id"),
            tenant_id=data.get("tenant_id", 0),
            order_id=data.get("order_id", 0),
            product_id=data.get("product_id", 0),
            description=data.get("description", ""),
            quantity=float(data.get("quantity", 0.0)),
            unit_price=float(data.get("unit_price", 0.0)),
            discount_percent=float(data.get("discount_percent", 0.0)),
            tax_id=data.get("tax_id"),
            uom_id=data.get("uom_id"),
            expected_delivery_date=edd,
            total_price=float(data.get("total_price", 0.0)),
            quantity_received=float(data.get("quantity_received", 0.0)),
        )
        if not line.total_price and (line.quantity or line.unit_price):
            line.calculate_total()
        return line


@dataclass
class PurchaseOrder:
    id: Optional[int] = None
    tenant_id: int = 0
    number: str = ""
    date: date = field(default_factory=date.today)
    supplier_id: int = 0
    currency_id: str = "EUR"
    payment_term_id: Optional[int] = None
    buyer_id: Optional[int] = None
    supplier_reference: str = ""
    landing_costs: float = 0.0
    status: str = "draft"
    total_amount: float = 0.0
    expected_date: Optional[date] = None
    notes: str = ""
    lines: List[PurchaseOrderLine] = field(default_factory=list)

    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def calculate_total(self) -> float:
        self.total_amount = sum(line.calculate_total() for line in self.lines) + float(self.landing_costs or 0.0)
        return self.total_amount

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "number": self.number,
            "date": self.date.isoformat() if self.date else None,
            "supplier_id": self.supplier_id,
            "currency_id": self.currency_id,
            "payment_term_id": self.payment_term_id,
            "buyer_id": self.buyer_id,
            "supplier_reference": self.supplier_reference,
            "landing_costs": self.landing_costs,
            "status": self.status,
            "total_amount": self.total_amount,
            "expected_date": self.expected_date.isoformat() if self.expected_date else None,
            "notes": self.notes,
            "lines": [line.to_dict() for line in self.lines],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PurchaseOrder":
        lines = [PurchaseOrderLine.from_dict(l) for l in data.get("lines", [])]
        exp_d = data.get("expected_date")
        if exp_d and isinstance(exp_d, str):
            exp_d = date.fromisoformat(exp_d)
        d_val = data.get("date")
        if d_val and isinstance(d_val, str):
            d_val = date.fromisoformat(d_val)
        elif not d_val:
            d_val = date.today()

        return cls(
            id=data.get("id"),
            tenant_id=data.get("tenant_id", 0),
            number=data.get("number", ""),
            date=d_val,
            supplier_id=data.get("supplier_id", 0),
            currency_id=data.get("currency_id", "EUR") or "EUR",
            payment_term_id=data.get("payment_term_id"),
            buyer_id=data.get("buyer_id"),
            supplier_reference=data.get("supplier_reference", ""),
            landing_costs=float(data.get("landing_costs", 0.0)),
            status=data.get("status", "draft"),
            total_amount=float(data.get("total_amount", 0.0)),
            expected_date=exp_d,
            notes=data.get("notes", ""),
            lines=lines,
        )

    def validate(self) -> tuple[bool, List[str]]:
        errors = []
        if not self.number:
            errors.append("Order number is required")
        if not self.supplier_id:
            errors.append("Supplier is required")
        if self.status not in ["draft", "confirmed", "received", "cancelled"]:
            errors.append(f"Invalid status: {self.status}")
        return len(errors) == 0, errors
