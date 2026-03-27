"""
Domain Package - Contains domain models and events for Products Service.
"""

from .models import Product, ProductList
from .events import (
    ProductCreatedEvent,
    ProductUpdatedEvent,
    ProductDeletedEvent,
    ProductStockChangedEvent,
    ProductLowStockEvent,
)

__all__ = [
    "Product",
    "ProductList",
    "ProductCreatedEvent",
    "ProductUpdatedEvent",
    "ProductDeletedEvent",
    "ProductStockChangedEvent",
    "ProductLowStockEvent",
]
