"""
AI Assistant API endpoints for FlaskERP
"""

from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields

from modules.ai.service import get_ai_service

blp = Blueprint("ai", __name__, url_prefix="/api/ai", description="AI Assistant API")


class ChatRequestSchema(Schema):
    message = fields.String(required=True)
    project_id = fields.Integer(required=False, allow_none=True)
    context = fields.Dict(required=False, allow_none=True)


class GenerateConfigSchema(Schema):
    request = fields.String(required=True)
    project_id = fields.Integer(required=False, allow_none=True)


@blp.route("/generate")
class AIGenerate(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(GenerateConfigSchema)
    @blp.response(200)
    def post(self, args):
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
            user_request = args.get("request", "")
            project_id = args.get("project_id", 1)

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

        # Return basic suggestions without calling the AI for now
        suggestions = []

        # Check for missing common fields
        if model_config:
            fields = model_config.get("fields", [])
            field_names = [f.get("name", "").lower() for f in fields]

            if "name" not in field_names and "title" not in field_names:
                suggestions.append(
                    "Aggiungi un campo 'name' o 'title' per l'identificazione"
                )
            if "created_at" not in field_names:
                suggestions.append(
                    "Considera aggiungere 'created_at' per tracciare la creazione"
                )
            if "updated_at" not in field_names:
                suggestions.append(
                    "Considera aggiungere 'updated_at' per tracciare le modifiche"
                )

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


@blp.route("/apply")
class AIApply(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200)
    def post(self):
        """
        Apply generated ERP configuration to the database.

        Example request:
        {
            "config": {
                "models": [
                    {
                        "name": "Fornitore",
                        "table": "fornitori",
                        "fields": [
                            {"name": "nome", "type": "string", "label": "Nome"},
                            {"name": "email", "type": "string", "label": "Email"}
                        ]
                    }
                ]
            },
            "project_id": 1
        }

        Example response:
        {
            "success": true,
            "created_models": ["Fornitore"],
            "created_fields": {"Fornitore": ["nome", "email"]},
            "message": "Modello creato con successo!"
        }
        """
        try:
            import logging

            logger = logging.getLogger(__name__)

            # Get current user
            current_user_id = get_jwt_identity()
            logger.info(f"AI Apply requested by user {current_user_id}")

            data = request.json or {}

            config = data.get("config", {})
            project_id = data.get("project_id")

            # Import services
            from modules.builder.service import get_builder_service as BuilderService
            from extensions import db
            from core.utils.utils import generate_create_table_sql
            from models import Project
            from sqlalchemy import text

            builder_service = BuilderService()

            if not config:
                abort(400, message="Missing config parameter")

            # Validate and get project - fallback to first available project if needed
            project = db.session.get(Project, project_id) if project_id else None
            if not project:
                # Try to find any available project
                available_project = db.session.query(Project).first()
                if available_project:
                    project_id = available_project.id
                    project = available_project
                else:
                    abort(
                        404,
                        message="Nessun progetto trovato. Creane uno prima di usare l'AI Assistant.",
                    )

            schema_name = f"project_{project_id}"

            # Create schema if it doesn't exist
            try:
                db.session.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
                db.session.commit()
            except Exception as e:
                logger.warning(f"[AI_APPLY] Could not create schema {schema_name}: {e}")
                db.session.rollback()

            created_models = []
            created_fields = {}
            errors = []

            models_config = config.get("models", [])

            for model_config in models_config:
                try:
                    model_name = model_config.get("name", "")
                    table_name = model_config.get("table", model_name.lower())
                    model_title = model_config.get("title", model_name)
                    model_description = model_config.get("description", "")
                    fields_config = model_config.get("fields", [])

                    if not model_name:
                        errors.append(f"Model name missing in config")
                        continue

                    # Create the model
                    try:
                        new_model = builder_service.create_model(
                            project_id=project_id,
                            name=table_name,
                            title=model_title,
                            description=model_description,
                        )
                    except Exception as e:
                        errors.append(f"Model {model_name}: {str(e)}")
                        continue

                    model_fields_created = []

                    # Add fields
                    for field_config in fields_config:
                        field_name = field_config.get("name", "")
                        field_type = field_config.get("type", "string")
                        field_label = field_config.get("label", field_name.title())

                        if not field_name:
                            continue

                        # Map AI types to builder types
                        type_mapping = {
                            "text": "text",
                            "number": "decimal",
                            "boolean": "boolean",
                            "date": "date",
                            "datetime": "datetime",
                            "select": "select",
                            "relation": "relation",
                        }
                        mapped_type = type_mapping.get(field_type, field_type)

                        # Build field kwargs
                        field_kwargs = {
                            "title": field_label,
                            "required": field_config.get("required", False),
                        }

                        # Handle select options
                        if mapped_type == "select" and "options" in field_config:
                            import json

                            field_kwargs["options"] = json.dumps(
                                field_config["options"]
                            )

                        # Handle relation
                        if mapped_type == "relation" and "relation_to" in field_config:
                            field_kwargs["relation_to"] = field_config["relation_to"]
                            field_kwargs["relation_type"] = field_config.get(
                                "relation_type", "many-to-one"
                            )

                        try:
                            builder_service.create_field(
                                model_id=new_model.id,
                                name=field_name,
                                field_type=mapped_type,
                                **field_kwargs,
                            )
                            model_fields_created.append(field_name)
                        except Exception as e:
                            errors.append(f"Field {field_name}: {str(e)}")

                    # Generate and execute CREATE TABLE
                    try:
                        # Refresh model to load fields
                        db.session.refresh(new_model)

                        sql = generate_create_table_sql(new_model, schema=schema_name)
                        db.session.execute(text(sql))
                        db.session.commit()
                    except Exception as e:
                        errors.append(f"Table creation for {table_name}: {str(e)}")
                        db.session.rollback()

                    created_models.append(model_name)
                    created_fields[model_name] = model_fields_created

                except Exception as e:
                    errors.append(
                        f"Model {model_config.get('name', 'unknown')}: {str(e)}"
                    )
                    continue

            if not created_models:
                return {
                    "success": False,
                    "error": "Nessun modello creato. " + "; ".join(errors)
                    if errors
                    else "Errore sconosciuto",
                    "errors": errors,
                }, 400

            message = (
                f"Creato {len(created_models)} modello(i): {', '.join(created_models)}"
            )
            if errors:
                message += f". Alcuni errori: {'; '.join(errors[:3])}"

            return {
                "success": True,
                "created_models": created_models,
                "created_fields": created_fields,
                "message": message,
                "errors": errors if errors else None,
            }

        except Exception as e:
            import logging

            logging.error(f"AI apply error: {e}")
            import traceback

            traceback.print_exc()
            abort(500, message=f"Errore interno: {str(e)}")


class ConversationSchema(Schema):
    project_id = fields.Integer(required=True)
    limit = fields.Integer(required=False, load_default=20)


class FeedbackSchema(Schema):
    conversation_id = fields.Integer(required=True)
    was_successful = fields.Boolean(required=True)
    user_correction = fields.String(required=False, allow_none=True)
    rating = fields.Integer(required=False, allow_none=True)


@blp.route("/conversations")
class AIConversations(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(ConversationSchema)
    @blp.response(200)
    def get(self, args):
        """Get conversation history for a project"""
        from models import AIConversation

        project_id = args.get("project_id")
        limit = args.get("limit", 20)

        if not project_id:
            return {"success": False, "error": "project_id required"}, 400

        conversations = (
            AIConversation.query.filter_by(project_id=project_id)
            .order_by(AIConversation.created_at.desc())
            .limit(limit)
            .all()
        )

        return {
            "success": True,
            "conversations": [
                {
                    "id": c.id,
                    "user_message": c.user_message,
                    "ai_response": c.ai_response[:200] if c.ai_response else None,
                    "was_successful": c.was_successful,
                    "rating": c.rating,
                    "action_taken": c.action_taken,
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                }
                for c in conversations
            ],
        }


@blp.route("/feedback")
class AIFeedback(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(FeedbackSchema)
    @blp.response(200)
    def post(self, args):
        """Save feedback for a conversation (for learning)"""
        from models import AIConversation

        conversation_id = args.get("conversation_id")
        was_successful = args.get("was_successful", False)
        user_correction = args.get("user_correction")
        rating = args.get("rating")

        conversation = AIConversation.query.get(conversation_id)
        if not conversation:
            return {"success": False, "error": "Conversation not found"}, 404

        conversation.was_successful = was_successful
        if user_correction:
            conversation.user_correction = user_correction
        if rating:
            conversation.rating = rating

        try:
            from extensions import db

            db.session.commit()
            return {"success": True, "message": "Feedback salvato"}
        except Exception as e:
            return {"success": False, "error": str(e)}, 500
