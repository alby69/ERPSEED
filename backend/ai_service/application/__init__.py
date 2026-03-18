"""
AI Service - CQRS Application Layer

Commands and Queries for AI interactions.
"""
from .commands import (
    SendMessageCommand,
    GenerateConfigCommand,
    CreateWorkflowCommand,
    CreateUIViewCommand,
    GenerateTestSuiteCommand,
)

from .queries import (
    GetConversationHistoryQuery,
    GetProjectContextQuery,
    GetToolDefinitionsQuery,
)

__all__ = [
    "SendMessageCommand",
    "GenerateConfigCommand",
    "CreateWorkflowCommand",
    "CreateUIViewCommand",
    "GenerateTestSuiteCommand",
    "GetConversationHistoryQuery",
    "GetProjectContextQuery",
    "GetToolDefinitionsQuery",
]
