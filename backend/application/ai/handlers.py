"""
AI Handlers - Handle AI commands and queries.
"""
import logging
from backend.shared.handlers import CommandHandler, CommandResult
from backend.shared.commands import Command

from backend.application.ai.commands import (
    SendMessageCommand, GenerateConfigCommand, CreateWorkflowCommand,
    CreateUIViewCommand, GenerateTestSuiteCommand, GetConversationHistoryQuery,
    GetProjectContextQuery, GetToolDefinitionsQuery,
)
from backend.infrastructure.ai.services import ChatService, ToolService

logger = logging.getLogger(__name__)


class SendMessageHandler(CommandHandler):
    def __init__(self, chat_service: ChatService, tool_service: ToolService):
        self.chat_service = chat_service; self.tool_service = tool_service
    
    @property
    def command_type(self) -> str: return "SendMessage"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, SendMessageCommand): return CommandResult.error(f"Invalid command type: {type(command)}")
        try:
            context = command.context or {}
            context["project_id"] = command.project_id
            context["user_id"] = command.user_id
            result = self.chat_service.chat(command.message, tools=self.tool_service.get_tool_definitions() if self.tool_service else None, context=context)
            self._save_conversation(command, result)
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return CommandResult.error(f"Failed to send message: {str(e)}")
    
    def _save_conversation(self, command, result):
        try:
            from backend.models import AIConversation
            from backend.extensions import db
            conv = AIConversation(project_id=command.project_id, user_id=command.user_id,
                user_message=command.message, ai_response=result.get("content"))
            db.session.add(conv)
            db.session.commit()
        except Exception as e:
            logger.error(f"Failed to save conversation: {e}")


class GenerateConfigHandler(CommandHandler):
    def __init__(self, chat_service: ChatService, tool_service: ToolService):
        self.chat_service = chat_service; self.tool_service = tool_service
    
    @property
    def command_type(self) -> str: return "GenerateConfig"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, GenerateConfigCommand): return CommandResult.error(f"Invalid command type: {type(command)}")
        try:
            prompt = f"Generate configuration for: {command.user_request}"
            result = self.chat_service.chat(prompt, context={"project_id": command.project_id, "mode": "generate_config"},
                tools=self.tool_service.get_tool_definitions() if self.tool_service else None)
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error generating config: {e}")
            return CommandResult.error(f"Failed to generate config: {str(e)}")


class CreateWorkflowHandler(CommandHandler):
    def __init__(self, chat_service: ChatService, tool_service: ToolService):
        self.chat_service = chat_service; self.tool_service = tool_service
    
    @property
    def command_type(self) -> str: return "CreateWorkflow"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, CreateWorkflowCommand): return CommandResult.error(f"Invalid command type: {type(command)}")
        try:
            prompt = f"Create workflow: {command.workflow_description}"
            result = self.chat_service.chat(prompt, context={"project_id": command.project_id, "mode": "create_workflow"},
                tools=self.tool_service.get_tool_definitions() if self.tool_service else None)
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error creating workflow: {e}")
            return CommandResult.error(f"Failed to create workflow: {str(e)}")


class CreateUIViewHandler(CommandHandler):
    def __init__(self, chat_service: ChatService, tool_service: ToolService):
        self.chat_service = chat_service; self.tool_service = tool_service
    
    @property
    def command_type(self) -> str: return "CreateUIView"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, CreateUIViewCommand): return CommandResult.error(f"Invalid command type: {type(command)}")
        try:
            prompt = f"Create {command.view_type} view: {command.view_description}"
            result = self.chat_service.chat(prompt, context={"project_id": command.project_id, "model_id": command.model_id, "mode": "create_ui_view"},
                tools=self.tool_service.get_tool_definitions() if self.tool_service else None)
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error creating UI view: {e}")
            return CommandResult.error(f"Failed to create UI view: {str(e)}")


class GenerateTestSuiteHandler(CommandHandler):
    def __init__(self, chat_service: ChatService, tool_service: ToolService):
        self.chat_service = chat_service; self.tool_service = tool_service
    
    @property
    def command_type(self) -> str: return "GenerateTestSuite"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, GenerateTestSuiteCommand): return CommandResult.error(f"Invalid command type: {type(command)}")
        try:
            prompt = f"Generate tests for {command.model_name}: {command.test_description}"
            result = self.chat_service.chat(prompt, context={"project_id": command.project_id, "model_name": command.model_name, "mode": "generate_tests"},
                tools=self.tool_service.get_tool_definitions() if self.tool_service else None)
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error generating test suite: {e}")
            return CommandResult.error(f"Failed to generate test suite: {str(e)}")


class GetToolDefinitionsHandler(CommandHandler):
    def __init__(self, tool_service: ToolService):
        self.tool_service = tool_service
    
    @property
    def command_type(self) -> str: return "GetToolDefinitions"
    
    def handle(self, command: Command) -> CommandResult:
        if not isinstance(command, GetToolDefinitionsQuery): return CommandResult.error(f"Invalid command type: {type(command)}")
        tools = self.tool_service.get_tool_definitions() if self.tool_service else []
        return CommandResult.ok({"tools": tools, "count": len(tools)})
