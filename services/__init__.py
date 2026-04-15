"""
Services package - Business logic layer.

This package contains service classes that encapsulate business logic,
separating it from route handlers (controllers).

Services:
    - DynamicApiService: Dynamic CRUD API operations
"""

from core.services.base import BaseService

class DynamicApiService:
    def __new__(cls, *args, **kwargs):
        from modules.dynamic_api.service import get_dynamic_api_service
        return get_dynamic_api_service()

class BuilderService:
    def __new__(cls, *args, **kwargs):
        from modules.builder.service import get_builder_service
        return get_builder_service()

class ProjectService:
    def __new__(cls, *args, **kwargs):
        from modules.projects.service import get_project_service
        return get_project_service()

class UserService:
    def __new__(cls, *args, **kwargs):
        from modules.users.service import get_user_service
        return get_user_service()

__all__ = [
    'BaseService',
    'ProjectService',
    'BuilderService',
    'DynamicApiService',
    'UserService',
]
