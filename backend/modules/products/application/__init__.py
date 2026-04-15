"""
Application Package - Contains commands, queries and handlers.
"""

from .commands import (
    CreateProductCommand,
    UpdateProductCommand,
    DeleteProductCommand,
    ListProductsCommand,
    GetProductCommand,
    UpdateStockCommand,
)
from .handlers import (
    CreateProductHandler,
    UpdateProductHandler,
    DeleteProductHandler,
    GetProductHandler,
    ListProductsHandler,
    UpdateStockHandler,
)

__all__ = [
    "CreateProductCommand",
    "UpdateProductCommand",
    "DeleteProductCommand",
    "ListProductsCommand",
    "GetProductCommand",
    "UpdateStockCommand",
    "CreateProductHandler",
    "UpdateProductHandler",
    "DeleteProductHandler",
    "GetProductHandler",
    "ListProductsHandler",
    "UpdateStockHandler",
]
