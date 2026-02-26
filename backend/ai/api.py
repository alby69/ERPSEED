"""
AI Assistant API endpoints for FlaskERP
"""

from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields

from backend.ai.service import get_ai_service

blp = Blueprint("ai", __name__, url_prefix="/api/ai", description="AI Assistant API")


class ChatRequestSchema(Schema):
    message = fields.String(required=True)
    project_id = fields.Integer(required=False, allow_none=True)
    context = fields.Dict(required=False, allow_none=True)


class GenerateConfigSchema(Schema):
    request = fields.String(required=True)
    project_id = fields.Integer(required=True)


@blp.route("/chat")
class AIChat(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(ChatRequestSchema)
    @blp.response(200)
    def post(self):
        """Chat with the AI assistant"""
        data = request.json
        message = data.get("message")
        context = data.get("context")

        ai_service = get_ai_service()
        result = ai_service.chat(message, context)

        return result


@blp.route("/generate")
class AIGenerate(MethodView):
    # Temporarily without auth for testing
    @blp.response(200)
    def post(self):
        """
        Generate ERP configuration from natural language

        Example request:
        {
            "request": "Create a module for suppliers with name, address and email",
            "project_id": 1
        }

        Example response:
        {
            "success": true,
            "config": {
                "models": [
                    {
                        "name": "Fornitore",
                        "table": "fornitori",
                        "fields": [...]
                    }
                ]
            },
            "created_models": ["Fornitore"],
            "message": "Ho creato il modello Fornitori con i campi richiesti."
        }
        """
        try:
            data = request.json or {}
            user_request = data.get("request", "")
            project_id = data.get("project_id", 1)

            if not user_request:
                return {"success": False, "error": "Missing request parameter"}, 400

            ai_service = get_ai_service()
            result = ai_service.generate_erp_config(user_request, project_id)

            if not result.get("success"):
                return {
                    "success": False,
                    "error": result.get("error", "Errore nella generazione"),
                }, 400

            # Extract created models count
            config = result.get("config", {})
            models = config.get("models", [])
            created_models = [m.get("name", "Unknown") for m in models]

            # Generate human-readable message
            if len(created_models) == 1:
                message = (
                    f"Ho creato il modello {created_models[0]} con i campi richiesti."
                )
            elif len(created_models) > 1:
                message = f"Ho creato i modelli: {', '.join(created_models)}."
            else:
                message = "Configurazione generata."

            return {
                "success": True,
                "config": config,
                "created_models": created_models,
                "message": message,
            }
        except Exception as e:
            import logging

            logging.error(f"AI generate error: {e}")
            abort(500, message=f"Errore interno: {str(e)}")


@blp.route("/suggestions")
class AISuggestions(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(GenerateConfigSchema)
    @blp.response(200)
    def post(self):
        """Get AI suggestions for improving a model"""
        data = request.json
        model_config = data.get("config", {})

        ai_service = get_ai_service()
        suggestions = ai_service.suggest_improvements(model_config)

        return {"success": True, "suggestions": suggestions}


@blp.route("/models")
class AIModels(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200)
    def get(self):
        """Get available AI models"""
        return {
            "models": [
                {
                    "id": "nvidia/nemotron-nano-9b-v2:free",
                    "name": "NVIDIA Nemotron Nano",
                    "description": "Fast, efficient model (Free)",
                    "provider": "OpenRouter",
                },
                {
                    "id": "qwen/qwen3-coder:free",
                    "name": "Qwen3 Coder",
                    "description": "Specialized in code generation (Free)",
                    "provider": "OpenRouter",
                },
            ],
            "current": "nvidia/nemotron-nano-9b-v2:free",
        }
