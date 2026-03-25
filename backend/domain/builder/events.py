"""
Domain Events for Builder.
"""
from dataclasses import dataclass
from typing import Dict, Any

from backend.shared.events.event import DomainEvent


@dataclass
class ModelCreatedEvent(DomainEvent):
    def __init__(self, model_id: int, model_name: str, project_id: int):
        super().__init__("builder.model.created", {"model_id": model_id, "model_name": model_name, "project_id": project_id})


@dataclass
class ModelUpdatedEvent(DomainEvent):
    def __init__(self, model_id: int, changes: Dict[str, Any]):
        super().__init__("builder.model.updated", {"model_id": model_id, "changes": changes})


@dataclass
class ModelDeletedEvent(DomainEvent):
    def __init__(self, model_id: int, model_name: str):
        super().__init__("builder.model.deleted", {"model_id": model_id, "model_name": model_name})


@dataclass
class FieldAddedEvent(DomainEvent):
    def __init__(self, model_id: int, field_id: int, field_name: str, field_type: str):
        super().__init__("builder.field.added", {"model_id": model_id, "field_id": field_id, "field_name": field_name, "field_type": field_type})


@dataclass
class FieldUpdatedEvent(DomainEvent):
    def __init__(self, field_id: int, changes: Dict[str, Any]):
        super().__init__("builder.field.updated", {"field_id": field_id, "changes": changes})


@dataclass
class FieldDeletedEvent(DomainEvent):
    def __init__(self, field_id: int, field_name: str):
        super().__init__("builder.field.deleted", {"field_id": field_id, "field_name": field_name})


@dataclass
class SchemaSyncedEvent(DomainEvent):
    def __init__(self, model_id: int, model_name: str, changes: Dict[str, Any]):
        super().__init__("builder.schema.synced", {"model_id": model_id, "model_name": model_name, "changes": changes})


@dataclass
class BlockCreatedEvent(DomainEvent):
    def __init__(self, block_id: int, block_name: str, project_id: int):
        super().__init__("builder.block.created", {"block_id": block_id, "block_name": block_name, "project_id": project_id})


@dataclass
class BlockCertifiedEvent(DomainEvent):
    def __init__(self, block_id: int, quality_score: int):
        super().__init__("builder.block.certified", {"block_id": block_id, "quality_score": quality_score})
