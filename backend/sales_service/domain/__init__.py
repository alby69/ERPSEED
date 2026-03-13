"""
Domain Package - Domain models and events for Sales Service.
"""

from .models import SalesOrder, SalesOrderLine, SalesOrderList
from .events import (
    SalesOrderCreatedEvent,
    SalesOrderUpdatedEvent,
    SalesOrderConfirmedEvent,
    SalesOrderCancelledEvent,
    SalesOrderDeletedEvent,
)

__all__ = [
    "SalesOrder",
    "SalesOrderLine", 
    "SalesOrderList",
    "SalesOrderCreatedEvent",
    "SalesOrderUpdatedEvent",
    "SalesOrderConfirmedEvent",
    "SalesOrderCancelledEvent",
    "SalesOrderDeletedEvent",
]
