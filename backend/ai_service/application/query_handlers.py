"""
Query Handlers for AI operations.
"""
import logging
from typing import List, Dict, Any, Optional

from ..domain.services.tool_service import ToolService
from .queries import (
    GetConversationHistoryQuery,
    GetProjectContextQuery,
    GetToolDefinitionsQuery,
    GetConversationQuery,
    SearchConversationsQuery,
)

logger = logging.getLogger(__name__)


class GetConversationHistoryHandler:
    """Handles GetConversationHistoryQuery."""

    def handle(self, query: GetConversationHistoryQuery) -> List[Dict[str, Any]]:
        """Get conversation history for a project."""
        try:
            from backend.models import AIConversation

            q = AIConversation.query.filter_by(project_id=query.project_id)

            if query.user_id:
                q = q.filter_by(user_id=query.user_id)

            q = q.order_by(AIConversation.created_at.desc())
            conversations = q.limit(query.limit).all()

            return [
                {
                    "id": c.id,
                    "user_message": c.user_message,
                    "ai_response": c.ai_response,
                    "action_taken": c.action_taken,
                    "rating": c.rating,
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                }
                for c in conversations
            ]
        except Exception as e:
            logger.error(f"Failed to get conversation history: {e}")
            return []


class GetProjectContextHandler:
    """Handles GetProjectContextQuery."""

    def handle(self, query: GetProjectContextQuery) -> Dict[str, Any]:
        """Get project context for AI context injection."""
        try:
            from backend.models import Project, SysModel, Workflow

            project = Project.query.get(query.project_id)
            if not project:
                return {}

            models = SysModel.query.filter_by(
                project_id=query.project_id, is_active=True
            ).limit(20).all()

            workflows = Workflow.query.filter_by(
                project_id=query.project_id, is_active=True
            ).limit(10).all()

            return {
                "project_id": project.id,
                "project_name": project.name,
                "project_title": project.title,
                "models": [
                    {"name": m.name, "title": m.title, "fields_count": len(m.fields)}
                    for m in models
                ],
                "workflows": [
                    {"name": w.name, "trigger_event": w.trigger_event}
                    for w in workflows
                ],
            }
        except Exception as e:
            logger.error(f"Failed to get project context: {e}")
            return {}


class GetToolDefinitionsHandler:
    """Handles GetToolDefinitionsQuery."""

    def __init__(self, tool_service: ToolService):
        self.tool_service = tool_service

    def handle(self, query: GetToolDefinitionsQuery) -> List[Dict[str, Any]]:
        """Get available tool definitions."""
        return self.tool_service.get_tool_definitions()


class GetConversationHandler:
    """Handles GetConversationQuery."""

    def handle(self, query: GetConversationQuery) -> Optional[Dict[str, Any]]:
        """Get a specific conversation."""
        try:
            from backend.models import AIConversation

            conversation = AIConversation.query.get(query.conversation_id)
            if not conversation:
                return None

            return {
                "id": conversation.id,
                "project_id": conversation.project_id,
                "user_id": conversation.user_id,
                "user_message": conversation.user_message,
                "ai_response": conversation.ai_response,
                "action_taken": conversation.action_taken,
                "entities_created": conversation.entities_created,
                "rating": conversation.rating,
                "was_successful": conversation.was_successful,
                "created_at": conversation.created_at.isoformat() if conversation.created_at else None,
            }
        except Exception as e:
            logger.error(f"Failed to get conversation: {e}")
            return None


class SearchConversationsHandler:
    """Handles SearchConversationsQuery."""

    def handle(self, query: SearchConversationsQuery) -> List[Dict[str, Any]]:
        """Search conversations by content."""
        try:
            from backend.models import AIConversation

            conversations = AIConversation.query.filter(
                AIConversation.project_id == query.project_id,
                (
                    AIConversation.user_message.ilike(f"%{query.search_term}%") |
                    AIConversation.ai_response.ilike(f"%{query.search_term}%")
                )
            ).order_by(AIConversation.created_at.desc()).limit(query.limit).all()

            return [
                {
                    "id": c.id,
                    "user_message": c.user_message,
                    "ai_response": c.ai_response,
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                }
                for c in conversations
            ]
        except Exception as e:
            logger.error(f"Failed to search conversations: {e}")
            return []
