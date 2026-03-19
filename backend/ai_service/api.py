"""
AI Service REST API - Flask-Smorest Blueprint

This module provides REST API endpoints for the AI Service using the CQRS pattern.
"""

from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields

from backend.ai_service import (
    SendMessageCommand,
    GenerateConfigCommand,
    CreateWorkflowCommand,
    CreateUIViewCommand,
    GenerateTestSuiteCommand,
    SendMessageHandler,
    GenerateConfigHandler,
    get_adapter,
)

blp = Blueprint("ai", __name__, url_prefix="/api/ai", description="AI Assistant API")


class ChatRequestSchema(Schema):
    message = fields.String(required=True)
    project_id = fields.Integer(required=False, allow_none=True)
    context = fields.Dict(required=False, allow_none=True)
    tools = fields.List(fields.Dict(), required=False)


class GenerateConfigSchema(Schema):
    request = fields.String(required=True)
    project_id = fields.Integer(required=False, allow_none=True)


@blp.route("/chat")
class AIChat(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(ChatRequestSchema)
    @blp.response(200)
    def post(self, args):
        """Send a chat message to the AI assistant"""
        try:
            user_id = get_jwt_identity()
            message = args.get("message", "")
            project_id = args.get("project_id")
            context = args.get("context", {})
            tools = args.get("tools")

            if not message:
                return {"success": False, "error": "Missing message parameter"}, 400

            from backend.ai_service import SendMessageHandler
            from backend.ai_service.application.commands import SendMessageCommand
            
            handler = SendMessageHandler()
            command = SendMessageCommand(
                user_id=user_id,
                message=message,
                project_id=project_id,
                context=context,
                tools=tools
            )
            
            result = handler.handle(command)
            return result
        except Exception as e:
            import logging
            logging.error(f"AI chat error: {e}")
            abort(500, message=f"Internal error: {str(e)}")


@blp.route("/generate")
class AIGenerate(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(GenerateConfigSchema)
    @blp.response(200)
    def post(self, args):
        """Generate ERP configuration from natural language"""
        try:
            user_id = get_jwt_identity()
            user_request = args.get("request", "")
            project_id = args.get("project_id", 1)

            if not user_request:
                return {"success": False, "error": "Missing request parameter"}, 400

            from backend.ai_service import GenerateConfigHandler
            from backend.ai_service.application.commands import GenerateConfigCommand
            
            handler = GenerateConfigHandler()
            command = GenerateConfigCommand(
                user_id=user_id,
                request=user_request,
                project_id=project_id
            )
            
            result = handler.handle(command)
            return result
        except Exception as e:
            import logging
            logging.error(f"AI generate error: {e}")
            abort(500, message=f"Internal error: {str(e)}")


@blp.route("/conversations/<int:conversation_id>")
class AIConversation(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, conversation_id):
        """Get conversation history"""
        try:
            from backend.ai_service import GetConversationHandler
            from backend.ai_service.application.queries import GetConversationQuery
            
            handler = GetConversationHandler()
            query = GetConversationQuery(conversation_id=conversation_id)
            
            result = handler.handle(query)
            return result
        except Exception as e:
            import logging
            logging.error(f"AI conversation error: {e}")
            abort(500, message=f"Internal error: {str(e)}")


@blp.route("/tools")
class AITools(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        """Get available AI tools"""
        try:
            from backend.ai_service import GetToolDefinitionsHandler
            from backend.ai_service.application.queries import GetToolDefinitionsQuery
            
            handler = GetToolDefinitionsHandler()
            query = GetToolDefinitionsQuery()
            
            result = handler.handle(query)
            return result
        except Exception as e:
            import logging
            logging.error(f"AI tools error: {e}")
            abort(500, message=f"Internal error: {str(e)}")
