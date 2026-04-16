"""
Module API - Endpoints per gestione moduli.
"""
from flask import request, g
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_smorest import Blueprint, abort
from marshmallow import Schema, fields

from models import User
from core.services.module_service import (
    ModuleService,
    ModuleNotFoundError,
    ModuleDependencyError,
    PlanNotCompatibleError,
    LicenseInvalidError
)
from core.services.tenant_module_service import TenantModuleService

blp = Blueprint('modules', __name__, url_prefix='/api/v1/modules')


class ModuleEnableSchema(Schema):
    """Schema per attivazione modulo."""
    module_id = fields.Str(required=True)
    license_key = fields.Str(required=False, allow_none=True)
    config = fields.Dict(required=False, load_default={})


class ModuleConfigSchema(Schema):
    """Schema per aggiornamento configurazione."""
    config = fields.Dict(required=True)


@blp.route('/')
class ModuleList(MethodView):
    @blp.response(200)
    @jwt_required()
    def get(self):
        """
        Lista moduli disponibili nel sistema.
        """
        modules = ModuleService.get_available_modules()
        return [m.to_dict() for m in modules]


@blp.route('/categories')
class ModuleCategories(MethodView):
    @blp.response(200)
    @jwt_required()
    def get(self):
        """
        Lista moduli raggruppati per categoria.
        """
        return {
            'core': [m.to_dict() for m in ModuleService.get_core_modules()],
            'builtin': [m.to_dict() for m in ModuleService.get_builtin_modules()],
            'premium': [m.to_dict() for m in ModuleService.get_premium_modules()]
        }


@blp.route('/enabled')
class TenantModules(MethodView):
    @blp.response(200)
    @jwt_required()
    def get(self):
        """
        Lista moduli attivi per il tenant corrente.
        """
        user = User.query.get(get_jwt_identity())
        tenant_id = user.tenant_id if user else None

        enabled = TenantModuleService.get_enabled_modules(tenant_id) # type: ignore
        return [tm.to_dict() for tm in enabled]

    @blp.arguments(ModuleEnableSchema)
    @blp.response(200)
    @jwt_required()
    def post(self, args):
        """
        Attiva un modulo per il tenant corrente.
        """
        user = User.query.get(get_jwt_identity())

        # Solo admin può attivare moduli
        if not user or user.role != 'admin':
            abort(403, message="Solo gli admin possono gestire i moduli")

        module_id = args['module_id']
        license_key = args.get('license_key')
        config = args.get('config', {})

        try:
            tm = TenantModuleService.enable_module(
                user.tenant_id if user else None, # type: ignore
                module_id,
                license_key,
                config
            )
            return tm.to_dict()
        except ModuleNotFoundError as e:
            abort(404, message=str(e))
        except PlanNotCompatibleError as e:
            abort(400, message=str(e))
        except ModuleDependencyError as e:
            abort(400, message=str(e))
        except LicenseInvalidError as e:
            abort(400, message=str(e))
        except ValueError as e:
            abort(400, message=str(e))


@blp.route('/<string:module_id>')
class ModuleDetail(MethodView):
    @blp.response(200)
    @jwt_required()
    def get(self, module_id):
        """
        Dettagli modulo con stato per il tenant corrente.
        """
        module = ModuleService.get_module_by_id(module_id)
        if not module:
            abort(404, message="Modulo non trovato")

        user = User.query.get(get_jwt_identity())
        is_enabled = TenantModuleService.is_module_enabled(user.tenant_id if user else None, module_id) # type: ignore

        result = module.to_dict()
        result['is_enabled'] = is_enabled
        return result

    @blp.response(204)
    @jwt_required()
    def delete(self, module_id):
        """
        Disattiva un modulo per il tenant corrente.
        """
        user = User.query.get(get_jwt_identity())

        if not user or user.role != 'admin':
            abort(403, message="Solo gli admin possono gestire i moduli")

        try:
            TenantModuleService.disable_module(user.tenant_id if user else None, module_id) # type: ignore
        except ModuleDependencyError as e:
            abort(400, message=str(e))
        except ValueError as e:
            abort(400, message=str(e))


@blp.route('/<string:module_id>/config')
class ModuleConfig(MethodView):
    @blp.response(200)
    @jwt_required()
    def get(self, module_id):
        """
        Configurazione del modulo per il tenant corrente.
        """
        user = User.query.get(get_jwt_identity())
        config = TenantModuleService.get_module_config(user.tenant_id if user else None, module_id) # type: ignore
        return {'config': config}

    @blp.arguments(ModuleConfigSchema)
    @blp.response(200)
    @jwt_required()
    def put(self, args, module_id):
        """
        Aggiorna configurazione del modulo.
        """
        user = User.query.get(get_jwt_identity())

        if not user or user.role != 'admin':
            abort(403, message="Solo gli admin possono gestire la configurazione")

        try:
            config = TenantModuleService.update_module_config(
                user.tenant_id if user else None, # type: ignore
                module_id,
                args['config']
            )
            return {'config': config}
        except ModuleNotFoundError as e:
            abort(404, message=str(e))
