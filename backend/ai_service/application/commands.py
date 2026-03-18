"""
AI Commands - CQRS Commands for AI operations.

Each command represents an action that modifies state.
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any


@dataclass
class SendMessageCommand:
    """Send a message to the AI assistant."""
    project_id: int
    user_id: int
    message: str
    conversation_id: Optional[int] = None
    context: Optional[Dict[str, Any]] = None


@dataclass
class GenerateConfigCommand:
    """Generate a configuration from natural language."""
    project_id: int
    user_id: int
    user_request: str
    apply_immediately: bool = False


@dataclass
class CreateWorkflowCommand:
    """Create a workflow from natural language description."""
    project_id: int
    user_id: int
    workflow_description: str
    trigger_event: Optional[str] = None


@dataclass
class CreateUIViewCommand:
    """Create a UI view from natural language description."""
    project_id: int
    user_id: int
    model_id: int
    view_description: str
    view_type: str = "list"


@dataclass
class GenerateTestSuiteCommand:
    """Generate test suite from natural language."""
    project_id: int
    user_id: int
    model_name: str
    test_description: str
