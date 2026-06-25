from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flask import Flask
    from backend.container import ServiceContainer

class Plugin(ABC):
    """
    Classe Astratta di Base per tutti i plugin.
    Ogni plugin deve fornire una classe che eredita da questa.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Un nome univoco per il plugin."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """La versione del plugin."""
        pass

    @abstractmethod
    def register(self, app: 'Flask', container: 'ServiceContainer'):
        """
        Chiamato quando il plugin viene caricato.
        Utilizzare per registrare blueprint, servizi, gestori di eventi, ecc.
        """
        pass

    @abstractmethod
    def unregister(self, app: 'Flask'):
        """
        Chiamato quando il plugin viene scaricato.
        Utilizzare per pulire le risorse.
        """
        pass