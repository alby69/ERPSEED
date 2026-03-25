"""
Domain Models for Products.

Pure Python dataclasses representing product domain concepts.
Independent from SQLAlchemy models (infrastructure layer).
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class Product:
    """Domain model for Product entity."""

    id: Optional[int] = None
    tenant_id: int = 0
    name: str = ""
    code: str = ""
    description: str = ""
    unit_price: float = 0.0
    category: str = ""
    sku: str = ""
    barcode: str = ""
    is_active: bool = True
    track_inventory: bool = False
    current_stock: float = 0.0
    reorder_level: float = 0.0
    unit_of_measure: str = "pcs"
    weight: Optional[float] = None
    dimensions: Optional[str] = None

    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "tenant_id": self.tenant_id, "name": self.name, "code": self.code,
            "description": self.description, "unit_price": self.unit_price, "category": self.category,
            "sku": self.sku, "barcode": self.barcode, "is_active": self.is_active,
            "track_inventory": self.track_inventory, "current_stock": self.current_stock,
            "reorder_level": self.reorder_level, "unit_of_measure": self.unit_of_measure,
            "weight": self.weight, "dimensions": self.dimensions,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Product":
        return cls(
            id=data.get("id"), tenant_id=data.get("tenant_id", 0), name=data.get("name", ""),
            code=data.get("code", ""), description=data.get("description", ""),
            unit_price=data.get("unit_price", 0.0), category=data.get("category", ""),
            sku=data.get("sku", ""), barcode=data.get("barcode", ""),
            is_active=data.get("is_active", True), track_inventory=data.get("track_inventory", False),
            current_stock=data.get("current_stock", 0.0), reorder_level=data.get("reorder_level", 0.0),
            unit_of_measure=data.get("unit_of_measure", "pcs"), weight=data.get("weight"),
            dimensions=data.get("dimensions"),
        )

    def validate(self) -> tuple[bool, list[str]]:
        errors = []
        if not self.name or not self.name.strip(): errors.append("Product name is required")
        if not self.code or not self.code.strip(): errors.append("Product code is required")
        if self.unit_price is not None and self.unit_price < 0: errors.append("Unit price cannot be negative")
        if self.current_stock is not None and self.current_stock < 0: errors.append("Current stock cannot be negative")
        return len(errors) == 0, errors


@dataclass
class ProductList:
    """Domain model for paginated product list."""

    items: list = field(default_factory=list)
    total: int = 0
    page: int = 1
    per_page: int = 20

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": [p.to_dict() if hasattr(p, 'to_dict') else p for p in self.items],
            "total": self.total, "page": self.page, "per_page": self.per_page,
            "pages": (self.total + self.per_page - 1) // self.per_page if self.per_page > 0 else 0,
        }
