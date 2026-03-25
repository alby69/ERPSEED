import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.domain.entities.models import Soggetto, Ruolo, TipoSoggetto, StatoSoggetto
from backend.domain.entities.events import SoggettoCreatedEvent, SoggettoUpdatedEvent


class TestDomainModels:
    def test_soggetto_denominazione_persona_fisica(self):
        soggetto = Soggetto(
            id=1,
            nome="Mario",
            cognome="Rossi",
            tipo_soggetto="persona_fisica"
        )
        assert soggetto.denominazione == "Rossi Mario"

    def test_soggetto_denominazione_persona_giuridica(self):
        soggetto = Soggetto(
            id=1,
            nome="Azienda",
            ragione_sociale="Rossi S.p.A.",
            tipo_soggetto="persona_giuridica"
        )
        assert soggetto.denominazione == "Rossi S.p.A."

    def test_soggetto_denominazione_fallback(self):
        soggetto = Soggetto(
            id=1,
            nome="Azienda",
            tipo_soggetto="persona_giuridica"
        )
        assert soggetto.denominazione == "Azienda"

    def test_soggetto_default_values(self):
        soggetto = Soggetto(nome="Test")
        assert soggetto.tipo_soggetto == "persona_fisica"
        assert soggetto.stato == "attivo"
        assert soggetto.ruoli == []
        assert soggetto.indirizzi == []
        assert soggetto.contatti == []

    def test_ruolo_default_values(self):
        ruolo = Ruolo(codice="CLI", nome="Cliente")
        assert ruolo.is_active is True
        assert ruolo.richiede_credito is False
        assert ruolo.richiede_contratto is False
        assert ruolo.soggetto_a_fatturazione is False

    def test_tipo_soggetto_enum(self):
        assert TipoSoggetto.PERSONA_FISICA == "persona_fisica"
        assert TipoSoggetto.PERSONA_GIURIDICA == "persona_giuridica"
        assert TipoSoggetto.ENTE == "ente"

    def test_stato_soggetto_enum(self):
        assert StatoSoggetto.ATTIVO == "attivo"
        assert StatoSoggetto.INATTIVO == "inattivo"
        assert StatoSoggetto.SOSPESO == "sospeso"


class TestDomainEvents:
    def test_soggetto_created_event(self):
        event = SoggettoCreatedEvent(
            soggetto_id=1,
            tenant_id=1,
            codice="CLI001",
            tipo_soggetto="persona_fisica"
        )
        assert event.soggetto_id == 1
        assert event.tenant_id == 1
        assert event.codice == "CLI001"

    def test_soggetto_updated_event(self):
        event = SoggettoUpdatedEvent(soggetto_id=1, tenant_id=1)
        assert event.soggetto_id == 1
        assert event.tenant_id == 1

    def test_soggetto_deleted_event(self):
        from backend.domain.entities.events import SoggettoDeletedEvent
        event = SoggettoDeletedEvent(soggetto_id=1, tenant_id=1)
        assert event.soggetto_id == 1
        assert event.tenant_id == 1

    def test_ruolo_created_event(self):
        from backend.domain.entities.events import RuoloCreatedEvent
        event = RuoloCreatedEvent(ruolo_id=1, tenant_id=1, codice="FORN")
        assert event.ruolo_id == 1
        assert event.codice == "FORN"

    def test_ruolo_assegnato_event(self):
        from backend.domain.entities.events import RuoloAssegnatoEvent
        event = RuoloAssegnatoEvent(soggetto_id=1, ruolo_id=2, tenant_id=1)
        assert event.soggetto_id == 1
        assert event.ruolo_id == 2


class TestCommands:
    def test_create_soggetto_command(self):
        from backend.application.entities.commands import CreateSoggettoCommand
        cmd = CreateSoggettoCommand(
            tenant_id=1,
            codice="CLI001",
            nome="Mario",
            cognome="Rossi"
        )
        assert cmd.tenant_id == 1
        assert cmd.codice == "CLI001"
        assert cmd.nome == "Mario"
        assert cmd.cognome == "Rossi"
        assert cmd.tipo_soggetto == "persona_fisica"

    def test_update_soggetto_command(self):
        from backend.application.entities.commands import UpdateSoggettoCommand
        cmd = UpdateSoggettoCommand(id=1, tenant_id=1, nome="Giuseppe")
        assert cmd.id == 1
        assert cmd.nome == "Giuseppe"

    def test_delete_soggetto_command(self):
        from backend.application.entities.commands import DeleteSoggettoCommand
        cmd = DeleteSoggettoCommand(id=1, tenant_id=1)
        assert cmd.id == 1
        assert cmd.tenant_id == 1

    def test_create_ruolo_command(self):
        from backend.application.entities.commands import CreateRuoloCommand
        cmd = CreateRuoloCommand(
            tenant_id=1,
            codice="CLI",
            nome="Cliente",
            richiede_credito=True
        )
        assert cmd.codice == "CLI"
        assert cmd.richiede_credito is True

    def test_assegna_ruolo_command(self):
        from backend.application.entities.commands import AssegnaRuoloCommand
        cmd = AssegnaRuoloCommand(soggetto_id=1, ruolo_id=2, tenant_id=1)
        assert cmd.soggetto_id == 1
        assert cmd.ruolo_id == 2

    def test_indirizzo_data(self):
        from backend.application.entities.commands import IndirizzoData
        addr = IndirizzoData(città="Roma", provincia="RM")
        assert addr.città == "Roma"
        assert addr.nazione == "IT"

    def test_contatto_data(self):
        from backend.application.entities.commands import ContattoData
        cont = ContattoData(canale="email", valore="test@example.com")
        assert cont.canale == "email"
        assert cont.is_verified is False


class TestHandlersImport:
    def test_handler_imports(self):
        from backend.application.entities.handlers import (
            SoggettoCommandHandler,
            SoggettoQueryHandler,
            RuoloCommandHandler,
            RuoloQueryHandler,
            SoggettoRuoloCommandHandler,
        )
        assert SoggettoCommandHandler is not None
        assert SoggettoQueryHandler is not None
        assert RuoloCommandHandler is not None
        assert RuoloQueryHandler is not None
        assert SoggettoRuoloCommandHandler is not None


class TestRepositoryImports:
    def test_repository_imports(self):
        from backend.infrastructure.entities.repository import (
            SoggettoRepository,
            RuoloRepository,
            SoggettoRuoloRepository,
            IndirizzoRepository,
            ContattoRepository,
        )
        assert SoggettoRepository is not None
        assert RuoloRepository is not None
        assert SoggettoRuoloRepository is not None
        assert IndirizzoRepository is not None
        assert ContattoRepository is not None


class TestEndpointsBlueprint:
    def test_endpoints_blueprint_exists(self):
        from backend.endpoints.entities import entities_bp
        assert entities_bp is not None
        assert entities_bp.url_prefix == "/api/entities"

    def test_endpoints_routes_registered(self):
        from backend.endpoints.entities import entities_bp
        assert hasattr(entities_bp, 'add_url_rule')
        assert entities_bp.url_prefix == "/api/entities"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
