"""Products application module."""
from backend.application.products.commands import (
    CreateProductCommand, UpdateProductCommand, DeleteProductCommand,
    GetProductCommand, ListProductsCommand, UpdateStockCommand,
)
from backend.application.products.handlers import (
    CreateProductHandler, UpdateProductHandler, DeleteProductHandler,
    GetProductHandler, ListProductsHandler, UpdateStockHandler,
)

__all__ = [
    "CreateProductCommand", "UpdateProductCommand", "DeleteProductCommand",
    "GetProductCommand", "ListProductsCommand", "UpdateStockCommand",
    "CreateProductHandler", "UpdateProductHandler", "DeleteProductHandler",
    "GetProductHandler", "ListProductsHandler", "UpdateStockHandler",
]
