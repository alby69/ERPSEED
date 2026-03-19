from typing import Optional, List
from backend.domain.entities.models import Soggetto, Ruolo
from backend.domain.entities.events import SoggettoCreatedEvent, SoggettoUpdatedEvent, SoggettoDeletedEvent, RuoloCreatedEvent, RuoloAssegnatoEvent
from backend.infrastructure.entities.repository import (
    SoggettoRepository, RuoloRepository, SoggettoRuoloRepository,
    IndirizzoRepository, ContattoRepository
)
from backend.infrastructure.entities.repository import SoggettoIndirizzo as SoggettoIndirizzoModel
from backend.infrastructure.entities.repository import SoggettoContatto as SoggettoContattoModel
from backend.extensions import db
from backend.application.entities.commands import (
    CreateSoggettoCommand, UpdateSoggettoCommand, DeleteSoggettoCommand,
    AssegnaRuoloCommand, RevocaRuoloCommand,
    CreateRuoloCommand, UpdateRuoloCommand, DeleteRuoloCommand,
    AggiungiIndirizzoCommand, AggiungiContattoCommand,
    IndirizzoData, ContattoData
)


class SoggettoCommandHandler:
    def __init__(self):
        self.repository = SoggettoRepository()
        self.ruolo_repo = SoggettoRuoloRepository()
        self.indirizzo_repo = IndirizzoRepository()
        self.contatto_repo = ContattoRepository()

    def handle_create(self, command: CreateSoggettoCommand) -> Soggetto:
        existing = self.repository.get_by_codice(command.tenant_id, command.codice)
        if existing:
            raise ValueError(f"Soggetto with codice {command.codice} already exists")

        soggetto = Soggetto(
            codice=command.codice,
            nome=command.nome,
            cognome=command.cognome,
            ragione_sociale=command.ragione_sociale,
            partita_iva=command.partita_iva,
            codice_fiscale=command.codice_fiscale,
            email_principale=command.email_principale,
            telefono_principale=command.telefono_principale,
            website=command.website,
            stato=command.stato,
            note=command.note,
            tags=command.tags,
            tenant_id=command.tenant_id,
            tipo_soggetto=command.tipo_soggetto,
        )
        result = self.repository.create(soggetto)

        for ruolo_data in command.ruoli:
            self.ruolo_repo.create(
                soggetto_id=result.id,
                ruolo_id=ruolo_data.ruolo_id,
                data_inizio=ruolo_data.data_inizio,
                data_fine=ruolo_data.data_fine,
                stato=ruolo_data.stato,
                parametri=ruolo_data.parametri,
            )

        for addr_data in command.indirizzi:
            addr_domain = self.indirizzo_repo.create(
                IndirizzoData(
                    denominazione=addr_data.denominazione,
                    numero_civico=addr_data.numero_civico,
                    CAP=addr_data.CAP,
                    città=addr_data.città,
                    provincia=addr_data.provincia,
                    regione=addr_data.regione,
                    nazione=addr_data.nazione,
                    latitudine=addr_data.latitudine,
                    longitudine=addr_data.longitudine,
                    indirizzo_completo=addr_data.indirizzo_completo,
                    tipo=addr_data.tipo,
                ),
                command.tenant_id
            )
            si = SoggettoIndirizzoModel(
                soggetto_id=result.id,
                indirizzo_id=addr_domain.id,
                tipo_riferimento=addr_data.tipo,
                is_preferred=False,
            )
            db.session.add(si)
            db.session.flush()

        for cont_data in command.contatti:
            cont_domain = self.contatto_repo.create(
                ContattoData(
                    canale=cont_data.canale,
                    valore=cont_data.valore,
                    tipo_utilizzo=cont_data.tipo_utilizzo,
                    is_verified=cont_data.is_verified,
                    is_preferred=cont_data.is_preferred,
                ),
                command.tenant_id
            )
            sc = SoggettoContattoModel(
                soggetto_id=result.id,
                contatto_id=cont_domain.id,
                tipo_riferimento=cont_data.tipo_utilizzo,
                is_primary=cont_data.is_preferred,
            )
            db.session.add(sc)
            db.session.flush()

        db.session.commit()
        return self.repository.get_by_id(result.id)

    def handle_update(self, command: UpdateSoggettoCommand) -> Soggetto:
        existing = self.repository.get_by_id(command.id)
        if not existing:
            raise ValueError(f"Soggetto {command.id} not found")

        if command.codice and command.codice != existing.codice:
            dup = self.repository.get_by_codice(command.tenant_id, command.codice)
            if dup and dup.id != command.id:
                raise ValueError(f"Soggetto with codice {command.codice} already exists")

        soggetto = Soggetto(
            id=command.id,
            codice=command.codice or existing.codice,
            nome=command.nome or existing.nome,
            cognome=command.cognome if command.cognome is not None else existing.cognome,
            ragione_sociale=command.ragione_sociale if command.ragione_sociale is not None else existing.ragione_sociale,
            partita_iva=command.partita_iva if command.partita_iva is not None else existing.partita_iva,
            codice_fiscale=command.codice_fiscale if command.codice_fiscale is not None else existing.codice_fiscale,
            email_principale=command.email_principale if command.email_principale is not None else existing.email_principale,
            telefono_principale=command.telefono_principale if command.telefono_principale is not None else existing.telefono_principale,
            website=command.website if command.website is not None else existing.website,
            stato=command.stato or existing.stato,
            note=command.note if command.note is not None else existing.note,
            tags=command.tags if command.tags is not None else existing.tags,
            tenant_id=command.tenant_id,
            tipo_soggetto=command.tipo_soggetto or existing.tipo_soggetto,
        )
        result = self.repository.update(soggetto)
        db.session.commit()
        return result

    def handle_delete(self, command: DeleteSoggettoCommand) -> None:
        existing = self.repository.get_by_id(command.id)
        if not existing:
            raise ValueError(f"Soggetto {command.id} not found")
        self.repository.delete(command.id)
        db.session.commit()


