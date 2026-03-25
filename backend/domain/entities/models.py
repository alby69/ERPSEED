from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List
from enum import Enum


class TipoSoggetto(str, Enum):
    PERSONA_FISICA = 'persona_fisica'
    PERSONA_GIURIDICA = 'persona_giuridica'
    ENTE = 'ente'


class StatoSoggetto(str, Enum):
    ATTIVO = 'attivo'
    INATTIVO = 'inattivo'
    SOSPESO = 'sospeso'


@dataclass
class RuoloAssegnato:
    ruolo_id: int
    ruolo_codice: str
    ruolo_nome: str
    data_inizio: Optional[date] = None
    data_fine: Optional[date] = None
    stato: str = 'attivo'
    parametri: Optional[str] = None


@dataclass
class IndirizzoValue:
    id: Optional[int] = None
    denominazione: Optional[str] = None
    numero_civico: Optional[str] = None
    CAP: Optional[str] = None
    città: Optional[str] = None
    provincia: Optional[str] = None
    regione: Optional[str] = None
    nazione: str = 'IT'
    latitudine: Optional[float] = None
    longitudine: Optional[float] = None
    indirizzo_completo: Optional[str] = None
    tipo: Optional[str] = None
    geocoded: bool = False
    geocoding_data: Optional[str] = None


@dataclass
class SoggettoIndirizzo:
    indirizzo_id: Optional[int] = None
    indirizzo: Optional[IndirizzoValue] = None
    tipo_riferimento: Optional[str] = None
    is_preferred: bool = False
    data_inizio: Optional[date] = None
    data_fine: Optional[date] = None


@dataclass
class ContattoValue:
    id: Optional[int] = None
    canale: str = ''
    valore: str = ''
    tipo_utilizzo: Optional[str] = None
    is_verified: bool = False
    verifica_data: Optional[datetime] = None
    is_preferred: bool = False


@dataclass
class SoggettoContatto:
    contatto_id: Optional[int] = None
    contatto: Optional[ContattoValue] = None
    tipo_riferimento: Optional[str] = None
    is_primary: bool = False


@dataclass
class Soggetto:
    id: Optional[int] = None
    codice: Optional[str] = None
    tipo_soggetto: str = 'persona_fisica'
    nome: str = ''
    cognome: Optional[str] = None
    ragione_sociale: Optional[str] = None
    partita_iva: Optional[str] = None
    codice_fiscale: Optional[str] = None
    email_principale: Optional[str] = None
    telefono_principale: Optional[str] = None
    website: Optional[str] = None
    stato: str = 'attivo'
    note: Optional[str] = None
    tags: Optional[str] = None
    tenant_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    ruoli: List[RuoloAssegnato] = field(default_factory=list)
    indirizzi: List[SoggettoIndirizzo] = field(default_factory=list)
    contatti: List[SoggettoContatto] = field(default_factory=list)

    @property
    def denominazione(self) -> str:
        if self.tipo_soggetto == 'persona_giuridica':
            return self.ragione_sociale or self.nome
        return f"{self.cognome or ''} {self.nome}".strip()


@dataclass
class Ruolo:
    id: Optional[int] = None
    codice: str = ''
    nome: str = ''
    descrizione: Optional[str] = None
    categoria: Optional[str] = None
    richiede_credito: bool = False
    richiede_contratto: bool = False
    soggetto_a_fatturazione: bool = False
    is_active: bool = True
    tenant_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
