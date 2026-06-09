from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional


@dataclass
class TaxRate:
    id: Optional[int] = None
    tenant_id: Optional[int] = None
    code: str = ""
    name: str = ""
    rate: float = 0.0
    description: str = ""
    is_active: bool = True
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def validate(self) -> list:
        errors = []
        if not self.code:
            errors.append("code is required")
        if not self.name:
            errors.append("name is required")
        if self.rate < 0:
            errors.append("rate must be >= 0")
        if self.valid_from and self.valid_to and self.valid_from > self.valid_to:
            errors.append("valid_from must be before valid_to")
        return errors

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "code": self.code,
            "name": self.name,
            "rate": self.rate,
            "description": self.description,
            "is_active": self.is_active,
            "valid_from": self.valid_from.isoformat() if self.valid_from else None,
            "valid_to": self.valid_to.isoformat() if self.valid_to else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TaxRate":
        valid_from = data.get("valid_from")
        valid_to = data.get("valid_to")
        if isinstance(valid_from, str):
            valid_from = date.fromisoformat(valid_from)
        if isinstance(valid_to, str):
            valid_to = date.fromisoformat(valid_to)
        return cls(
            id=data.get("id"),
            tenant_id=data.get("tenant_id"),
            code=data.get("code", ""),
            name=data.get("name", ""),
            rate=float(data.get("rate", 0)),
            description=data.get("description", ""),
            is_active=data.get("is_active", True),
            valid_from=valid_from,
            valid_to=valid_to,
        )


@dataclass
class TaxRateList:
    items: list = field(default_factory=list)
    total: int = 0
    page: int = 1
    per_page: int = 20
