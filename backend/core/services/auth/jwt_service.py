"""
JWT Service - Gestione token JWT.
Separato da AuthService per rispettare il principio DRY (Single Responsibility).

Questo modulo gestisce:
- Creazione access/refresh token
- Validazione token
- Refresh token
- Claims nel token
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from flask import Flask
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    get_jwt,
    decode_token
)
from flask_jwt_extended import JWTManager


class JWTService:
    """
    Service per la gestione dei token JWT.
    Responsabile solo della creazione e validazione dei token.
    """
    
    _app: Optional[Flask] = None
    
    @classmethod
    def init_app(cls, app: Flask):
        """Inizializza il servizio JWT con l'app Flask."""
        cls._app = app
        JWTManager(app)
    
    @classmethod
    def create_access_token(
        cls,
        identity: str,
        additional_claims: Optional[Dict[str, Any]] = None,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Crea un access token JWT.
        
        Args:
            identity: Identità dell'utente (user_id)
            additional_claims: Claims aggiuntivi da includere nel token
            expires_delta: Durata personalizzata del token
            
        Returns:
            str: Access token JWT
        """
        if additional_claims is None:
            additional_claims = {}
            
        return create_access_token(
            identity=identity,
            additional_claims=additional_claims,
            expires_delta=expires_delta
        )
    
    @classmethod
    def create_refresh_token(cls, identity: str) -> str:
        """
        Crea un refresh token JWT.
        
        Args:
            identity: Identità dell'utente (user_id)
            
        Returns:
            str: Refresh token JWT
        """
        return create_refresh_token(identity=identity)
    
    @classmethod
    def decode_token(cls, token: str) -> Dict[str, Any]:
        """
        Decodifica e valida un token JWT.
        
        Args:
            token: Token JWT da decodificare
            
        Returns:
            Dict contenente i claims del token
            
        Raises:
            Exception: Se il token è invalido o scaduto
        """
        return decode_token(token)
    
    @classmethod
    def get_identity(cls) -> Optional[str]:
        """Ottiene l'identità (user_id) dal token corrente."""
        return get_jwt_identity()
    
    @classmethod
    def get_claims(cls) -> Dict[str, Any]:
        """Ottiene i claims aggiuntivi dal token corrente."""
        return get_jwt()
    
    @classmethod
    def get_tenant_id_from_token(cls) -> Optional[int]:
        """Ottiene il tenant_id dai claims del token."""
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        if tenant_id:
            try:
                return int(tenant_id)
            except (ValueError, TypeError):
                return None
        return None
    
    @classmethod
    def get_user_role_from_token(cls) -> Optional[str]:
        """Ottiene il ruolo dell'utente dai claims del token."""
        claims = get_jwt()
        return claims.get('role')
    
    @classmethod
    def build_user_claims(cls, user) -> Dict[str, Any]:
        """
        Costruisce i claims per un utente.
        
        Args:
            user: Istanza del modello User
            
        Returns:
            Dict contenente i claims dell'utente
        """
        return {
            'role': user.role,
            'tenant_id': user.tenant_id,
            'email': user.email,
            'is_primary': user.is_primary
        }
