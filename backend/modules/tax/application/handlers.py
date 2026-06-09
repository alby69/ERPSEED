import logging
from typing import Optional
from backend.shared.handlers import CommandHandler, CommandResult, CreateHandler, UpdateHandler, DeleteHandler, QueryHandler
from backend.shared.events.event_bus import get_event_bus
from .commands import (
    CreateTaxRateCommand, UpdateTaxRateCommand, DeleteTaxRateCommand,
    GetTaxRateQuery, ListTaxRatesQuery,
)
from ..domain.models import TaxRate
from ..domain.events import TaxRateCreatedEvent, TaxRateUpdatedEvent, TaxRateDeletedEvent
from ..infrastructure.repository import TaxRateRepository

logger = logging.getLogger(__name__)


class CreateTaxRateHandler(CreateHandler):
    def __init__(self, repository: TaxRateRepository, event_bus=None):
        self.repository = repository
        self.event_bus = event_bus

    def handle(self, command: CreateTaxRateCommand) -> CommandResult:
        tax_rate = TaxRate.from_dict(command.to_payload())
        errors = tax_rate.validate()
        if errors:
            return CommandResult(success=False, errors=errors)

        existing = self.repository.find_by_code(command.code, command.tenant_id)
        if existing:
            return CommandResult(success=False, errors=[f"Tax rate with code '{command.code}' already exists"])

        created = self.repository.create({
            **tax_rate.to_dict(),
            "tenant_id": command.tenant_id,
        })

        if self.event_bus:
            self.event_bus.publish(TaxRateCreatedEvent(created["id"], created, command.tenant_id))

        return CommandResult(success=True, data=created)


class UpdateTaxRateHandler(UpdateHandler):
    def __init__(self, repository: TaxRateRepository, event_bus=None):
        self.repository = repository
        self.event_bus = event_bus

    def handle(self, command: UpdateTaxRateCommand) -> CommandResult:
        existing = self.repository.find_by_id(command.entity_id, command.tenant_id)
        if not existing:
            return CommandResult(success=False, errors=["Tax rate not found"])

        if command.code and command.code != existing["code"]:
            duplicate = self.repository.find_by_code(command.code, command.tenant_id)
            if duplicate and duplicate["id"] != command.entity_id:
                return CommandResult(success=False, errors=[f"Tax rate with code '{command.code}' already exists"])

        result = self.repository.update(command.entity_id, command.tenant_id, command.to_payload())

        if self.event_bus:
            self.event_bus.publish(TaxRateUpdatedEvent(command.entity_id, result["old"], result["new"], command.tenant_id))

        return CommandResult(success=True, data=result["new"])


class DeleteTaxRateHandler(DeleteHandler):
    def __init__(self, repository: TaxRateRepository):
        self.repository = repository

    def handle(self, command: DeleteTaxRateCommand) -> CommandResult:
        existing = self.repository.find_by_id(command.entity_id, command.tenant_id)
        if not existing:
            return CommandResult(success=False, errors=["Tax rate not found"])

        self.repository.delete(command.entity_id, command.tenant_id)

        return CommandResult(success=True, data={"message": "Tax rate deleted"})


class GetTaxRateHandler(QueryHandler):
    def __init__(self, repository: TaxRateRepository):
        self.repository = repository

    def handle(self, query: GetTaxRateQuery) -> CommandResult:
        tax_rate = self.repository.find_by_id(query.entity_id, query.tenant_id)
        if not tax_rate:
            return CommandResult(success=False, errors=["Tax rate not found"])
        return CommandResult(success=True, data=tax_rate)


class ListTaxRatesHandler(QueryHandler):
    def __init__(self, repository: TaxRateRepository):
        self.repository = repository

    def handle(self, query: ListTaxRatesQuery) -> CommandResult:
        result = self.repository.find_all(
            tenant_id=query.tenant_id,
            search=query.search,
            is_active=query.is_active,
            page=query.page,
            per_page=query.per_page,
        )
        return CommandResult(success=True, data=result)
