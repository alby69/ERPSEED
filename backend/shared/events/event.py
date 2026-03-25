from dataclasses import dataclass
from typing import Any

@dataclass
class DomainEvent:
    """
    Rappresenta un evento di dominio all'interno del sistema.
    """
    event_type: str
    payload: Any