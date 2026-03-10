import pytest
from unittest.mock import Mock
from .event_bus import EventBus
from .event import DomainEvent

@pytest.fixture
def event_bus():
    """Fornisce una nuova istanza di EventBus per ogni test."""
    return EventBus()

def test_subscribe_and_publish(event_bus: EventBus):
    """Verifica che un handler sottoscritto venga chiamato alla pubblicazione di un evento."""
    handler_mock = Mock()
    event_type = "test.event.created"
    event_payload = {"id": 1, "name": "Test Item"}
    event = DomainEvent(event_type=event_type, payload=event_payload)

    # Sottoscrivi l'handler
    event_bus.subscribe(event_type, handler_mock)

    # Pubblica l'evento
    event_bus.publish(event)

    # Verifica che l'handler sia stato chiamato una volta con l'evento corretto
    handler_mock.assert_called_once_with(event)

def test_publish_with_no_subscribers(event_bus: EventBus):
    """Verifica che la pubblicazione di un evento senza sottoscrittori non causi errori."""
    handler_mock = Mock()
    event = DomainEvent(event_type="unsubscribed.event", payload={})

    try:
        event_bus.publish(event)
    except Exception as e:
        pytest.fail(f"La pubblicazione senza sottoscrittori ha sollevato un'eccezione: {e}")

    # Verifica che nessun handler sia stato chiamato
    handler_mock.assert_not_called()

def test_multiple_handlers_for_one_event(event_bus: EventBus):
    """Verifica che tutti gli handler sottoscritti per un evento vengano chiamati."""
    handler1_mock = Mock()
    handler2_mock = Mock()
    event_type = "multiple.handlers.event"
    event = DomainEvent(event_type=event_type, payload={"data": "shared"})

    event_bus.subscribe(event_type, handler1_mock)
    event_bus.subscribe(event_type, handler2_mock)

    event_bus.publish(event)

    handler1_mock.assert_called_once_with(event)
    handler2_mock.assert_called_once_with(event)

def test_handler_for_different_event_not_called(event_bus: EventBus):
    """Verifica che un handler per un tipo di evento non venga chiamato per un altro tipo."""
    handler_subscribed = Mock()
    event_type_subscribed = "subscribed.event"
    event_type_published = "other.event"

    event_bus.subscribe(event_type_subscribed, handler_subscribed)

    event_to_publish = DomainEvent(event_type=event_type_published, payload={})
    event_bus.publish(event_to_publish)

    handler_subscribed.assert_not_called()

def test_unsubscribe_handler(event_bus: EventBus):
    """Verifica che un handler rimosso non venga più chiamato."""
    handler_mock = Mock()
    event_type = "test.unsubscribe"
    event = DomainEvent(event_type=event_type, payload={})

    # Sottoscrivi e poi rimuovi
    event_bus.subscribe(event_type, handler_mock)
    event_bus.unsubscribe(event_type, handler_mock)

    event_bus.publish(event)

    handler_mock.assert_not_called()

def test_unsubscribe_nonexistent_handler(event_bus: EventBus):
    """Verifica che la rimozione di un handler non esistente non causi errori."""
    handler_mock = Mock()
    event_type = "test.unsubscribe.nonexistent"

    try:
        event_bus.unsubscribe(event_type, handler_mock)
    except Exception as e:
        pytest.fail(f"La rimozione di un handler non esistente ha sollevato un'eccezione: {e}")

def test_payload_is_passed_correctly(event_bus: EventBus):
    """Verifica che il payload dell'evento sia passato correttamente all'handler."""
    handler_mock = Mock()
    event_type = "payload.test"
    payload_data = {"key": "value", "number": 123, "active": True}
    event = DomainEvent(event_type=event_type, payload=payload_data)

    event_bus.subscribe(event_type, handler_mock)
    event_bus.publish(event)

    handler_mock.assert_called_once()
    # Estrai l'argomento con cui l'handler è stato chiamato
    called_event = handler_mock.call_args[0][0]

    assert isinstance(called_event, DomainEvent)
    assert called_event.event_type == event_type
    assert called_event.payload == payload_data
    assert called_event.payload["key"] == "value"