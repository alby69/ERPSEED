import logging
from typing import Optional

from backend.shared.handlers import CommandResult
from .application.handlers import (
    CreateInvoiceHandler, CreateInvoiceFromSalesOrderHandler,
    UpdateInvoiceHandler, IssueInvoiceHandler,
    CancelInvoiceHandler, PayInvoiceHandler,
    GetInvoiceHandler, ListInvoicesHandler,
)
from .application.commands import (
    CreateInvoiceCommand, CreateInvoiceFromSalesOrderCommand,
    UpdateInvoiceCommand, IssueInvoiceCommand,
    CancelInvoiceCommand, PayInvoiceCommand,
    GetInvoiceCommand, ListInvoicesCommand,
)
from .infrastructure.repository import InvoiceRepository

logger = logging.getLogger(__name__)


class InvoicingService:
    COMMAND_HANDLERS = {
        "CreateInvoice": CreateInvoiceHandler,
        "CreateInvoiceFromSalesOrder": CreateInvoiceFromSalesOrderHandler,
        "UpdateInvoice": UpdateInvoiceHandler,
        "IssueInvoice": IssueInvoiceHandler,
        "CancelInvoice": CancelInvoiceHandler,
        "PayInvoice": PayInvoiceHandler,
        "GetInvoice": GetInvoiceHandler,
        "ListInvoices": ListInvoicesHandler,
    }

    def __init__(self, repository: InvoiceRepository = None):
        self._repository = repository
        self._handlers = {}

    @property
    def repository(self) -> InvoiceRepository:
        if self._repository is None:
            self._repository = InvoiceRepository()
        return self._repository

    def _get_handler(self, command_name: str):
        if command_name not in self._handlers:
            handler_class = self.COMMAND_HANDLERS.get(command_name)
            if not handler_class:
                return None
            self._handlers[command_name] = handler_class(repository=self.repository)
        return self._handlers[command_name]

    def execute(self, command_data: dict) -> dict:
        command_name = command_data.get("command")
        if not command_name:
            return CommandResult.error("Command name is required").to_dict()
        handler = self._get_handler(command_name)
        if not handler:
            return CommandResult.error(f"Unknown command: {command_name}").to_dict()
        command = self._parse_command(command_name, command_data)
        if isinstance(command, CommandResult):
            return command.to_dict()
        try:
            result = handler.handle(command)
            return result.to_dict()
        except Exception as e:
            logger.error(f"Error executing {command_name}: {e}", exc_info=True)
            return CommandResult.error(f"Internal error: {str(e)}").to_dict()

    def _parse_command(self, command_name: str, data: dict):
        command_classes = {
            "CreateInvoice": CreateInvoiceCommand,
            "CreateInvoiceFromSalesOrder": CreateInvoiceFromSalesOrderCommand,
            "UpdateInvoice": UpdateInvoiceCommand,
            "IssueInvoice": IssueInvoiceCommand,
            "CancelInvoice": CancelInvoiceCommand,
            "PayInvoice": PayInvoiceCommand,
            "GetInvoice": GetInvoiceCommand,
            "ListInvoices": ListInvoicesCommand,
        }
        cmd_class = command_classes.get(command_name)
        if not cmd_class:
            return CommandResult.error(f"Unknown command: {command_name}")
        try:
            cmd = cmd_class.from_dict(data)
            if hasattr(cmd, "entity_id") and not cmd.entity_id:
                cmd.entity_id = data.get("entity_id", data.get("id", 0))
            return cmd
        except Exception as e:
            return CommandResult.error(f"Invalid command data: {str(e)}")


_service_instance = None


def get_invoicing_service() -> InvoicingService:
    global _service_instance
    if _service_instance is None:
        _service_instance = InvoicingService()
    return _service_instance


def execute(command_data: dict) -> dict:
    return get_invoicing_service().execute(command_data)
