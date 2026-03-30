"""
Accounting Plugin Routes.

API endpoints for accounting operations:
- Chart of Accounts management
- Journal Entry management
- Invoice management
"""
from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
import datetime
from marshmallow import fields

from .models import ChartOfAccounts, Account, JournalEntry, JournalEntryLine, Invoice, InvoiceLine
from backend.core.services.tenant_context import TenantContext
from backend.core.decorators.decorators import tenant_required
from backend.extensions import db, ma
from backend.core.schemas.schemas import BaseSchema
from backend.core.services.generic_service import generic_service
from backend.core.utils.utils import paginate, apply_filters, apply_sorting

blp = Blueprint("accounting", __name__, url_prefix="/accounting", description="Accounting Operations")

class ChartOfAccountsSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = ChartOfAccounts

class ChartOfAccountsUpdateSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = ChartOfAccounts
        load_instance = False

class AccountSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = Account

class JournalEntryLineSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = JournalEntryLine
        exclude = BaseSchema.Meta.exclude + ('entry',)

class JournalEntrySchema(BaseSchema):
    date = fields.Date(load_default=None)
    lines = fields.List(fields.Nested(JournalEntryLineSchema))
    total_debit = fields.Function(lambda obj: obj.total_debit, dump_only=True)
    total_credit = fields.Function(lambda obj: obj.total_credit, dump_only=True)
    is_balanced = fields.Function(lambda obj: obj.is_balanced, dump_only=True)
    class Meta(BaseSchema.Meta):
        model = JournalEntry
        exclude = BaseSchema.Meta.exclude + ("date",)

class InvoiceLineSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = InvoiceLine
        exclude = BaseSchema.Meta.exclude + ('invoice',)

class InvoiceSchema(BaseSchema):
    date = fields.Date(load_default=None)
    lines = fields.List(fields.Nested(InvoiceLineSchema))
    class Meta(BaseSchema.Meta):
        model = Invoice
        exclude = BaseSchema.Meta.exclude + ("date",)


@blp.route("/coa")
class COAList(MethodView):
    """Chart of Accounts endpoints."""
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.response(200, ChartOfAccountsSchema(many=True))
    def get(self, tenant_id):
        """List all accounts in Chart of Accounts."""
        query = ChartOfAccounts.query.filter_by(tenant_id=tenant_id, is_active=True)
        query = apply_filters(query, ChartOfAccounts, ['code', 'name'])
        query = apply_sorting(query, ChartOfAccounts, default_sort_column='code')
        items, headers = paginate(query)
        return items, 200, headers
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.arguments(ChartOfAccountsSchema)
    @blp.response(201, ChartOfAccountsSchema)
    def post(self, coa_instance, tenant_id):
        """Create new account in Chart of Accounts."""
        return generic_service.create_tenant_resource(
            ChartOfAccounts, coa_instance, tenant_id, unique_fields=['code']
        )


@blp.route("/coa/<int:coa_id>")
class COAResource(MethodView):
    """Single Chart of Accounts entry."""
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.response(200, ChartOfAccountsSchema)
    def get(self, coa_id, tenant_id):
        """Get account by ID."""
        return generic_service.get_tenant_resource(
            ChartOfAccounts, coa_id, tenant_id, not_found_message="Account not found"
        )
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.arguments(ChartOfAccountsUpdateSchema(partial=True))
    @blp.response(200, ChartOfAccountsSchema)
    def put(self, data, coa_id, tenant_id):
        """Update account."""
        return generic_service.update_tenant_resource(
            ChartOfAccounts, coa_id, tenant_id, data, not_found_message="Account not found"
        )
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.response(204)
    def delete(self, coa_id, tenant_id):
        """Deactivate account (soft delete)."""
        coa = ChartOfAccounts.query.filter_by(id=coa_id, tenant_id=tenant_id).first()
        if not coa:
            abort(404, message="Account not found")
        
        # Prevent deactivation if any associated account has a non-zero balance
        accounts_with_balance = Account.query.filter(
            Account.coa_id == coa.id,
            Account.balance != 0
        ).first()
        if accounts_with_balance:
            abort(409, message="Cannot deactivate account with a non-zero balance in one of its sub-accounts.")

        coa.is_active = False
        Account.query.filter_by(coa_id=coa.id).update({"is_active": False})

        db.session.commit()
        return '', 204


