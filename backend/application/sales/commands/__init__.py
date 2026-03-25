"""
Sales Commands - Command classes for Sales.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List

from backend.shared.commands import Command, CreateCommand, UpdateCommand, DeleteCommand, QueryCommand


@dataclass
class CreateSalesOrderCommand(CreateCommand):
    number: str = ""; date: str = ""; customer_id: int = 0; notes: str = ""; lines: List[Dict[str, Any]] = field(default_factory=list)

    def to_payload(self) -> Dict[str, Any]:
        return {"number": self.number, "date": self.date, "customer_id": self.customer_id, "notes": self.notes, "lines": self.lines}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CreateSalesOrderCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            number=data.get("number", ""), date=data.get("date", ""), customer_id=data.get("customer_id", 0),
            notes=data.get("notes", ""), lines=data.get("lines", []))


@dataclass
class UpdateSalesOrderCommand(UpdateCommand):
    number: Optional[str] = None; date: Optional[str] = None; customer_id: Optional[int] = None
    status: Optional[str] = None; notes: Optional[str] = None

    def to_payload(self) -> Dict[str, Any]:
        payload = {}
        for f in ["number", "date", "customer_id", "status", "notes"]:
            v = getattr(self, f, None)
            if v is not None: payload[f] = v
        return payload

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UpdateSalesOrderCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            entity_id=data.get("entity_id", data.get("id", 0)), number=data.get("number"), date=data.get("date"),
            customer_id=data.get("customer_id"), status=data.get("status"), notes=data.get("notes"))


@dataclass
class DeleteSalesOrderCommand(DeleteCommand):
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeleteSalesOrderCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            entity_id=data.get("entity_id", data.get("id", 0)))


@dataclass
class ConfirmSalesOrderCommand(Command):
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConfirmSalesOrderCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}))


@dataclass
class CancelSalesOrderCommand(Command):
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CancelSalesOrderCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}))


@dataclass
class GetSalesOrderCommand(QueryCommand):
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GetSalesOrderCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            entity_id=data.get("entity_id", data.get("id", 0)))


@dataclass
class ListSalesOrdersCommand(QueryCommand):
    search: str = ""; status: str = ""; customer_id: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ListSalesOrdersCommand":
        return cls(tenant_id=data.get("tenant_id"), user_id=data.get("user_id"), metadata=data.get("metadata", {}),
            filters=data.get("filters", {}), pagination=data.get("pagination", {}), sorting=data.get("sorting", {}),
            search=data.get("search", ""), status=data.get("status", ""), customer_id=data.get("customer_id"))
