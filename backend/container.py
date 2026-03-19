from typing import Callable, Any, Dict

import warnings


class ServiceContainer:
    """
    Un semplice container per la dependency injection con supporto per servizi
    transient e singleton (lazy loaded).
    
    CQRS Services are registered here for easy access across the application.
    """

    def __init__(self):
        self._providers: Dict[str, Callable] = {}
        self._singletons: Dict[str, bool] = {}
        self._instances: Dict[str, Any] = {}

    def register(self, name: str, provider: Callable, singleton: bool = False):
        """
        Registra un provider di servizi.

        Args:
            name (str): Il nome del servizio.
            provider (Callable): Una funzione che crea un'istanza del servizio.
            singleton (bool): Se True, il servizio sarà un singleton (creato una volta).
        """
        self._providers[name] = provider
        if singleton:
            self._singletons[name] = True

    def get(self, name: str) -> Any:
        """
        Risolve e restituisce un'istanza di un servizio.

        Args:
            name (str): Il nome del servizio da risolvere.

        Returns:
            Any: Un'istanza del servizio.

        Raises:
            KeyError: Se il servizio non è registrato.
        """
        if name not in self._providers:
            raise KeyError(f"Service '{name}' not found in container.")

        if name in self._instances:
            return self._instances[name]

        instance = self._providers[name]()

        if name in self._singletons:
            self._instances[name] = instance

        return instance

    def _register_cqrs_services(self):
        from backend.infrastructure.products.repository import ProductRepository
        from backend.infrastructure.sales.repository import SalesOrderRepository
        from backend.infrastructure.purchases.repository import PurchaseOrderRepository
        from backend.infrastructure.analytics.repository import ChartRepository, ChartLibraryRepository
        from backend.infrastructure.builder.repository import ModelRepository, ArchetypeRepository, ComponentRepository, BlockRepository
        from backend.infrastructure.ai.services import ChatService, ToolService
        from backend.infrastructure.ai.llm_adapters import OllamaAdapter
        
        default_llm = OllamaAdapter()
        default_tool_service = ToolService()
        default_chat_service = ChatService(llm_adapter=default_llm, tool_service=default_tool_service)
        
        self.register("product_repository", lambda: ProductRepository(), singleton=True)
        self.register("sale_repository", lambda: SalesOrderRepository(), singleton=True)
        self.register("purchase_repository", lambda: PurchaseOrderRepository(), singleton=True)
        self.register("chart_repository", lambda: ChartRepository(), singleton=True)
        self.register("chart_library_repository", lambda: ChartLibraryRepository(), singleton=True)
        self.register("model_repository", lambda: ModelRepository(), singleton=True)
        self.register("archetype_repository", lambda: ArchetypeRepository(), singleton=True)
        self.register("component_repository", lambda: ComponentRepository(), singleton=True)
        self.register("block_repository", lambda: BlockRepository(), singleton=True)
        self.register("chat_service", lambda: default_chat_service, singleton=True)
        self.register("tool_service", lambda: default_tool_service, singleton=True)

_container = ServiceContainer()
_container._register_cqrs_services()


def get_container() -> ServiceContainer:
    """Restituisce l'istanza globale del service container."""
    return _container


def get_product_repository():
    """Get ProductRepository instance."""
    return _container.get("product_repository")


def get_sale_repository():
    """Get SaleRepository instance."""
    return _container.get("sale_repository")


def get_purchase_repository():
    """Get PurchaseRepository instance."""
    return _container.get("purchase_repository")


def get_analytics_repository():
    """Get AnalyticsRepository instance."""
    return _container.get("analytics_repository")


def get_builder_repository():
    """Get BuilderRepository instance."""
    return _container.get("builder_repository")


def get_chat_service():
    """Get ChatService instance."""
    return _container.get("chat_service")


def get_tool_service():
    """Get ToolService instance."""
    return _container.get("tool_service")