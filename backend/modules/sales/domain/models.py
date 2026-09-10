"""
Domain Models for Sales Service.

Pure Python dataclasses representing sales concepts.
"""
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, Dict, Any, List


@dataclass
class SalesOrderLine:
    """Domain model for sales order line."""

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
    total_price: float = 0.0

    def calculate_total(self) -> float:
        """Calculate total price accounting for discount percent."""
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
            "total_price": self.total_price,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SalesOrderLine":
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
            total_price=float(data.get("total_price", 0.0)),
        )
        if not line.total_price and (line.quantity or line.unit_price):
            line.calculate_total()
        return line


@dataclass
class SalesOrder:
    """Domain model for sales order."""

    id: Optional[int] = None
    tenant_id: int = 0
    number: str = ""
    date: date = field(default_factory=date.today)
    customer_id: int = 0
    pricelist_id: Optional[int] = None
    currency_id: str = "EUR"
    payment_term_id: Optional[int] = None
    billing_address_id: Optional[int] = None
    shipping_address_id: Optional[int] = None
    salesperson_id: Optional[int] = None
    customer_reference: str = ""
    warehouse_id: Optional[int] = None
    status: str = "draft"
    type: str = "order"  # order, quote, delivery_note
    expiry_date: Optional[date] = None  # for quotes
    total_amount: float = 0.0
    notes: str = ""
    lines: List[SalesOrderLine] = field(default_factory=list)

    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def calculate_total(self) -> float:
        """Calculate total from lines."""
        self.total_amount = sum(line.calculate_total() for line in self.lines)
        return self.total_amount

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "number": self.number,
            "date": self.date.isoformat() if self.date else None,
            "customer_id": self.customer_id,
            "pricelist_id": self.pricelist_id,
            "currency_id": self.currency_id,
            "payment_term_id": self.payment_term_id,
            "billing_address_id": self.billing_address_id,
            "shipping_address_id": self.shipping_address_id,
            "salesperson_id": self.salesperson_id,
            "customer_reference": self.customer_reference,
            "warehouse_id": self.warehouse_id,
            "status": self.status,
            "type": self.type,
            "expiry_date": self.expiry_date.isoformat() if self.expiry_date else None,
            "total_amount": self.total_amount,
            "notes": self.notes,
            "lines": [line.to_dict() for line in self.lines],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SalesOrder":
        lines = [SalesOrderLine.from_dict(l) for l in data.get("lines", [])]
        ed = data.get("expiry_date")
        if ed and isinstance(ed, str):
            ed = date.fromisoformat(ed)
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
            customer_id=data.get("customer_id", 0),
            pricelist_id=data.get("pricelist_id"),
            currency_id=data.get("currency_id", "EUR") or "EUR",
            payment_term_id=data.get("payment_term_id"),
            billing_address_id=data.get("billing_address_id"),
            shipping_address_id=data.get("shipping_address_id"),
            salesperson_id=data.get("salesperson_id"),
            customer_reference=data.get("customer_reference", ""),
            warehouse_id=data.get("warehouse_id"),
            status=data.get("status", "draft"),
            type=data.get("type", "order"),
            expiry_date=ed,
            total_amount=float(data.get("total_amount", 0.0)),
            notes=data.get("notes", ""),
            lines=lines,
        )

    def validate(self) -> tuple[bool, List[str]]:
        errors = []
        if not self.number:
            errors.append("Order number is required")
        if not self.customer_id:
            errors.append("Customer is required")
        if self.status not in ["draft", "confirmed", "completed", "cancelled"]:
            errors.append(f"Invalid status: {self.status}")
        if self.type not in ["order", "quote", "delivery_note"]:
            errors.append(f"Invalid type: {self.type}")
        return len(errors) == 0, errors


@dataclass
class SalesOrderList:
    """Paginated list of sales orders."""

    items: List[SalesOrder] = field(default_factory=list)
    total: int = 0
    page: int = 1
    per_page: int = 20

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": [o.to_dict() for o in self.items],
            "total": self.total,
            "page": self.page,
            "per_page": self.per_page,
            "pages": (self.total + self.per_page - 1) // self.per_page if self.per_page > 0 else 0,
        }
