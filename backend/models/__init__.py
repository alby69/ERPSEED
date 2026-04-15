"""
Models package - Organized models for ERPSeed.
All application models are organized here with clear separation of concerns.
"""
from backend.extensions import db

from .base import BaseModel
from .user import User
from .project import Project, project_members
from .product import Product, ProductStockModel as ProductStock
from .sales import SalesOrder, SalesOrderLine
from .purchase import PurchaseOrder, PurchaseOrderLine
from .ai import AIConversation
from .chart import ChartLibraryConfig
from .user_role import UserRole

from .system import (
    SysModel,
    SysField,
    SysView,
    SysComponent,
    SysAction,
    SysChart,
    SysDashboard,
    SysModelVersion,
    SysReadModel,
)

from backend.core.models import Tenant, TenantMember, AuditLog
from backend.modules.entities.soggetto import Soggetto

__all__ = [
    "db",
    "BaseModel",
    "User",
    "Project",
    "project_members",
    "Product",
    "ProductStock",
    "SalesOrder",
    "SalesOrderLine",
    "PurchaseOrder",
    "PurchaseOrderLine",
    "AIConversation",
    "ChartLibraryConfig",
    "UserRole",
    "SysModel",
    "SysField",
    "SysView",
    "SysComponent",
    "SysAction",
    "SysChart",
    "SysDashboard",
    "SysModelVersion",
    "SysReadModel",
    "AuditLog",
    "Tenant",
    "TenantMember",
    "Soggetto",
]
