from dataclasses import dataclass
from typing import Any, Dict
from backend.shared.events.event import DomainEvent


@dataclass
class TaxRateCreatedEvent(DomainEvent):
    def __init__(self, tax_rate_id: int, tax_rate_data: Dict[str, Any], tenant_id: int):
        super().__init__(
            event_type="tax_rate.created",
            payload={
                "tax_rate_id": tax_rate_id,
                "code": tax_rate_data.get("code"),
                "name": tax_rate_data.get("name"),
                "rate": tax_rate_data.get("rate"),
                "tenant_id": tenant_id,
            }
        )


@dataclass
class TaxRateUpdatedEvent(DomainEvent):
    def __init__(self, tax_rate_id: int, old_data: Dict[str, Any], new_data: Dict[str, Any], tenant_id: int):
        super().__init__(
            event_type="tax_rate.updated",
            payload={
                "tax_rate_id": tax_rate_id,
                "old_data": old_data,
                "new_data": new_data,
                "tenant_id": tenant_id,
            }
        )


@dataclass
class TaxRateDeletedEvent(DomainEvent):
    def __init__(self, tax_rate_id: int, tax_rate_data: Dict[str, Any], tenant_id: int):
        super().__init__(
            event_type="tax_rate.deleted",
            payload={
                "tax_rate_id": tax_rate_id,
                "code": tax_rate_data.get("code"),
                "name": tax_rate_data.get("name"),
                "tenant_id": tenant_id,
            }
        )
