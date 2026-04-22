"""
Services package - Centralized business logic with proxy support for backward compatibility.
"""

from backend.core.services.base import BaseService

class ServiceProxy:
    """Proxy class to handle lazy imports of services."""
    def __init__(self, module_path, class_name):
        self.module_path = module_path
        self.class_name = class_name
        self._instance = None

    def _get_instance(self):
        if self._instance is None:
            import importlib
            module = importlib.import_module(self.module_path)
            self._instance = getattr(module, self.class_name)()
        return self._instance

    def __getattr__(self, name):
        return getattr(self._get_instance(), name)

    def __call__(self, *args, **kwargs):
        # If the proxy is called, assume we want to instantiate the underlying class
        import importlib
        module = importlib.import_module(self.module_path)
        cls = getattr(module, self.class_name)
        return cls(*args, **kwargs)

# Backward compatibility proxies
ProjectService = ServiceProxy("backend.modules.projects.service", "ProjectService")
BuilderService = ServiceProxy("backend.modules.builder.service", "BuilderService")
DynamicApiService = ServiceProxy("backend.modules.dynamic_api.services.dynamic_api_service", "DynamicApiService")
UserService = ServiceProxy("backend.modules.users.service", "UserService")

__all__ = [
    "BaseService",
    "ProjectService",
    "BuilderService",
    "DynamicApiService",
    "UserService"
]
