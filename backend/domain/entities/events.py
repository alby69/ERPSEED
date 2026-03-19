from dataclasses import dataclass
from typing import Optional, List


@dataclass
class SoggettoCreatedEvent:
    soggetto_id: int
    tenant_id: int
    codice: str
    tipo_soggetto: str


@dataclass
class SoggettoUpdatedEvent:
    soggetto_id: int
    tenant_id: int


@dataclass
class SoggettoDeletedEvent:
    soggetto_id: int
    tenant_id: int


@dataclass
class RuoloCreatedEvent:
    ruolo_id: int
    tenant_id: int
    codice: str


@dataclass
class RuoloAssegnatoEvent:
    soggetto_id: int
    ruolo_id: int
    tenant_id: int
