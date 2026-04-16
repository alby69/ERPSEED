"""
Module Middleware - Protezione accesso ai moduli.
"""
from functools import wraps
from flask import request, jsonify, g
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from backend.models import User
from backend.core.services.tenant_module_service import TenantModuleService


class ModuleMiddleware:
    """Middleware per verificare accesso ai moduli."""

    @staticmethod
    def require_module(module_id: str):
        """
        Decorator per proteggere endpoint con modulo richiesto.

        Usage:
            @require_module('accounting')
            def my_endpoint():
                ...

        Args:
            module_id: ID del modulo richiesto.
        """
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # Verifica JWT
                verify_jwt_in_request()
                user_id = get_jwt_identity()

                user = User.query.get(user_id)
                if not user:
                    return jsonify({
                        'error': 'USER_NOT_FOUND',
                        'message': 'Utente non trovato'
                    }), 404

                tenant_id = user.tenant_id

                # Verifica modulo abilitato
                if not TenantModuleService.is_module_enabled(tenant_id, module_id):
                    return jsonify({
                        'error': 'MODULE_NOT_ENABLED',
                        'message': f"Modulo '{module_id}' non abilitato per questa organizzazione"
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
                user_id = get_jwt_identity(optional=True)

                if user_id:
                    user = User.query.get(user_id)
                    if user and user.tenant_id:
                        enabled = TenantModuleService.get_enabled_module_ids(user.tenant_id)
                        g.enabled_modules = enabled
                    else:
                        g.enabled_modules = []
                else:
                    g.enabled_modules = []
            except Exception:
                g.enabled_modules = []

        return middleware

    @staticmethod
    def check_module_access(module_id: str) -> bool:
        """
        Verifica se l'utente corrente ha accesso al modulo.

        Args:
            module_id: ID del modulo da verificare.

        Returns:
            True se l'utente ha accesso, False altrimenti.
        """
        try:
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity(optional=True)

            if not user_id:
                return False

            user = User.query.get(user_id)
            if not user or not user.tenant_id:
                return False

            return TenantModuleService.is_module_enabled(user.tenant_id, module_id)
        except Exception:
            return False


def init_app(app):
    """Inizializza il middleware dei moduli."""
    app.before_request(ModuleMiddleware.get_enabled_modules_middleware())
