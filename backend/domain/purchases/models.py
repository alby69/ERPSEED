"""
Domain Models for Purchases.

Pure Python dataclasses representing purchase concepts.
"""
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, Dict, Any, List


@dataclass
class PurchaseOrderLine:
    id: Optional[int] = None; tenant_id: int = 0; order_id: int = 0; product_id: int = 0
    description: str = ""; quantity: float = 0.0; unit_price: float = 0.0; total_price: float = 0.0

    def calculate_total(self) -> float:
        self.total_price = self.quantity * self.unit_price
        return self.total_price

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "tenant_id": self.tenant_id, "order_id": self.order_id, "product_id": self.product_id,
            "description": self.description, "quantity": self.quantity, "unit_price": self.unit_price, "total_price": self.total_price}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PurchaseOrderLine":
        return cls(id=data.get("id"), tenant_id=data.get("tenant_id", 0), order_id=data.get("order_id", 0),
            product_id=data.get("product_id", 0), description=data.get("description", ""),
            quantity=data.get("quantity", 0.0), unit_price=data.get("unit_price", 0.0), total_price=data.get("total_price", 0.0))


@dataclass
class PurchaseOrder:
    id: Optional[int] = None; tenant_id: int = 0; number: str = ""; date: date = field(default_factory=date.today)
    supplier_id: int = 0; status: str = "draft"; total_amount: float = 0.0
    expected_date: Optional[date] = None; notes: str = ""
    lines: List[PurchaseOrderLine] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow); updated_at: datetime = field(default_factory=datetime.utcnow)

    def calculate_total(self) -> float:
        self.total_amount = sum(line.calculate_total() for line in self.lines)
        return self.total_amount

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "tenant_id": self.tenant_id, "number": self.number,
            "date": self.date.isoformat() if self.date else None, "supplier_id": self.supplier_id,
            "status": self.status, "total_amount": self.total_amount,
            "expected_date": self.expected_date.isoformat() if self.expected_date else None,
            "notes": self.notes, "lines": [line.to_dict() for line in self.lines],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PurchaseOrder":
        lines = [PurchaseOrderLine.from_dict(l) for l in data.get("lines", [])]
        return cls(id=data.get("id"), tenant_id=data.get("tenant_id", 0), number=data.get("number", ""),
            date=data.get("date", date.today()), supplier_id=data.get("supplier_id", 0),
            status=data.get("status", "draft"), total_amount=data.get("total_amount", 0.0),
            expected_date=data.get("expected_date"), notes=data.get("notes", ""), lines=lines)

    def validate(self) -> tuple[bool, List[str]]:
        errors = []
        if not self.number: errors.append("Order number is required")
        if not self.supplier_id: errors.append("Supplier is required")
        if self.status not in ["draft", "confirmed", "received", "cancelled"]: errors.append(f"Invalid status: {self.status}")
        return len(errors) == 0, errors
