from dataclasses import dataclass, field
from typing import Optional, List
from datetime import date


@dataclass
class CreateInvoiceFromSalesOrderCommand:
    tenant_id: int = 0
    sales_order_id: int = 0
    user_id: Optional[int] = None
    date: Optional[date] = None
    due_date: Optional[date] = None
    description: str = ""
    notes: str = ""


@dataclass
class CreateInvoiceCommand:
    tenant_id: int = 0
    party_id: int = 0
    sales_order_id: Optional[int] = None
    date: Optional[date] = None
    due_date: Optional[date] = None
    description: str = ""
    notes: str = ""
    lines: List[dict] = field(default_factory=list)
    user_id: Optional[int] = None

    @classmethod
    def from_dict(cls, data: dict) -> "CreateInvoiceCommand":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class UpdateInvoiceCommand:
    entity_id: int = 0
    tenant_id: int = 0
    date: Optional[date] = None
    due_date: Optional[date] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    lines: Optional[List[dict]] = None

    @classmethod
    def from_dict(cls, data: dict) -> "UpdateInvoiceCommand":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class IssueInvoiceCommand:
    entity_id: int = 0
    tenant_id: int = 0
    user_id: Optional[int] = None

    @classmethod
    def from_dict(cls, data: dict) -> "IssueInvoiceCommand":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class CancelInvoiceCommand:
    entity_id: int = 0
    tenant_id: int = 0
    reason: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> "CancelInvoiceCommand":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class PayInvoiceCommand:
    entity_id: int = 0
    tenant_id: int = 0
    amount: float = 0.0
    payment_date: Optional[date] = None

    @classmethod
    def from_dict(cls, data: dict) -> "PayInvoiceCommand":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class GetInvoiceCommand:
    entity_id: int = 0
    tenant_id: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> "GetInvoiceCommand":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class ListInvoicesCommand:
    tenant_id: int = 0
    status: Optional[str] = None
    party_id: Optional[int] = None
    search: Optional[str] = None
    page: int = 1
    per_page: int = 20

    @classmethod
    def from_dict(cls, data: dict) -> "ListInvoicesCommand":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
