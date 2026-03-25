from collections import defaultdict
from typing import Callable, List, Dict
import logging

from .event import DomainEvent

logger = logging.getLogger(__name__)

class EventBus:
    """
    Bus di eventi in-memory per la comunicazione asincrona disaccoppiata
    tra i diversi moduli del sistema.
    """

    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = defaultdict(list)
        logger.info("EventBus initialized.")

    def subscribe(self, event_type: str, handler: Callable):
        """
        Sottoscrive un handler a un tipo di evento specifico.

        Args:
            event_type: Il tipo di evento a cui sottoscrivere (es. "order.created").
            handler: La funzione da chiamare quando l'evento viene pubblicato.
        """
        self._handlers[event_type].append(handler)
        logger.debug(f"Handler {handler.__name__} subscribed to event '{event_type}'")

    def publish(self, event: DomainEvent):
        """
        Pubblica un evento, notificando tutti gli handler sottoscritti.

        Args:
            event: L'oggetto DomainEvent da pubblicare.
        """
        event_type = event.event_type
        logger.debug(f"Publishing event '{event_type}' with payload: {event.payload}")
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                try:
                    handler(event)
                    logger.debug(f"Handler {handler.__name__} executed for event '{event_type}'")
                except Exception as e:
                    logger.error(
                        f"Error executing handler {handler.__name__} for event {event_type}: {e}",
                        exc_info=True
                    )

    def unsubscribe(self, event_type: str, handler: Callable):
        """
        Rimuove la sottoscrizione di un handler da un tipo di evento.

        Args:
            event_type: Il tipo di evento.
            handler: L'handler da rimuovere.
        """
        if event_type in self._handlers and handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)
            logger.debug(f"Handler {handler.__name__} unsubscribed from event '{event_type}'")

# Istanza globale per semplicità, gestita tramite DI container nell'app
_event_bus = EventBus()

def get_event_bus() -> EventBus:
    """
    Factory function per ottenere l'istanza globale dell'EventBus.
    Nell'applicazione reale, questo verrebbe gestito dal container DI.
    """
    return _event_bus