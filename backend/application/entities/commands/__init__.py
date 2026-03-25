from dataclasses import dataclass, field
from typing import Optional, List
from datetime import date


@dataclass
class IndirizzoData:
    denominazione: Optional[str] = None
    numero_civico: Optional[str] = None
    CAP: Optional[str] = None
    città: str = ''
    provincia: Optional[str] = None
    regione: Optional[str] = None
    nazione: str = 'IT'
    latitudine: Optional[float] = None
    longitudine: Optional[float] = None
    indirizzo_completo: Optional[str] = None
    tipo: Optional[str] = None


@dataclass
class ContattoData:
    canale: str = ''
    valore: str = ''
    tipo_utilizzo: Optional[str] = None
    is_verified: bool = False
    is_preferred: bool = False


@dataclass
class RuoloAssegnatoData:
    ruolo_id: int
    ruolo_codice: Optional[str] = None
    data_inizio: Optional[date] = None
    data_fine: Optional[date] = None
    stato: str = 'attivo'
    parametri: Optional[str] = None


@dataclass
class CreateSoggettoCommand:
    tenant_id: int
    codice: str
    nome: str
    tipo_soggetto: str = 'persona_fisica'
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
    ruoli: List[RuoloAssegnatoData] = field(default_factory=list)
    indirizzi: List[IndirizzoData] = field(default_factory=list)
    contatti: List[ContattoData] = field(default_factory=list)


@dataclass
class UpdateSoggettoCommand:
    id: int
    tenant_id: int
    codice: Optional[str] = None
    nome: Optional[str] = None
    tipo_soggetto: Optional[str] = None
    cognome: Optional[str] = None
    ragione_sociale: Optional[str] = None
    partita_iva: Optional[str] = None
    codice_fiscale: Optional[str] = None
    email_principale: Optional[str] = None
    telefono_principale: Optional[str] = None
    website: Optional[str] = None
    stato: Optional[str] = None
    note: Optional[str] = None
    tags: Optional[str] = None


@dataclass
class DeleteSoggettoCommand:
    id: int
    tenant_id: int


@dataclass
class AssegnaRuoloCommand:
    soggetto_id: int
    ruolo_id: int
    tenant_id: int
    data_inizio: Optional[date] = None
    data_fine: Optional[date] = None
    stato: str = 'attivo'
    parametri: Optional[str] = None


@dataclass
class RevocaRuoloCommand:
    soggetto_id: int
    ruolo_id: int
    tenant_id: int


@dataclass
class CreateRuoloCommand:
    tenant_id: int
    codice: str
    nome: str
    descrizione: Optional[str] = None
    categoria: Optional[str] = None
    richiede_credito: bool = False
    richiede_contratto: bool = False
    soggetto_a_fatturazione: bool = False


@dataclass
class UpdateRuoloCommand:
    id: int
    tenant_id: int
    codice: Optional[str] = None
    nome: Optional[str] = None
    descrizione: Optional[str] = None
    categoria: Optional[str] = None
    richiede_credito: Optional[bool] = None
    richiede_contratto: Optional[bool] = None
    soggetto_a_fatturazione: Optional[bool] = None
    is_active: Optional[bool] = None


@dataclass
class DeleteRuoloCommand:
    id: int
    tenant_id: int


@dataclass
class AggiungiIndirizzoCommand:
    soggetto_id: int
    tenant_id: int
    indirizzo: IndirizzoData
    tipo_riferimento: Optional[str] = None
    is_preferred: bool = False


@dataclass
class AggiungiContattoCommand:
    soggetto_id: int
    tenant_id: int
    contatto: ContattoData
    tipo_riferimento: Optional[str] = None
    is_primary: bool = False
