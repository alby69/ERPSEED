"""
AI Queries - CQRS Queries for AI operations.

Each query represents a read operation that doesn't modify state.
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any


@dataclass
class GetConversationHistoryQuery:
    """Get conversation history for a project."""
    project_id: int
    user_id: Optional[int] = None
    limit: int = 50


@dataclass
class GetProjectContextQuery:
    """Get project context for AI context injection."""
    project_id: int


@dataclass
class GetToolDefinitionsQuery:
    """Get available tool definitions for AI."""
    provider: Optional[str] = None
    include_custom: bool = True


@dataclass
class GetConversationQuery:
    """Get a specific conversation."""
    conversation_id: int


@dataclass
class SearchConversationsQuery:
    """Search conversations by content."""
    project_id: int
    search_term: str
    limit: int = 20
