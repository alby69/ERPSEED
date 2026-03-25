"""
Domain Models for Sales.

Pure Python dataclasses representing sales concepts.
"""
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, Dict, Any, List


@dataclass
class SalesOrderLine:
    id: Optional[int] = None; tenant_id: int = 0; order_id: int = 0; product_id: int = 0
    description: str = ""; quantity: float = 0.0; unit_price: float = 0.0; total_price: float = 0.0

    def calculate_total(self) -> float:
        self.total_price = self.quantity * self.unit_price
        return self.total_price

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "tenant_id": self.tenant_id, "order_id": self.order_id, "product_id": self.product_id,
            "description": self.description, "quantity": self.quantity, "unit_price": self.unit_price, "total_price": self.total_price}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SalesOrderLine":
        return cls(id=data.get("id"), tenant_id=data.get("tenant_id", 0), order_id=data.get("order_id", 0),
            product_id=data.get("product_id", 0), description=data.get("description", ""),
            quantity=data.get("quantity", 0.0), unit_price=data.get("unit_price", 0.0), total_price=data.get("total_price", 0.0))


@dataclass
class SalesOrder:
    id: Optional[int] = None; tenant_id: int = 0; number: str = ""; date: date = field(default_factory=date.today)
    customer_id: int = 0; status: str = "draft"; total_amount: float = 0.0; notes: str = ""
    lines: List[SalesOrderLine] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow); updated_at: datetime = field(default_factory=datetime.utcnow)

    def calculate_total(self) -> float:
        self.total_amount = sum(line.calculate_total() for line in self.lines)
        return self.total_amount

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "tenant_id": self.tenant_id, "number": self.number,
            "date": self.date.isoformat() if self.date else None, "customer_id": self.customer_id,
            "status": self.status, "total_amount": self.total_amount, "notes": self.notes,
            "lines": [line.to_dict() for line in self.lines],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SalesOrder":
        lines = [SalesOrderLine.from_dict(l) for l in data.get("lines", [])]
        return cls(id=data.get("id"), tenant_id=data.get("tenant_id", 0), number=data.get("number", ""),
            date=data.get("date", date.today()), customer_id=data.get("customer_id", 0),
            status=data.get("status", "draft"), total_amount=data.get("total_amount", 0.0),
            notes=data.get("notes", ""), lines=lines)

    def validate(self) -> tuple[bool, List[str]]:
        errors = []
        if not self.number: errors.append("Order number is required")
        if not self.customer_id: errors.append("Customer is required")
        if self.status not in ["draft", "confirmed", "completed", "cancelled"]: errors.append(f"Invalid status: {self.status}")
        return len(errors) == 0, errors


@dataclass
class SalesOrderList:
    items: List[SalesOrder] = field(default_factory=list); total: int = 0; page: int = 1; per_page: int = 20

    def to_dict(self) -> Dict[str, Any]:
        return {"items": [o.to_dict() for o in self.items], "total": self.total, "page": self.page, "per_page": self.per_page,
            "pages": (self.total + self.per_page - 1) // self.per_page if self.per_page > 0 else 0}