class SoggettoQueryHandler:
    def __init__(self):
        self.repository = SoggettoRepository()

    def handle_get_by_id(self, soggetto_id: int, tenant_id: int) -> Optional[Soggetto]:
        soggetto = self.repository.get_by_id(soggetto_id)
        if soggetto and soggetto.tenant_id != tenant_id:
            return None
        return soggetto

    def handle_get_by_codice(self, tenant_id: int, codice: str) -> Optional[Soggetto]:
        return self.repository.get_by_codice(tenant_id, codice)

    def handle_get_all(self, tenant_id: int, skip: int = 0, limit: int = 100) -> List[Soggetto]:
        return self.repository.get_by_tenant(tenant_id, skip, limit)


class RuoloCommandHandler:
    def __init__(self):
        self.repository = RuoloRepository()

    def handle_create(self, command: CreateRuoloCommand) -> Ruolo:
        existing = self.repository.get_by_codice(command.tenant_id, command.codice)
        if existing:
            raise ValueError(f"Ruolo with codice {command.codice} already exists")

        ruolo = Ruolo(
            codice=command.codice,
            nome=command.nome,
            descrizione=command.descrizione,
            categoria=command.categoria,
            richiede_credito=command.richiede_credito,
            richiede_contratto=command.richiede_contratto,
            soggetto_a_fatturazione=command.soggetto_a_fatturazione,
            tenant_id=command.tenant_id,
        )
        result = self.repository.create(ruolo)
        db.session.commit()
        return result

    def handle_update(self, command: UpdateRuoloCommand) -> Ruolo:
        existing = self.repository.get_by_id(command.id)
        if not existing:
            raise ValueError(f"Ruolo {command.id} not found")

        if command.codice and command.codice != existing.codice:
            dup = self.repository.get_by_codice(command.tenant_id, command.codice)
            if dup and dup.id != command.id:
                raise ValueError(f"Ruolo with codice {command.codice} already exists")

        ruolo = Ruolo(
            id=command.id,
            codice=command.codice or existing.codice,
            nome=command.nome or existing.nome,
            descrizione=command.descrizione if command.descrizione is not None else existing.descrizione,
            categoria=command.categoria if command.categoria is not None else existing.categoria,
            richiede_credito=command.richiede_credito if command.richiede_credito is not None else existing.richiede_credito,
            richiede_contratto=command.richiede_contratto if command.richiede_contratto is not None else existing.richiede_contratto,
            soggetto_a_fatturazione=command.soggetto_a_fatturazione if command.soggetto_a_fatturazione is not None else existing.soggetto_a_fatturazione,
            is_active=command.is_active if command.is_active is not None else existing.is_active,
            tenant_id=command.tenant_id,
        )
        result = self.repository.update(ruolo)
        db.session.commit()
        return result

    def handle_delete(self, command: DeleteRuoloCommand) -> None:
        existing = self.repository.get_by_id(command.id)
        if not existing:
            raise ValueError(f"Ruolo {command.id} not found")
        self.repository.delete(command.id)
        db.session.commit()


class RuoloQueryHandler:
    def __init__(self):
        self.repository = RuoloRepository()

    def handle_get_by_id(self, ruolo_id: int, tenant_id: int) -> Optional[Ruolo]:
        ruolo = self.repository.get_by_id(ruolo_id)
        if ruolo and ruolo.tenant_id != tenant_id:
            return None
        return ruolo

    def handle_get_all(self, tenant_id: int) -> List[Ruolo]:
        return self.repository.get_by_tenant(tenant_id)


class SoggettoRuoloCommandHandler:
    def __init__(self):
        self.repository = SoggettoRuoloRepository()
        self.soggetto_repo = SoggettoRepository()

    def handle_assegna(self, command: AssegnaRuoloCommand) -> dict:
        soggetto = self.soggetto_repo.get_by_id(command.soggetto_id)
        if not soggetto:
            raise ValueError(f"Soggetto {command.soggetto_id} not found")

        result = self.repository.create(
            soggetto_id=command.soggetto_id,
            ruolo_id=command.ruolo_id,
            data_inizio=command.data_inizio,
            data_fine=command.data_fine,
            stato=command.stato,
            parametri=command.parametri,
        )
        db.session.commit()
        return result

    def handle_revoca(self, command: RevocaRuoloCommand) -> None:
        self.repository.delete(command.soggetto_id, command.ruolo_id)
        db.session.commit()
