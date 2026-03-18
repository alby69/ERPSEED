"""
Domain Events for Builder Service.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional

from backend.shared.events import DomainEvent


@dataclass
class ModelCreatedEvent(DomainEvent):
    """Event fired when a model is created."""

    model_id: int = 0
    model_name: str = ""
    project_id: int = 0


@dataclass
class ModelUpdatedEvent(DomainEvent):
    """Event fired when a model is updated."""

    model_id: int = 0
    model_name: str = ""
    changes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelDeletedEvent(DomainEvent):
    """Event fired when a model is deleted."""

    model_id: int = 0
    model_name: str = ""


@dataclass
class FieldAddedEvent(DomainEvent):
    """Event fired when a field is added to a model."""

    model_id: int = 0
    field_id: int = 0
    field_name: str = ""
    field_type: str = ""


@dataclass
class FieldUpdatedEvent(DomainEvent):
    """Event fired when a field is updated."""

    field_id: int = 0
    field_name: str = ""
    changes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FieldDeletedEvent(DomainEvent):
    """Event fired when a field is deleted."""

    model_id: int = 0
    field_id: int = 0
    field_name: str = ""


@dataclass
class SchemaSyncedEvent(DomainEvent):
    """Event fired when model schema is synced to database."""

    model_id: int = 0
    model_name: str = ""
    changes: Dict[str, Any] = field(default_factory=dict)
