"""
Handler Base Classes - Base classes for all command handlers in the system.

A Handler processes a Command and returns a CommandResult.
Handlers are stateless and should be easily testable.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from backend.shared.commands import Command
from backend.shared.events.event import DomainEvent


@dataclass
class CommandResult:
    """Standard result returned by all handlers."""

    success: bool = True
    data: Any = None
    error: Optional[str] = None
    errors: List[str] = field(default_factory=list)
    events: List[DomainEvent] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary (JSON-serializable)."""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "errors": self.errors,
            "events": [
                {"event_type": e.event_type, "payload": e.payload}
                for e in self.events
            ],
            "metadata": self.metadata,
        }

    @classmethod
    def ok(cls, data: Any = None, metadata: Dict = None) -> "CommandResult":
        """Create a success result."""
        return cls(success=True, data=data, metadata=metadata or {})

    @classmethod
    def error(cls, message: str, errors: List[str] = None) -> "CommandResult":
        """Create an error result."""
        return cls(
            success=False,
            error=message,
            errors=errors or [message]
        )


class CommandHandler(ABC):
    """Base class for all command handlers."""

    @abstractmethod
    def handle(self, command: Command) -> CommandResult:
        """
        Process a command and return a result.

        Args:
            command: The command to process

        Returns:
            CommandResult with success/data or error
        """
        pass

    @property
    @abstractmethod
    def command_type(self) -> str:
        """Return the command type this handler processes."""
        pass


class CreateHandler(CommandHandler):
    """Base class for create command handlers."""

    @property
    def command_type(self) -> str:
        return "create"


class UpdateHandler(CommandHandler):
    """Base class for update command handlers."""

    @property
    def command_type(self) -> str:
        return "update"


class DeleteHandler(CommandHandler):
    """Base class for delete command handlers."""

    @property
    def command_type(self) -> str:
        return "delete"


class QueryHandler(CommandHandler):
    """Base class for query handlers."""

    @property
    def command_type(self) -> str:
        return "query"
