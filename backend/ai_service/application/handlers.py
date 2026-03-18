"""
Command Handlers for AI operations.
"""
import logging
from typing import Dict, Any, Optional

from ..domain.services.chat_service import ChatService
from ..domain.services.tool_service import ToolService
from ..infrastructure.adapters.factory import AdapterFactory
from .commands import (
    SendMessageCommand,
    GenerateConfigCommand,
    CreateWorkflowCommand,
    CreateUIViewCommand,
    GenerateTestSuiteCommand,
)

logger = logging.getLogger(__name__)


class SendMessageHandler:
    """Handles SendMessageCommand."""

    def __init__(self, chat_service: ChatService, tool_service: ToolService):
        self.chat_service = chat_service
        self.tool_service = tool_service

    def handle(self, command: SendMessageCommand) -> Dict[str, Any]:
        """Process a message and return AI response."""
        context = command.context or {}
        context["project_id"] = command.project_id
        context["user_id"] = command.user_id

        result = self.chat_service.chat(
            user_message=command.message,
            context=context,
            tools=self.tool_service.get_tool_definitions(),
        )

        self._save_conversation(
            project_id=command.project_id,
            user_id=command.user_id,
            user_message=command.message,
            ai_response=result.get("content"),
            action_taken=result.get("tool_calls", [{}])[0].get("name") if result.get("tool_calls") else None,
        )

        return result

    def _save_conversation(
        self,
        project_id: int,
        user_id: int,
        user_message: str,
        ai_response: str,
        action_taken: Optional[str] = None,
    ):
        """Save conversation to database."""
        try:
            from backend.models import AIConversation, db
            conversation = AIConversation(
                project_id=project_id,
                user_id=user_id,
                user_message=user_message,
                ai_response=ai_response,
                action_taken=action_taken,
            )
            db.session.add(conversation)
            db.session.commit()
        except Exception as e:
            logger.error(f"Failed to save conversation: {e}")


class GenerateConfigHandler:
    """Handles GenerateConfigCommand."""

    def __init__(self, chat_service: ChatService, tool_service: ToolService):
        self.chat_service = chat_service
        self.tool_service = tool_service

    def handle(self, command: GenerateConfigCommand) -> Dict[str, Any]:
        """Generate configuration from natural language."""
        context = {
            "project_id": command.project_id,
            "user_id": command.user_id,
            "mode": "generate_config",
        }

        prompt = f"Generate configuration for: {command.user_request}"

        result = self.chat_service.chat(
            user_message=prompt,
            context=context,
            tools=self.tool_service.get_tool_definitions(),
        )

        return result


class CreateWorkflowHandler:
    """Handles CreateWorkflowCommand."""

    def __init__(self, chat_service: ChatService, tool_service: ToolService):
        self.chat_service = chat_service
        self.tool_service = tool_service

    def handle(self, command: CreateWorkflowCommand) -> Dict[str, Any]:
        """Create workflow from description."""
        context = {
            "project_id": command.project_id,
            "user_id": command.user_id,
            "mode": "create_workflow",
        }

        prompt = f"Create workflow: {command.workflow_description}"

        result = self.chat_service.chat(
            user_message=prompt,
            context=context,
            tools=self.tool_service.get_tool_definitions(),
        )

        return result


class CreateUIViewHandler:
    """Handles CreateUIViewCommand."""

    def __init__(self, chat_service: ChatService, tool_service: ToolService):
        self.chat_service = chat_service
        self.tool_service = tool_service

    def handle(self, command: CreateUIViewCommand) -> Dict[str, Any]:
        """Create UI view from description."""
        context = {
            "project_id": command.project_id,
            "user_id": command.user_id,
            "model_id": command.model_id,
            "mode": "create_ui_view",
        }

        prompt = f"Create {command.view_type} view: {command.view_description}"

        result = self.chat_service.chat(
            user_message=prompt,
            context=context,
            tools=self.tool_service.get_tool_definitions(),
        )

        return result


class GenerateTestSuiteHandler:
    """Handles GenerateTestSuiteCommand."""

    def __init__(self, chat_service: ChatService, tool_service: ToolService):
        self.chat_service = chat_service
        self.tool_service = tool_service

    def handle(self, command: GenerateTestSuiteCommand) -> Dict[str, Any]:
        """Generate test suite from description."""
        context = {
            "project_id": command.project_id,
            "user_id": command.user_id,
            "model_name": command.model_name,
            "mode": "generate_tests",
        }

        prompt = f"Generate tests for {command.model_name}: {command.test_description}"

        result = self.chat_service.chat(
            user_message=prompt,
            context=context,
            tools=self.tool_service.get_tool_definitions(),
        )

        return result
