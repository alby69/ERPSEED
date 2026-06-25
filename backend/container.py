from typing import Callable, Any, Dict

class ServiceContainer:
    """
    Un semplice container per la dependency injection con supporto per servizi
    transient e singleton (lazy loaded).
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
            singleton (bool): Se True, il servizio sarà un singleton (creato una sola volta).
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

_container = ServiceContainer()

def get_container() -> ServiceContainer:
    """Restituisce l'istanza globale del service container."""
    return _container