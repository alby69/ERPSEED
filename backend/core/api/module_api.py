"""
Module Dynamic API - Routing dinamico per moduli pubblicati.

Espone API automaticamente basate sui modelli contenuti nel modulo:
- CRUD automatico per ogni SysModel
- Possibilità di custom endpoints
"""

from flask import request, jsonify
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_smorest import Blueprint, abort
from marshmallow import fields

from backend.extensions import db
from backend.modules.dynamic_api.services.dynamic_api_service import DynamicApiService

blp = Blueprint("module_api", __name__, url_prefix="/api/modules")


class ModuleApiService:
    """Service per gestire le API dei moduli."""

    def __init__(self):
        self.dynamic_api = DynamicApiService()

    def get_module_by_name(self, module_name, projectId):
        """Trova un modulo pubblicato per nome."""
        from backend.core.models.module import Module
        from backend.models import Project

        module = Module.query.filter(
            Module.name == module_name,
            Module.status == "published",
        ).join(Module.projects).filter(Project.id == projectId).first() # type: ignore

        if not module:
            abort(404, message=f"Module '{module_name}' not found or not published")

        return module

    def get_module_models(self, module):
        """Ritorna i modelli contenuti nel modulo."""
        # Usa la relazione corretta dal modello Module
        if hasattr(module, "models"):
            return list(module.models)
        return []


module_api_service = ModuleApiService()


@blp.route("/<string:module_name>")
class ModuleApiRoot(MethodView):
    """Root endpoint per il modulo."""

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, {"type": "object"})
    def get(self, module_name):
        """Info sul modulo e modelli disponibili."""
        userId = get_jwt_identity()
        from backend.models import User

        user = db.session.get(User, userId)

        if not user:
            abort(401, message="User not found")

        # Trova il progetto dell'utente
        projectId = getattr(user, "current_projectId", None) or 1

        module = module_api_service.get_module_by_name(module_name, projectId)
        models = module_api_service.get_module_models(module)

        return {
            "module": {
                "name": module.name,
                "title": module.title,
                "description": module.description,
                "version": module.version,
            },
            "endpoints": {
                "CRUD": {
                    model.name: {
                        "list": f"/api/modules/{module_name}/{model.name}",
                        "get": f"/api/modules/{module_name}/{model.name}/{{id}}",
                        "create": f"/api/modules/{module_name}/{model.name}",
                        "update": f"/api/modules/{module_name}/{model.name}/{{id}}",
                        "delete": f"/api/modules/{module_name}/{model.name}/{{id}}",
                    }
                    for model in models
                },
                "custom": module.api_definition.get("endpoints", [])
                if module.api_definition
                else [],
            },
        }


@blp.route("/<string:module_name>/<string:model_name>")
class ModuleModelList(MethodView):
    """Lista e creazione record per un modello nel modulo."""

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, {"type": "object"})
    def get(self, module_name, model_name):
        """Lista record del modello."""
        userId = get_jwt_identity()
        from backend.models import User

        user = db.session.get(User, userId)

        if not user:
            abort(401, message="User not found")

        projectId = getattr(user, "current_projectId", None) or 1

        # Verifica che il modello appartenga al modulo
        module = module_api_service.get_module_by_name(module_name, projectId)
        models = module_api_service.get_module_models(module)
        model_names = [m.name for m in models]

        if model_name not in model_names:
            abort(
                404, message=f"Model '{model_name}' not found in module '{module_name}'"
            )

        # Delega al DynamicApiService
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)

        result, headers = module_api_service.dynamic_api.list_records(
            projectId=projectId, model_name=model_name, page=page, per_page=per_page
        )

        return result, 200, headers

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(201, {"type": "object"})
    def post(self, module_name, model_name):
        """Crea un nuovo record nel modello."""
        userId = get_jwt_identity()
        from backend.models import User

        user = db.session.get(User, userId)

        if not user:
            abort(401, message="User not found")

        projectId = getattr(user, "current_projectId", None) or 1

        # Verifica che il modello appartenga al modulo
        module = module_api_service.get_module_by_name(module_name, projectId)
        models = module_api_service.get_module_models(module)
        model_names = [m.name for m in models]

        if model_name not in model_names:
            abort(
                404, message=f"Model '{model_name}' not found in module '{module_name}'"
            )

        data = request.get_json() or {}

        result, status = module_api_service.dynamic_api.create_record(
            projectId=projectId, model_name=model_name, data=data
        )

        if status != 201:
            abort(status, message=result.get('message', 'Error creating record.'))
        return result


@blp.route("/<string:module_name>/<string:model_name>/<int:itemId>")
class ModuleModelDetail(MethodView):
    """Dettaglio, aggiornamento e cancellazione record."""

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, {"type": "object"})
    def get(self, module_name, model_name, itemId):
        """Leggi un record."""
        userId = get_jwt_identity()
        from backend.models import User

        user = db.session.get(User, userId)

        if not user:
            abort(401, message="User not found")

        projectId = getattr(user, "current_projectId", None) or 1

        # Verifica che il modello appartenga al modulo
        module = module_api_service.get_module_by_name(module_name, projectId)
        models = module_api_service.get_module_models(module)
        model_names = [m.name for m in models]

        if model_name not in model_names:
            abort(
                404, message=f"Model '{model_name}' not found in module '{module_name}'"
            )

        result = module_api_service.dynamic_api.get_record(
            projectId=projectId, model_name=model_name, itemId=itemId
        )

        return result

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, {"type": "object"})
    def put(self, module_name, model_name, itemId):
        """Aggiorna un record."""
        userId = get_jwt_identity()
        from backend.models import User

        user = db.session.get(User, userId)

        if not user:
            abort(401, message="User not found")

        projectId = getattr(user, "current_projectId", None) or 1

        # Verifica che il modello appartenga al modulo
        module = module_api_service.get_module_by_name(module_name, projectId)
        models = module_api_service.get_module_models(module)
        model_names = [m.name for m in models]

        if model_name not in model_names:
            abort(
                404, message=f"Model '{model_name}' not found in module '{module_name}'"
            )

        data = request.get_json() or {}

        result = module_api_service.dynamic_api.update_record(
            projectId=projectId, model_name=model_name, itemId=itemId, data=data
        )

        return result

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(204)
    def delete(self, module_name, model_name, itemId):
        """Elimina un record."""
        userId = get_jwt_identity()
        from backend.models import User

        user = db.session.get(User, userId)

        if not user:
            abort(401, message="User not found")

        projectId = getattr(user, "current_projectId", None) or 1

        # Verifica che il modello appartenga al modulo
        module = module_api_service.get_module_by_name(module_name, projectId)
        models = module_api_service.get_module_models(module)
        model_names = [m.name for m in models]

        if model_name not in model_names:
            abort(
                404, message=f"Model '{model_name}' not found in module '{module_name}'"
            )

        module_api_service.dynamic_api.delete_record(
            projectId=projectId, model_name=model_name, itemId=itemId
        )

        return "", 204
