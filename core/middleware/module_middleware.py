"""
Module Middleware - Protezione accesso ai moduli.
"""
from functools import wraps
from flask import request, jsonify, g
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from models import User
from core.services.tenant_module_service import TenantModuleService


class ModuleMiddleware:
    """Middleware per verificare accesso ai moduli."""

    @staticmethod
    def require_module(moduleId: str):
        """
        Decorator per proteggere endpoint con modulo richiesto.

        Usage:
            @require_module('accounting')
            def my_endpoint():
                ...

        Args:
            moduleId: ID del modulo richiesto.
        """
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # Verifica JWT
                verify_jwt_in_request()
                userId = get_jwt_identity()

                user = User.query.get(userId)
                if not user:
                    return jsonify({
                        'error': 'USER_NOT_FOUND',
                        'message': 'Utente non trovato'
                    }), 404

                tenant_id = user.tenant_id

                # Verifica modulo abilitato
                if not TenantModuleService.is_module_enabled(tenant_id, moduleId):
                    return jsonify({
                        'error': 'MODULE_NOT_ENABLED',
                        'message': f"Modulo '{moduleId}' non abilitato per questa organizzazione"
                    }), 403

                return f(*args, **kwargs)
            return decorated_function
        return decorator

    @staticmethod
    def get_enabled_modules_middleware():
        """
        Middleware per aggiungere lista moduli abilitati a ogni richiesta.
        Da usare come before_request handler.
        """
        def middleware():
            try:
                verify_jwt_in_request(optional=True)
                userId = get_jwt_identity(optional=True)

                if userId:
                    user = User.query.get(userId)
                    if user and user.tenant_id:
                        enabled = TenantModuleService.get_enabled_moduleIds(user.tenant_id)
                        g.enabled_modules = enabled
                    else:
                        g.enabled_modules = []
                else:
                    g.enabled_modules = []
            except Exception:
                g.enabled_modules = []

        return middleware

    @staticmethod
    def check_module_access(moduleId: str) -> bool:
        """
        Verifica se l'utente corrente ha accesso al modulo.

        Args:
            moduleId: ID del modulo da verificare.

        Returns:
            True se l'utente ha accesso, False altrimenti.
        """
        try:
            verify_jwt_in_request(optional=True)
            userId = get_jwt_identity(optional=True)

            if not userId:
                return False

            user = User.query.get(userId)
            if not user or not user.tenant_id:
                return False

            return TenantModuleService.is_module_enabled(user.tenant_id, moduleId)
        except Exception:
            return False


def init_app(app):
    """Inizializza il middleware dei moduli."""
    app.before_request(ModuleMiddleware.get_enabled_modules_middleware())
