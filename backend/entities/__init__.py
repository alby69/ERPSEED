"""
Entities module - DEPRECATED.

Redirects all imports to the new infrastructure location.
"""
from backend.infrastructure.entities.models import (
    Soggetto, Ruolo, SoggettoRuolo,
    Indirizzo, SoggettoIndirizzo,
    Contatto, SoggettoContatto,
)
from backend.infrastructure.entities.models import Soggetto as SoggettoModel
from backend.infrastructure.entities.models import Ruolo as RuoloModel
from backend.infrastructure.entities.models import Indirizzo as IndirizzoModel
from backend.infrastructure.entities.models import Contatto as ContattoModel
from backend.infrastructure.entities.models import SoggettoRuolo as SoggettoRuoloModel
from backend.infrastructure.entities.models import SoggettoIndirizzo as SoggettoIndirizzoModel
from backend.infrastructure.entities.models import SoggettoContatto as SoggettoContattoModel

__all__ = [
    'Soggetto', 'Ruolo', 'SoggettoRuolo',
    'Indirizzo', 'SoggettoIndirizzo',
    'Contatto', 'SoggettoContatto',
    'SoggettoModel', 'RuoloModel', 'IndirizzoModel', 'ContattoModel',
    'SoggettoRuoloModel', 'SoggettoIndirizzoModel', 'SoggettoContattoModel',
]
