"""
System Events - Standard event definitions for FlaskERP.

This module defines all standard domain events that can be published
across the system for decoupled communication.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum

from .event import DomainEvent


class EventCategory(Enum):
    """Event category classification."""

    ENTITY = "entity"
    USER = "user"
    PROJECT = "project"
    WORKFLOW = "workflow"
    SYSTEM = "system"
    INTEGRATION = "integration"


ENTITY_EVENTS = {
    # Model events
    "model.created": "A new model was created",
    "model.updated": "A model was updated",
    "model.deleted": "A model was deleted",
    "model.published": "A model was published",
    # Field events
    "field.created": "A field was added to a model",
    "field.updated": "A field was updated",
    "field.deleted": "A field was deleted",
    # Record events
    "record.created": "A record was created",
    "record.updated": "A record was updated",
    "record.deleted": "A record was deleted",
    # View events
    "view.created": "A view was created",
    "view.updated": "A view was updated",
    "view.deleted": "A view was deleted",
}

USER_EVENTS = {
    "user.created": "A new user was registered",
    "user.updated": "User profile was updated",
    "user.deleted": "A user was deleted",
    "user.login": "User logged in",
    "user.logout": "User logged out",
    "user.password_changed": "User changed password",
    "user.role_changed": "User role was changed",
}

PROJECT_EVENTS = {
    "project.created": "A new project was created",
    "project.updated": "Project settings were updated",
    "project.deleted": "A project was deleted",
    "project.member_added": "A member was added to project",
    "project.member_removed": "A member was removed from project",
}

WORKFLOW_EVENTS = {
    "workflow.started": "A workflow execution started",
    "workflow.completed": "A workflow execution completed",
    "workflow.failed": "A workflow execution failed",
    "workflow.step.completed": "A workflow step completed",
    "workflow.step.failed": "A workflow step failed",
}

INTEGRATION_EVENTS = {
    "webhook.triggered": "A webhook was triggered",
    "api.called": "An external API was called",
    "sync.started": "A synchronization process started",
    "sync.completed": "A synchronization process completed",
}


@dataclass
class EntityEvent(DomainEvent):
    """Base event for entity operations."""

    entity_type: str = ""
    entity_id: Optional[int] = None
    changes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelCreatedEvent(EntityEvent):
    """Fired when a model is created."""

    entity_type: str = "model"


@dataclass
class ModelUpdatedEvent(EntityEvent):
    """Fired when a model is updated."""

    entity_type: str = "model"


@dataclass
class ModelDeletedEvent(EntityEvent):
    """Fired when a model is deleted."""

    entity_type: str = "model"


@dataclass
class RecordCreatedEvent(EntityEvent):
    """Fired when a record is created."""

    entity_type: str = "record"
    model_name: str = ""


@dataclass
class RecordUpdatedEvent(EntityEvent):
    """Fired when a record is updated."""

    entity_type: str = "record"
    model_name: str = ""


@dataclass
class RecordDeletedEvent(EntityEvent):
    """Fired when a record is deleted."""

    entity_type: str = "record"
    model_name: str = ""


@dataclass
class UserEvent(DomainEvent):
    """Base event for user operations."""

    userId: int = 0
    username: str = ""


@dataclass
class UserCreatedEvent(UserEvent):
    """Fired when a user is created."""

    event_type: str = "user.created"


@dataclass
class UserLoggedInEvent(UserEvent):
    """Fired when a user logs in."""

    event_type: str = "user.login"


@dataclass
class UserLoggedOutEvent(UserEvent):
    """Fired when a user logs out."""

    event_type: str = "user.logout"


@dataclass
class ProjectEvent(DomainEvent):
    """Base event for project operations."""

    projectId: int = 0
    project_name: str = ""


@dataclass
class ProjectCreatedEvent(ProjectEvent):
    """Fired when a project is created."""

    event_type: str = "project.created"


@dataclass
class ProjectDeletedEvent(ProjectEvent):
    """Fired when a project is deleted."""

    event_type: str = "project.deleted"


@dataclass
class WorkflowEvent(DomainEvent):
    """Base event for workflow operations."""

    workflowId: int = 0
    workflow_name: str = ""
    execution_id: Optional[int] = None


@dataclass
class WorkflowStartedEvent(WorkflowEvent):
    """Fired when a workflow starts."""

    event_type: str = "workflow.started"


@dataclass
class WorkflowCompletedEvent(WorkflowEvent):
    """Fired when a workflow completes."""

    event_type: str = "workflow.completed"


@dataclass
class WorkflowFailedEvent(WorkflowEvent):
    """Fired when a workflow fails."""

    event_type: str = "workflow.failed"
    error: str = ""


@dataclass
class IntegrationEvent(DomainEvent):
    """Base event for integration operations."""

    integration_name: str = ""
    status: str = ""


@dataclass
class WebhookTriggeredEvent(IntegrationEvent):
    """Fired when a webhook is triggered."""

    event_type: str = "webhook.triggered"
    webhook_url: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)


def get_all_event_types() -> Dict[str, str]:
    """Get all defined event types with descriptions."""
    all_events = {}
    all_events.update(ENTITY_EVENTS)
    all_events.update(USER_EVENTS)
    all_events.update(PROJECT_EVENTS)
    all_events.update(WORKFLOW_EVENTS)
    all_events.update(INTEGRATION_EVENTS)
    return all_events


def register_default_subscriptions(event_bus) -> None:
    """Register default event handlers for the event bus.

    This sets up internal system handlers for standard events.
    """
    pass