@blp.route("/accounts")
class AccountList(MethodView):
    """Account endpoints."""
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.response(200, AccountSchema(many=True))
    def get(self, tenant_id):
        """List all active accounts."""
        query = Account.query.filter_by(tenant_id=tenant_id, is_active=True)
        query = apply_filters(query, Account, ['code', 'name'])
        query = apply_sorting(query, Account, default_sort_column='code')
        items, headers = paginate(query)
        return items, 200, headers
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.arguments(AccountSchema)
    @blp.response(201, AccountSchema)
    def post(self, account_instance, tenant_id):
        """Create new account."""
        return generic_service.create_tenant_resource(
            Account, account_instance, tenant_id, unique_fields=['code']
        )


@blp.route("/journal")
class JournalEntryList(MethodView):
    """Journal Entry endpoints."""
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.response(200, JournalEntrySchema(many=True))
    def get(self, tenant_id):
        """List journal entries."""
        query = JournalEntry.query.filter_by(tenant_id=tenant_id)
        query = apply_filters(query, JournalEntry, ['entry_number', 'description', 'reference'])
        
        sort_by = request.args.get('sort_by')
        if not sort_by:
             query = query.order_by(JournalEntry.date.desc(), JournalEntry.entry_number.desc())
        else:
             query = apply_sorting(query, JournalEntry)
        items, headers = paginate(query)
        return items, 200, headers
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.arguments(JournalEntrySchema)
    @blp.response(201, JournalEntrySchema)
    def post(self, entry_instance, tenant_id):
        """Create journal entry with double-entry validation."""
        # The lines are already on the instance from Marshmallow
        lines = entry_instance.lines
        
        total_debit = sum(line.debit for line in lines)
        total_credit = sum(line.credit for line in lines)
        
        if abs(total_debit - total_credit) > 0.01:
            abort(400, message=f"Debits ({total_debit}) must equal credits ({total_credit}).")
        
        entry_number = self._generate_entry_number(tenant_id)
        
        # Set tenant_id and other server-side fields on the main instance
        entry_instance.tenant_id = tenant_id
        entry_instance.entry_number = entry_number
        entry_instance.created_by = get_jwt_identity()
        if not entry_instance.date:
            entry_instance.date = datetime.date.today()

        # Set tenant_id for each line and update account balances
        for line in lines:
            line.tenant_id = tenant_id
            account = db.session.get(Account, line.account_id)
            if not account or account.tenant_id != tenant_id:
                abort(400, message=f"Account with ID {line.account_id} not found for this tenant.")
            account.balance += line.debit - line.credit

        db.session.add(entry_instance)
        db.session.commit()
        
        try:
            from backend.webhook_triggers import on_journal_entry_created
            on_journal_entry_created(entry_instance)
        except Exception:
            pass
        
        return entry_instance, 201
    
    def _generate_entry_number(self, tenant_id):
        """Generate unique entry number."""
        today = datetime.date.today()
        year = today.year
        
        last_entry = JournalEntry.query.filter(
            JournalEntry.tenant_id == tenant_id,
            JournalEntry.entry_number.like(f'JE-{year}%')
        ).order_by(JournalEntry.entry_number.desc()).first()
        
        if last_entry:
            last_num = int(last_entry.entry_number.split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1
        
        return f'JE-{year}-{new_num:05d}'


@blp.route("/journal/<int:entry_id>")
class JournalEntryResource(MethodView):
    """Single Journal Entry."""
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.response(200, JournalEntrySchema)
    def get(self, entry_id, tenant_id):
        """Get journal entry with lines."""
        return generic_service.get_tenant_resource(
            JournalEntry, entry_id, tenant_id, not_found_message="Journal entry not found"
        )
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.response(200, JournalEntrySchema)
    def post(self, entry_id, tenant_id):
        """Post (validate and finalize) journal entry."""
        entry = JournalEntry.query.filter_by(id=entry_id, tenant_id=tenant_id).first()
        if not entry:
            abort(404, message="Journal entry not found")
        
        if entry.status != 'draft':
            abort(400, message="Only draft entries can be posted.")
        
        if not entry.is_balanced:
            abort(400, message="Entry must be balanced before posting.")
        
        entry.status = 'posted'
        db.session.commit()
        
        return entry


@blp.route("/invoices")
class InvoiceList(MethodView):
    """Invoice endpoints."""
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.response(200, InvoiceSchema(many=True))
    def get(self, tenant_id):
        """List invoices."""
        query = Invoice.query.filter_by(tenant_id=tenant_id)
        
        if request.args.get('type'):
            query = query.filter_by(invoice_type=request.args.get('type'))
        if request.args.get('status'):
            query = query.filter_by(status=request.args.get('status'))
        
        query = apply_filters(query, Invoice, ['invoice_number', 'description'])
        
        sort_by = request.args.get('sort_by')
        if not sort_by:
             query = query.order_by(Invoice.date.desc())
        else:
             query = apply_sorting(query, Invoice)
             
        items, headers = paginate(query)
        return items, 200, headers
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.arguments(InvoiceSchema)
    @blp.response(201, InvoiceSchema)
    def post(self, invoice_instance, tenant_id):
        """Create new invoice."""
        invoice_number = self._generate_invoice_number(tenant_id, invoice_instance.invoice_type)
        
        # Set server-side fields on the instance from Marshmallow
        invoice_instance.tenant_id = tenant_id
        invoice_instance.invoice_number = invoice_number
        if not invoice_instance.date:
            invoice_instance.date = datetime.date.today()
        
        subtotal = 0
        # Process lines that were loaded by Marshmallow
        for line in invoice_instance.lines:
            line.tenant_id = tenant_id
            line.calculate()
            subtotal += line.amount
        
        invoice_instance.subtotal = subtotal
        invoice_instance.tax_amount = sum(l.amount - (l.amount / (1 + l.tax_percent/100)) for l in invoice_instance.lines if l.tax_percent > 0)
        invoice_instance.total = invoice_instance.subtotal + invoice_instance.tax_amount
        
        db.session.add(invoice_instance)
        db.session.commit()
        
        try:
            from backend.webhook_triggers import on_invoice_created
            on_invoice_created(invoice_instance)
        except Exception:
            pass
        
        return invoice_instance, 201
    
    def _generate_invoice_number(self, tenant_id, invoice_type):
        """Generate unique invoice number."""
        prefix = 'AR' if invoice_type == 'AR' else 'AP'
        today = datetime.date.today()
        
        last_invoice = Invoice.query.filter(
            Invoice.tenant_id == tenant_id,
            Invoice.invoice_number.like(f'{prefix}%')
        ).order_by(Invoice.invoice_number.desc()).first()
        
        if last_invoice:
            last_num = int(last_invoice.invoice_number.split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1
        
        return f'{prefix}-{today.year}{today.month:02d}-{new_num:05d}'


@blp.route("/invoices/<int:invoice_id>")
class InvoiceResource(MethodView):
    """Single Invoice."""
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.response(200, InvoiceSchema)
    def get(self, invoice_id, tenant_id):
        """Get invoice with lines."""
        return generic_service.get_tenant_resource(
            Invoice, invoice_id, tenant_id, not_found_message="Invoice not found"
        )
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.response(200, InvoiceSchema)
    def post(self, invoice_id, tenant_id):
        """Send/Confirm invoice."""
        invoice = Invoice.query.filter_by(id=invoice_id, tenant_id=tenant_id).first()
        if not invoice:
            abort(404, message="Invoice not found")
        
        if invoice.status != 'draft':
            abort(400, message="Only draft invoices can be sent.")
        
        invoice.status = 'sent'
        db.session.commit()
        
        return invoice


@blp.route("/reports/trial-balance")
class TrialBalance(MethodView):
    """Trial Balance Report."""
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.response(200, fields.Dict())
    def get(self, tenant_id):
        """Generate trial balance report."""
        accounts = Account.query.filter_by(tenant_id=tenant_id, is_active=True).all()
        
        result = []
        total_debit = 0
        total_credit = 0
        
        for account in accounts:
            balance = db.session.query(
                func.coalesce(func.sum(JournalEntryLine.debit), 0) - 
                func.coalesce(func.sum(JournalEntryLine.credit), 0)
            ).filter(
                JournalEntryLine.account_id == account.id,
                JournalEntryLine.tenant_id == tenant_id
            ).scalar()
            
            entry = {
                'code': account.code,
                'name': account.name,
                'type': account.coa.type if account.coa else 'unknown',
                'balance': balance or 0
            }
            
            result.append(entry)
            
            if entry['type'] in ['asset', 'expense']:
                if balance and balance > 0:
                    total_debit += balance
                else:
                    total_credit += abs(balance)
            else:
                if balance and balance > 0:
                    total_credit += balance
                else:
                    total_debit += abs(balance)
        
        return {
            'accounts': result,
            'total_debit': total_debit,
            'total_credit': total_credit,
            'balanced': abs(total_debit - total_credit) < 0.01
        }
