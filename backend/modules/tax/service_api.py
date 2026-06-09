import logging
from typing import Dict, Any, Optional
from backend.extensions import db

from .application.commands import (
    CreateTaxRateCommand, UpdateTaxRateCommand, DeleteTaxRateCommand,
    GetTaxRateQuery, ListTaxRatesQuery,
)
from .application.handlers import (
    CreateTaxRateHandler, UpdateTaxRateHandler, DeleteTaxRateHandler,
    GetTaxRateHandler, ListTaxRatesHandler,
)
from .infrastructure.repository import TaxRateRepository

logger = logging.getLogger(__name__)

COMMAND_HANDLERS = {
    "CreateTaxRate": ("create", CreateTaxRateHandler, CreateTaxRateCommand),
    "UpdateTaxRate": ("update", UpdateTaxRateHandler, UpdateTaxRateCommand),
    "DeleteTaxRate": ("delete", DeleteTaxRateHandler, DeleteTaxRateCommand),
    "GetTaxRate": ("get", GetTaxRateHandler, GetTaxRateQuery),
    "ListTaxRates": ("list", ListTaxRatesHandler, ListTaxRatesQuery),
}


class TaxService:
    def __init__(self, repository: TaxRateRepository, event_bus=None):
        self.repository = repository
        self.event_bus = event_bus

    def execute(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        command_name = command_data.get("command", "")
        if not command_name:
            return {"success": False, "error": "command is required"}

        handler_info = COMMAND_HANDLERS.get(command_name)
        if not handler_info:
            return {"success": False, "error": f"Unknown command: {command_name}"}

        command_type, handler_cls, command_cls = handler_info
        command = command_cls.from_dict(command_data)
        command.tenant_id = command_data.get("tenant_id")

        handler = handler_cls(self.repository, self.event_bus)
        result = handler.handle(command)

        return result.to_dict()


_service_instance = None


def get_tax_service():
    global _service_instance
    if _service_instance is None:
        _service_instance = TaxService(repository=TaxRateRepository(db=db))
    return _service_instance


def execute(command_data: Dict[str, Any]) -> Dict[str, Any]:
    return get_tax_service().execute(command_data)
