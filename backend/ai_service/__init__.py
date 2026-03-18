"""
AI Service Package - CQRS Architecture for AI.

This package provides a clean CQRS architecture for AI interactions:
- Commands: SendMessage, GenerateConfig, CreateWorkflow, etc.
- Queries: GetConversationHistory, GetProjectContext, etc.
- Handlers: Process commands and queries
- Domain: Core business logic (ChatService, ToolService)
- Infrastructure: Adapters for LLM providers
"""
from .application.commands import (
    SendMessageCommand,
    GenerateConfigCommand,
    CreateWorkflowCommand,
    CreateUIViewCommand,
    GenerateTestSuiteCommand,
)
from .application.queries import (
    GetConversationHistoryQuery,
    GetProjectContextQuery,
    GetToolDefinitionsQuery,
    GetConversationQuery,
    SearchConversationsQuery,
)
from .application.handlers import (
    SendMessageHandler,
    GenerateConfigHandler,
    CreateWorkflowHandler,
    CreateUIViewHandler,
    GenerateTestSuiteHandler,
)
from .application.query_handlers import (
    GetConversationHistoryHandler,
    GetProjectContextHandler,
    GetToolDefinitionsHandler,
    GetConversationHandler,
    SearchConversationsHandler,
)
from .domain.services.chat_service import ChatService
from .domain.services.tool_service import ToolService, get_tool_service
from .infrastructure.adapters.factory import AdapterFactory, get_adapter

__all__ = [
    # Commands
    "SendMessageCommand",
    "GenerateConfigCommand",
    "CreateWorkflowCommand",
    "CreateUIViewCommand",
    "GenerateTestSuiteCommand",
    # Queries
    "GetConversationHistoryQuery",
    "GetProjectContextQuery",
    "GetToolDefinitionsQuery",
    "GetConversationQuery",
    "SearchConversationsQuery",
    # Handlers
    "SendMessageHandler",
    "GenerateConfigHandler",
    "CreateWorkflowHandler",
    "CreateUIViewHandler",
    "GenerateTestSuiteHandler",
    "GetConversationHistoryHandler",
    "GetProjectContextHandler",
    "GetToolDefinitionsHandler",
    "GetConversationHandler",
    "SearchConversationsHandler",
    # Domain
    "ChatService",
    "ToolService",
    "get_tool_service",
    # Infrastructure
    "AdapterFactory",
    "get_adapter",
]
