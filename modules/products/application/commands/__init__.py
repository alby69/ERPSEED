"""
Product Commands - Command classes for Products Service.

These commands represent intentions to perform actions on products.
They are simple data classes used by the command handlers.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

from shared.commands import Command, CreateCommand, UpdateCommand, DeleteCommand, QueryCommand


@dataclass
class CreateProductCommand(CreateCommand):
    """Command to create a new product."""

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

    def to_payload(self) -> Dict[str, Any]:
        """Extract product data as payload."""
        return {
            "name": self.name,
            "code": self.code,
            "description": self.description,
            "unit_price": self.unit_price,
            "category": self.category,
            "sku": self.sku,
            "barcode": self.barcode,
            "is_active": self.is_active,
            "track_inventory": self.track_inventory,
            "current_stock": self.current_stock,
            "reorder_level": self.reorder_level,
            "unit_of_measure": self.unit_of_measure,
            "weight": self.weight,
            "dimensions": self.dimensions,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CreateProductCommand":
        """Create command from dictionary."""
        return cls(
            tenant_id=data.get("tenant_id"),
            user_id=data.get("user_id"),
            metadata=data.get("metadata", {}),
            name=data.get("name", ""),
            code=data.get("code", ""),
            description=data.get("description", ""),
            unit_price=data.get("unit_price", 0.0),
            category=data.get("category", ""),
            sku=data.get("sku", ""),
            barcode=data.get("barcode", ""),
            is_active=data.get("is_active", True),
            track_inventory=data.get("track_inventory", False),
            current_stock=data.get("current_stock", 0.0),
            reorder_level=data.get("reorder_level", 0.0),
            unit_of_measure=data.get("unit_of_measure", "pcs"),
            weight=data.get("weight"),
            dimensions=data.get("dimensions"),
        )


@dataclass
class UpdateProductCommand(UpdateCommand):
    """Command to update an existing product."""

    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    unit_price: Optional[float] = None
    category: Optional[str] = None
    sku: Optional[str] = None
    barcode: Optional[str] = None
    is_active: Optional[bool] = None
    track_inventory: Optional[bool] = None
    current_stock: Optional[float] = None
    reorder_level: Optional[float] = None
    unit_of_measure: Optional[str] = None
    weight: Optional[float] = None
    dimensions: Optional[str] = None

    def to_payload(self) -> Dict[str, Any]:
        """Extract non-None fields as payload."""
        payload = {}
        for field_name in ["name", "code", "description", "unit_price", "category",
                          "sku", "barcode", "is_active", "track_inventory",
                          "current_stock", "reorder_level", "unit_of_measure",
                          "weight", "dimensions"]:
            value = getattr(self, field_name, None)
            if value is not None:
                payload[field_name] = value
        return payload

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UpdateProductCommand":
        """Create command from dictionary."""
        return cls(
            tenant_id=data.get("tenant_id"),
            user_id=data.get("user_id"),
            metadata=data.get("metadata", {}),
            entity_id=data.get("entity_id", data.get("id", 0)),
            name=data.get("name"),
            code=data.get("code"),
            description=data.get("description"),
            unit_price=data.get("unit_price"),
            category=data.get("category"),
            sku=data.get("sku"),
            barcode=data.get("barcode"),
            is_active=data.get("is_active"),
            track_inventory=data.get("track_inventory"),
            current_stock=data.get("current_stock"),
            reorder_level=data.get("reorder_level"),
            unit_of_measure=data.get("unit_of_measure"),
            weight=data.get("weight"),
            dimensions=data.get("dimensions"),
        )


@dataclass
class DeleteProductCommand(DeleteCommand):
    """Command to delete a product."""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeleteProductCommand":
        """Create command from dictionary."""
        return cls(
            tenant_id=data.get("tenant_id"),
            user_id=data.get("user_id"),
            metadata=data.get("metadata", {}),
            entity_id=data.get("entity_id", data.get("id", 0)),
        )


@dataclass
class GetProductCommand(QueryCommand):
    """Command to get a single product by ID."""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GetProductCommand":
        return cls(
            tenant_id=data.get("tenant_id"),
            user_id=data.get("user_id"),
            metadata=data.get("metadata", {}),
            entity_id=data.get("entity_id", data.get("id", 0)),
        )


@dataclass
class ListProductsCommand(QueryCommand):
    """Command to list products with filtering and pagination."""

    search: str = ""
    category: str = ""
    is_active: Optional[bool] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ListProductsCommand":
        return cls(
            tenant_id=data.get("tenant_id"),
            user_id=data.get("user_id"),
            metadata=data.get("metadata", {}),
            filters=data.get("filters", {}),
            pagination=data.get("pagination", {}),
            sorting=data.get("sorting", {}),
            search=data.get("search", ""),
            category=data.get("category", ""),
            is_active=data.get("is_active"),
            min_price=data.get("min_price"),
            max_price=data.get("max_price"),
        )


@dataclass
class UpdateStockCommand(Command):
    """Command to update product stock."""

    product_id: int = 0
    new_stock: float = 0.0
    reason: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UpdateStockCommand":
        return cls(
            tenant_id=data.get("tenant_id"),
            user_id=data.get("user_id"),
            metadata=data.get("metadata", {}),
            product_id=data.get("product_id", 0),
            new_stock=data.get("new_stock", 0.0),
            reason=data.get("reason", "manual"),
        )
