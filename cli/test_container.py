import pytest
from core.container import ServiceContainer

# --- Fixtures e Classi di Supporto ---

@pytest.fixture
def container():
    """Fornisce una nuova istanza vuota di ServiceContainer per ogni test."""
    return ServiceContainer()

class DummyService:
    """Una classe semplice da usare per testare la registrazione."""
    def __init__(self):
        self.value = "dummy"

class DependentService:
    """Una classe che dipende da un altro servizio."""
    def __init__(self, dummy_service: DummyService):
        self.dummy_service = dummy_service

# --- Casi di Test ---

def test_register_and_get_transient_service(container: ServiceContainer):
    """
    Verifica che ottenere un servizio transient restituisca una nuova istanza ogni volta.
    """
    container.register("dummy", DummyService)

    instance1 = container.get("dummy")
    instance2 = container.get("dummy")

    assert isinstance(instance1, DummyService)
    assert isinstance(instance2, DummyService)
    assert instance1 is not instance2

def test_register_and_get_singleton_service(container: ServiceContainer):
    """
    Verifica che ottenere un servizio singleton restituisca sempre la stessa istanza.
    """
    container.register("dummy_singleton", DummyService, singleton=True)

    instance1 = container.get("dummy_singleton")
    instance2 = container.get("dummy_singleton")

    assert isinstance(instance1, DummyService)
    assert instance1 is instance2

def test_get_unregistered_service_raises_keyerror(container: ServiceContainer):
    """
    Verifica che il tentativo di ottenere un servizio non registrato sollevi un KeyError.
    """
    with pytest.raises(KeyError) as excinfo:
        container.get("non_existent_service")
    assert "Service 'non_existent_service' not found" in str(excinfo.value)

def test_overwrite_service_registration(container: ServiceContainer):
    """
    Verifica che registrare nuovamente un servizio con lo stesso nome sovrascriva il precedente.
    """
    class AnotherService:
        pass

    container.register("service", DummyService)
    instance1 = container.get("service")
    assert isinstance(instance1, DummyService)

    container.register("service", AnotherService)
    instance2 = container.get("service")
    assert isinstance(instance2, AnotherService)

def test_dependency_injection_with_transient_services(container: ServiceContainer):
    """
    Verifica che il container possa iniettare dipendenze nei servizi.
    """
    container.register("dummy", DummyService)
    container.register("dependent", lambda: DependentService(container.get("dummy")))

    dependent_instance = container.get("dependent")

    assert isinstance(dependent_instance, DependentService)
    assert isinstance(dependent_instance.dummy_service, DummyService)

def test_dependency_injection_with_singleton_dependency(container: ServiceContainer):
    """
    Verifica che una dipendenza singleton sia iniettata correttamente e condivisa.
    """
    container.register("dummy_singleton", DummyService, singleton=True)
    container.register("dependent1", lambda: DependentService(container.get("dummy_singleton")))
    container.register("dependent2", lambda: DependentService(container.get("dummy_singleton")))

    dependent1 = container.get("dependent1")
    dependent2 = container.get("dependent2")

    assert isinstance(dependent1.dummy_service, DummyService)
    assert isinstance(dependent2.dummy_service, DummyService)
    assert dependent1.dummy_service is dependent2.dummy_service

def test_register_with_lambda_provider(container: ServiceContainer):
    """
    Verifica la registrazione di un servizio utilizzando una funzione lambda come provider.
    """
    container.register("configured_service", lambda: DummyService())
    instance = container.get("configured_service")
    assert isinstance(instance, DummyService)