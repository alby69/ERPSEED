"""
Modelli archetipici per ERPE.

Questi sono i mattoncini base del sistema:
- Soggetto: entità anagrafica principale
- Ruolo: ruoli che un soggetto può avere (cliente, fornitore, etc.)
- Indirizzo: informazioni geografiche
- Contatto: canali di contatto
"""

from .soggetto import Soggetto
from .ruolo import Ruolo, SoggettoRuolo
from .indirizzo import Indirizzo, SoggettoIndirizzo
from .contatto import Contatto, SoggettoContatto

__all__ = [
    'Soggetto',
    'Ruolo',
    'SoggettoRuolo',
    'Indirizzo',
    'SoggettoIndirizzo',
    'Contatto',
    'SoggettoContatto',
]
