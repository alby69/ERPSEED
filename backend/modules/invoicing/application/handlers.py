import logging
from typing import Optional
from datetime import date

from backend.shared.handlers import CommandResult

from .commands import (
    CreateInvoiceCommand, CreateInvoiceFromSalesOrderCommand,
    UpdateInvoiceCommand, IssueInvoiceCommand,
    CancelInvoiceCommand, PayInvoiceCommand,
    GetInvoiceCommand, ListInvoicesCommand,
)
from ..domain.models import SalesInvoice, SalesInvoiceLine
from ..infrastructure.repository import InvoiceRepository

logger = logging.getLogger(__name__)


class CreateInvoiceHandler:
    def __init__(self, repository: InvoiceRepository):
        self.repository = repository

    def handle(self, command: CreateInvoiceCommand) -> CommandResult:
        try:
            invoice = SalesInvoice(
                tenant_id=command.tenant_id,
                party_id=command.party_id,
                sales_order_id=command.sales_order_id,
                date=command.date or date.today(),
                due_date=command.due_date,
                description=command.description,
                notes=command.notes,
                created_by=command.user_id,
            )
            for line_data in command.lines:
                line = SalesInvoiceLine.from_dict(line_data)
                line.tenant_id = command.tenant_id
                line.calculate_total()
                invoice.lines.append(line)

            invoice.calculate_totals()
            result = self.repository.create(invoice)
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error creating invoice: {e}")
            return CommandResult.error(f"Failed to create invoice: {str(e)}")


class CreateInvoiceFromSalesOrderHandler:
    def __init__(self, repository: InvoiceRepository):
        self.repository = repository

    def handle(self, command: CreateInvoiceFromSalesOrderCommand) -> CommandResult:
        try:
            result = self.repository.create_from_sales_order(
                tenant_id=command.tenant_id,
                sales_order_id=command.sales_order_id,
                user_id=command.user_id,
                invoice_date=command.date,
                due_date=command.due_date,
                description=command.description,
                notes=command.notes,
            )
            if "error" in result:
                return CommandResult.error(result["error"])
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error creating invoice from sales order: {e}")
            return CommandResult.error(f"Failed to create invoice: {str(e)}")


class UpdateInvoiceHandler:
    def __init__(self, repository: InvoiceRepository):
        self.repository = repository

    def handle(self, command: UpdateInvoiceCommand) -> CommandResult:
        try:
            data = {}
            for f in ("date", "due_date", "description", "notes"):
                v = getattr(command, f, None)
                if v is not None:
                    data[f] = v
            if command.lines is not None:
                data["lines"] = command.lines
            result = self.repository.update(command.entity_id, command.tenant_id, data)
            if not result:
                return CommandResult.error("Invoice not found")
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error updating invoice: {e}")
            return CommandResult.error(f"Failed to update invoice: {str(e)}")


class IssueInvoiceHandler:
    def __init__(self, repository: InvoiceRepository):
        self.repository = repository

    def handle(self, command: IssueInvoiceCommand) -> CommandResult:
        try:
            result = self.repository.issue(command.entity_id, command.tenant_id, command.user_id)
            if "error" in result:
                return CommandResult.error(result["error"])
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error issuing invoice: {e}")
            return CommandResult.error(f"Failed to issue invoice: {str(e)}")


class CancelInvoiceHandler:
    def __init__(self, repository: InvoiceRepository):
        self.repository = repository

    def handle(self, command: CancelInvoiceCommand) -> CommandResult:
        try:
            result = self.repository.cancel(command.entity_id, command.tenant_id, command.reason)
            if "error" in result:
                return CommandResult.error(result["error"])
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error cancelling invoice: {e}")
            return CommandResult.error(f"Failed to cancel invoice: {str(e)}")


class PayInvoiceHandler:
    def __init__(self, repository: InvoiceRepository):
        self.repository = repository

    def handle(self, command: PayInvoiceCommand) -> CommandResult:
        try:
            result = self.repository.mark_paid(
                command.entity_id, command.tenant_id,
                command.amount, command.payment_date or date.today()
            )
            if "error" in result:
                return CommandResult.error(result["error"])
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error paying invoice: {e}")
            return CommandResult.error(f"Failed to pay invoice: {str(e)}")


class GetInvoiceHandler:
    def __init__(self, repository: InvoiceRepository):
        self.repository = repository

    def handle(self, command: GetInvoiceCommand) -> CommandResult:
        try:
            result = self.repository.find_by_id(command.entity_id, command.tenant_id)
            if not result:
                return CommandResult.error("Invoice not found")
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error getting invoice: {e}")
            return CommandResult.error(f"Failed to get invoice: {str(e)}")


class ListInvoicesHandler:
    def __init__(self, repository: InvoiceRepository):
        self.repository = repository

    def handle(self, command: ListInvoicesCommand) -> CommandResult:
        try:
            result = self.repository.find_all(
                tenant_id=command.tenant_id,
                status=command.status,
                party_id=command.party_id,
                search=command.search,
                page=command.page,
                per_page=command.per_page,
            )
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error listing invoices: {e}")
            return CommandResult.error(f"Failed to list invoices: {str(e)}")
