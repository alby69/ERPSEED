"""
Purchases Commands - Command classes for Purchases Service.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List

from shared.commands import Command, CreateCommand, UpdateCommand, DeleteCommand, QueryCommand


@dataclass
class CreatePurchaseOrderCommand(CreateCommand):
    number: str = ""
    date: str = ""
    supplier_id: int = 0
    expected_date: str = ""
    notes: str = ""
    lines: List[Dict[str, Any]] = field(default_factory=list)

    def to_payload(self) -> Dict[str, Any]:
        return {"number": self.number, "date": self.date, "supplier_id": self.supplier_id,
            "expected_date": self.expected_date, "notes": self.notes, "lines": self.lines}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CreatePurchaseOrderCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            number=data.get("number", ""), date=data.get("date", ""), supplier_id=data.get("supplier_id", 0),
            expected_date=data.get("expected_date", ""), notes=data.get("notes", ""), lines=data.get("lines", []))


@dataclass
class UpdatePurchaseOrderCommand(UpdateCommand):
    number: Optional[str] = None
    date: Optional[str] = None
    supplier_id: Optional[int] = None
    status: Optional[str] = None
    expected_date: Optional[str] = None
    notes: Optional[str] = None

    def to_payload(self) -> Dict[str, Any]:
        payload = {}
        for f in ["number", "date", "supplier_id", "status", "expected_date", "notes"]:
            v = getattr(self, f, None)
            if v is not None: payload[f] = v
        return payload

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UpdatePurchaseOrderCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            entity_id=data.get("entity_id", data.get("id", 0)), number=data.get("number"), date=data.get("date"),
            supplier_id=data.get("supplier_id"), status=data.get("status"), expected_date=data.get("expected_date"),
            notes=data.get("notes"))


@dataclass
class DeletePurchaseOrderCommand(DeleteCommand):
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeletePurchaseOrderCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            entity_id=data.get("entity_id", data.get("id", 0)))


@dataclass
class ConfirmPurchaseOrderCommand(Command):
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConfirmPurchaseOrderCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}))


@dataclass
class ReceivePurchaseOrderCommand(Command):
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReceivePurchaseOrderCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}))


@dataclass
class CancelPurchaseOrderCommand(Command):
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CancelPurchaseOrderCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}))


@dataclass
class GetPurchaseOrderCommand(QueryCommand):
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GetPurchaseOrderCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            entity_id=data.get("entity_id", data.get("id", 0)))


@dataclass
class ListPurchaseOrdersCommand(QueryCommand):
    search: str = ""
    status: str = ""
    supplier_id: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ListPurchaseOrdersCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            filters=data.get("filters", {}), pagination=data.get("pagination", {}), sorting=data.get("sorting", {}),
            search=data.get("search", ""), status=data.get("status", ""), supplier_id=data.get("supplier_id"))
