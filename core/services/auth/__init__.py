"""
Auth services package.
Contiene i servizi per l'autenticazione e gestione JWT.

Struttura:
- auth_service.py: Servizio principale di autenticazione
- jwt_service.py: Gestione token JWT
- permission_service.py: Gestione permessi (gia' esistente)
"""
from core.services.auth.jwt_service import JWTService

__all__ = ['JWTService']
