"""
Models package - Organized models for ERPSeed.
All application models are organized here with clear separation of concerns.
"""
from backend.extensions import db

from backend.core.models.base import BaseModel
from .user import User
from .project import Project, project_members
from .product import Product, ProductCategory, ProductStockModel as ProductStock
from .sales import SalesOrder, SalesOrderLine
from .purchase import PurchaseOrder, PurchaseOrderLine
from .ai import AIConversation
from .chart import ChartLibraryConfig
from .user_role import UserRole
from .tax import TaxRate
from .uom import UnitOfMeasure
from .pricing import PriceList, PriceListItem
from .movement_reason import MovementReason
from .goods_receipt import GoodsReceipt, GoodsReceiptLine
from .maturity import Maturity
from .crm import Lead, Opportunity
from .contract import Contract
from .manufacturing import BillOfMaterial, BOMLine, WorkCycle, WorkPhase, ProductionOrder, ProductionOrderMaterial
from .project_management import BusinessProject, Timesheet, TimesheetLine
from .report import Report, ReportExecution
from .vat import VatRegisterEntry, VatLiquidation, IntrastatDeclaration
from .riba import RiBa, RiBaItem
from .lot import Lot, SerialNumber
from .purchase_request import PurchaseRequest, PurchaseRequestLine, RFQ, RFQLine, SupplierQuotation, SupplierQuotationLine
from .mrp import MRPRun, MRPSuggestion

from backend.plugins.accounting.models import Invoice

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
    "ProductCategory",
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
    "TaxRate",
    "UnitOfMeasure",
    "PriceList",
    "PriceListItem",
    "MovementReason",
    "GoodsReceipt",
    "GoodsReceiptLine",
    "Maturity",
    "Lead",
    "Opportunity",
    "Contract",
    "BillOfMaterial", "BOMLine", "WorkCycle", "WorkPhase", "ProductionOrder", "ProductionOrderMaterial",
    "BusinessProject", "Timesheet", "TimesheetLine",
    "Report", "ReportExecution",
    "VatRegisterEntry", "VatLiquidation", "IntrastatDeclaration",
    "RiBa", "RiBaItem",
    "Lot", "SerialNumber",
    "PurchaseRequest", "PurchaseRequestLine", "RFQ", "RFQLine", "SupplierQuotation", "SupplierQuotationLine",
    "MRPRun", "MRPSuggestion",
    "Invoice",
]
