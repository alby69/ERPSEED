"""
Event Bus - Sistema di comunicazione asincrona tra componenti.

Permette a blocchi, container e robot di comunicare in modo
decoupling attraverso eventi.
"""
from typing import Dict, List, Callable, Any
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class EventBus:
    """Bus eventi per comunicazione asincrona tra componenti"""

    _handlers: Dict[str, List[Callable]] = defaultdict(list)
    _global_handlers: List[Callable] = []
    _event_history: List[Dict[str, Any]] = []
    _max_history = 100

    @classmethod
    def subscribe(cls, event_type: str, handler: Callable):
        """Iscrive un handler a un tipo di evento"""
        cls._handlers[event_type].append(handler)
        logger.debug(f"[EventBus] Handler registrato per evento: {event_type}")

    @classmethod
    def unsubscribe(cls, event_type: str, handler: Callable):
        """Rimuove un handler da un tipo di evento"""
        if event_type in cls._handlers and handler in cls._handlers[event_type]:
            cls._handlers[event_type].remove(handler)

    @classmethod
    def subscribe_all(cls, handler: Callable):
        """Iscrive un handler a tutti gli eventi"""
        cls._global_handlers.append(handler)

    @classmethod
    def publish(cls, event_type: str, data: Dict[str, Any] = None):
        """Pubblica un evento"""
        event_data = {
            'type': event_type,
            'data': data or {},
            'handlers': []
        }

        # Notifica handler specifici
        for handler in cls._handlers.get(event_type, []):
            try:
                result = handler(event_data['data'])
                event_data['handlers'].append({
                    'handler': handler.__name__,
                    'result': result
                })
            except Exception as e:
                logger.error(f"[EventBus] Errore nell'handler {handler}: {e}")

        # Notifica handler globali
        for handler in cls._global_handlers:
            try:
                handler(event_data)
            except Exception as e:
                logger.error(f"[EventBus] Errore nell'handler globale: {e}")

        # Salva nella storia
        cls._event_history.append(event_data)
        if len(cls._event_history) > cls._max_history:
            cls._event_history.pop(0)

        logger.debug(f"[EventBus] Pubblicato evento: {event_type}")

    @classmethod
    def get_history(cls, event_type: str = None, limit: int = 10) -> List[Dict]:
        """Recupera la storia degli eventi"""
        if event_type:
            return [e for e in cls._event_history if e['type'] == event_type][-limit:]
        return cls._event_history[-limit:]

    @classmethod
    def clear(cls):
        """Pulisce tutti gli handler e la storia"""
        cls._handlers.clear()
        cls._global_handlers.clear()
        cls._event_history.clear()


# Eventi standard del sistema
class SystemEvents:
    """Costanti per eventi di sistema"""

    # Entity events
    ENTITY_CREATED = "entity.created"
    ENTITY_UPDATED = "entity.updated"
    ENTITY_DELETED = "entity.deleted"

    # Block events
    BLOCK_REGISTERED = "block.registered"
    BLOCK_LOADED = "block.loaded"

    # Container events
    CONTAINER_INITIALIZED = "container.initialized"
    CONTAINER_DESTROYED = "container.destroyed"

    # Robot events
    ROBOT_INSTALLED = "robot.installed"
    ROBOT_UNINSTALLED = "robot.uninstalled"
    ROBOT_ACTIVATED = "robot.activated"
    ROBOT_DEACTIVATED = "robot.deactivated"

    # Application events
    APP_STARTED = "app.started"
    APP_STOPPED = "app.stopped"


def emit(event_type: str, data: Dict[str, Any] = None):
    """Shortcut per pubblicare eventi"""
    EventBus.publish(event_type, data)
