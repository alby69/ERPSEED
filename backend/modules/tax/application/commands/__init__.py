from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import date
from backend.shared.commands import Command, CreateCommand, UpdateCommand, DeleteCommand, QueryCommand


@dataclass
class CreateTaxRateCommand(CreateCommand):
    code: str = ""
    name: str = ""
    rate: float = 0.0
    description: str = ""
    is_active: bool = True
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None

    def to_payload(self) -> Dict[str, Any]:
        payload = {
            "code": self.code,
            "name": self.name,
            "rate": self.rate,
            "description": self.description,
            "is_active": self.is_active,
        }
        if self.valid_from:
            payload["valid_from"] = self.valid_from
        if self.valid_to:
            payload["valid_to"] = self.valid_to
        return payload

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CreateTaxRateCommand":
        return cls(
            code=data.get("code", ""),
            name=data.get("name", ""),
            rate=float(data.get("rate", 0)),
            description=data.get("description", ""),
            is_active=data.get("is_active", True),
            valid_from=data.get("valid_from"),
            valid_to=data.get("valid_to"),
            tenant_id=data.get("tenant_id"),
            userId=data.get("userId"),
        )


@dataclass
class UpdateTaxRateCommand(UpdateCommand):
    entity_id: int = 0
    code: Optional[str] = None
    name: Optional[str] = None
    rate: Optional[float] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None

    def to_payload(self) -> Dict[str, Any]:
        payload = {}
        if self.code is not None:
            payload["code"] = self.code
        if self.name is not None:
            payload["name"] = self.name
        if self.rate is not None:
            payload["rate"] = self.rate
        if self.description is not None:
            payload["description"] = self.description
        if self.is_active is not None:
            payload["is_active"] = self.is_active
        if self.valid_from is not None:
            payload["valid_from"] = self.valid_from
        if self.valid_to is not None:
            payload["valid_to"] = self.valid_to
        return payload

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UpdateTaxRateCommand":
        return cls(
            entity_id=data.get("entity_id", 0),
            code=data.get("code"),
            name=data.get("name"),
            rate=float(data["rate"]) if "rate" in data and data["rate"] is not None else None,
            description=data.get("description"),
            is_active=data.get("is_active"),
            valid_from=data.get("valid_from"),
            valid_to=data.get("valid_to"),
            tenant_id=data.get("tenant_id"),
            userId=data.get("userId"),
        )


@dataclass
class DeleteTaxRateCommand(DeleteCommand):
    entity_id: int = 0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeleteTaxRateCommand":
        return cls(
            entity_id=data.get("entity_id", 0),
            tenant_id=data.get("tenant_id"),
            userId=data.get("userId"),
        )


@dataclass
class GetTaxRateQuery(QueryCommand):
    entity_id: int = 0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GetTaxRateQuery":
        return cls(
            entity_id=data.get("entity_id", 0),
            tenant_id=data.get("tenant_id"),
            userId=data.get("userId"),
        )


@dataclass
class ListTaxRatesQuery(QueryCommand):
    search: Optional[str] = None
    is_active: Optional[bool] = None
    page: int = 1
    per_page: int = 20

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ListTaxRatesQuery":
        return cls(
            search=data.get("search"),
            is_active=data.get("is_active"),
            page=data.get("pagination", {}).get("page", 1) if isinstance(data.get("pagination"), dict) else data.get("page", 1),
            per_page=data.get("pagination", {}).get("per_page", 20) if isinstance(data.get("pagination"), dict) else data.get("per_page", 20),
            tenant_id=data.get("tenant_id"),
            userId=data.get("userId"),
        )
