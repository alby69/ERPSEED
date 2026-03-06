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
from backend.extensions import db, ma

blp = Blueprint("accounting", __name__, url_prefix="/accounting", description="Accounting Operations")

class ChartOfAccountsSchema(ma.SQLAlchemyAutoSchema):
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    class Meta:
        model = ChartOfAccounts
        load_instance = True
        include_fk = True

class AccountSchema(ma.SQLAlchemyAutoSchema):
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    class Meta:
        model = Account
        load_instance = True
        include_fk = True

class JournalEntryLineSchema(ma.SQLAlchemyAutoSchema):
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    class Meta:
        model = JournalEntryLine
        load_instance = True
        include_fk = True
        exclude = ('entry',)

class JournalEntrySchema(ma.SQLAlchemyAutoSchema):
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    date = fields.Date()
    lines = fields.List(fields.Nested(JournalEntryLineSchema))
    class Meta:
        model = JournalEntry
        load_instance = True
        include_fk = True

class InvoiceLineSchema(ma.SQLAlchemyAutoSchema):
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    class Meta:
        model = InvoiceLine
        load_instance = True
        include_fk = True
        exclude = ('invoice',)

class InvoiceSchema(ma.SQLAlchemyAutoSchema):
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    date = fields.Date()
    lines = fields.List(fields.Nested(InvoiceLineSchema))
    class Meta:
        model = Invoice
        load_instance = True
        include_fk = True


def get_tenant_query(model):
    """Get query filtered by current tenant."""
    tenant_id = TenantContext.get_tenant_id()
    if tenant_id is None:
        abort(403, message="Tenant context not found")
    return model.query.filter_by(tenant_id=tenant_id)


@blp.route("/coa")
class COAList(MethodView):
    """Chart of Accounts endpoints."""
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, ChartOfAccountsSchema(many=True))
    def get(self):
        """List all accounts in Chart of Accounts."""
        tenant_id = TenantContext.get_tenant_id()
        if tenant_id is None:
            abort(403, message="Tenant context not found")
        query = ChartOfAccounts.query.filter_by(tenant_id=tenant_id, is_active=True).order_by(ChartOfAccounts.code)
        return query.all()
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(ChartOfAccountsSchema)
    @blp.response(201, ChartOfAccountsSchema)
    def post(self):
        """Create new account in Chart of Accounts."""
        data = request.get_json()
        tenant_id = TenantContext.get_tenant_id()
        if tenant_id is None:
            abort(403, message="Tenant context not found")
        
        existing = ChartOfAccounts.query.filter_by(tenant_id=tenant_id, code=data['code']).first()
        if existing:
            abort(409, message=f"Account code '{data['code']}' already exists.")
        
        coa = ChartOfAccounts(
            tenant_id=tenant_id, # type: ignore
            code=data['code'], # type: ignore
            name=data['name'], # type: ignore
            type=data['type'], # type: ignore
            parent_id=data.get('parent_id'), # type: ignore
            allow_transaction=data.get('allow_transaction', True) # type: ignore
        )
        
        db.session.add(coa)
        db.session.commit()
        
        return coa, 201


@blp.route("/coa/<int:coa_id>")
class COAResource(MethodView):
    """Single Chart of Accounts entry."""
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, ChartOfAccountsSchema)
    def get(self, coa_id):
        """Get account by ID."""
        tenant_id = TenantContext.get_tenant_id()
        if tenant_id is None:
            abort(403, message="Tenant context not found")
        coa = ChartOfAccounts.query.filter_by(id=coa_id, tenant_id=tenant_id).first()
        if not coa:
            abort(404, message="Account not found")
        return coa
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(ChartOfAccountsSchema(partial=True))
    @blp.response(200, ChartOfAccountsSchema)
    def put(self, coa_id):
        """Update account."""
        data = request.get_json()
        tenant_id = TenantContext.get_tenant_id()
        if tenant_id is None:
            abort(403, message="Tenant context not found")
        coa = ChartOfAccounts.query.filter_by(id=coa_id, tenant_id=tenant_id).first()
        if not coa:
            abort(404, message="Account not found")
        
        for key, value in data.items():
            if hasattr(coa, key):
                setattr(coa, key, value)
        
        db.session.commit()
        return coa
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(204)
    def delete(self, coa_id):
        """Deactivate account (soft delete)."""
        tenant_id = TenantContext.get_tenant_id()
        if tenant_id is None:
            abort(403, message="Tenant context not found")
        coa = ChartOfAccounts.query.filter_by(id=coa_id, tenant_id=tenant_id).first()
        if not coa:
            abort(404, message="Account not found")
        coa.is_active = False
        
        db.session.commit()
        return '', 204


@blp.route("/accounts")
class AccountList(MethodView):
    """Account endpoints."""
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, AccountSchema(many=True))
    def get(self):
        """List all active accounts."""
        tenant_id = TenantContext.get_tenant_id()
        if tenant_id is None:
            abort(403, message="Tenant context not found")
        query = Account.query.filter_by(tenant_id=tenant_id, is_active=True).order_by(Account.code)
        return query.all()
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(AccountSchema)
    @blp.response(201, AccountSchema)
    def post(self):
        """Create new account."""
        data = request.get_json()
        tenant_id = TenantContext.get_tenant_id()
        if tenant_id is None:
            abort(403, message="Tenant context not found")
        
        existing = Account.query.filter_by(tenant_id=tenant_id, code=data['code']).first()
        if existing:
            abort(409, message=f"Account code '{data['code']}' already exists.")
        
        account = Account(
            tenant_id=tenant_id, # type: ignore
            coa_id=data['coa_id'], # type: ignore
            code=data['code'], # type: ignore
            name=data['name'], # type: ignore
            description=data.get('description') # type: ignore
        )
        
        db.session.add(account)
        db.session.commit()
        
        return account, 201


@blp.route("/journal")
class JournalEntryList(MethodView):
    """Journal Entry endpoints."""
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, JournalEntrySchema(many=True))
    def get(self):
        """List journal entries."""
        tenant_id = TenantContext.get_tenant_id()
        if tenant_id is None:
            abort(403, message="Tenant context not found")
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        query = JournalEntry.query.filter_by(tenant_id=tenant_id).order_by(JournalEntry.date.desc(), JournalEntry.entry_number.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return pagination.items
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(JournalEntrySchema)
    @blp.response(201, JournalEntrySchema)
    def post(self):
        """Create journal entry with double-entry validation."""
        data = request.get_json()
        lines = data.pop('lines', [])
        
        tenant_id = TenantContext.get_tenant_id()
        if tenant_id is None:
            abort(403, message="Tenant context not found")
        
        total_debit = sum(l.get('debit', 0) for l in lines)
        total_credit = sum(l.get('credit', 0) for l in lines)
        
        if abs(total_debit - total_credit) > 0.01:
            abort(400, message=f"Debits ({total_debit}) must equal credits ({total_credit}).")
        
        entry_number = self._generate_entry_number(tenant_id)
        
        entry = JournalEntry(
            tenant_id=tenant_id, # type: ignore
            entry_number=entry_number, # type: ignore
            date=data.get('date', datetime.date.today()), # type: ignore
            description=data['description'], # type: ignore
            reference=data.get('reference'), # type: ignore
            created_by=get_jwt_identity() # type: ignore
        )
        db.session.add(entry)
        db.session.flush()
        
        for line_data in lines:
            line = JournalEntryLine(
                tenant_id=tenant_id, # type: ignore
                entry_id=entry.id, # type: ignore
                account_id=line_data['account_id'], # type: ignore
                debit=line_data.get('debit', 0), # type: ignore
                credit=line_data.get('credit', 0), # type: ignore
                description=line_data.get('description') # type: ignore
            )
            db.session.add(line)
            
            account = Account.query.filter_by(id=line_data['account_id'], tenant_id=tenant_id).first()
            if account:
                account.balance += line_data.get('debit', 0) - line_data.get('credit', 0)
        
        db.session.commit()
        
        try:
            from backend.webhook_triggers import on_journal_entry_created
            on_journal_entry_created(entry)
        except Exception:
            pass
        
        return entry, 201
    
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
    @blp.response(200, JournalEntrySchema)
    def get(self, entry_id):
        """Get journal entry with lines."""
        tenant_id = TenantContext.get_tenant_id()
        if tenant_id is None:
            abort(403, message="Tenant context not found")
        entry = JournalEntry.query.filter_by(id=entry_id, tenant_id=tenant_id).first()
        if not entry:
            abort(404, message="Journal entry not found")
        return entry
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, JournalEntrySchema)
    def post(self, entry_id):
        """Post (validate and finalize) journal entry."""
        tenant_id = TenantContext.get_tenant_id()
        if tenant_id is None:
            abort(403, message="Tenant context not found")
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
    @blp.response(200, InvoiceSchema(many=True))
    def get(self):
        """List invoices."""
        tenant_id = TenantContext.get_tenant_id()
        if tenant_id is None:
            abort(403, message="Tenant context not found")
        
        invoice_type = request.args.get('type')
        status = request.args.get('status')
        
        query = Invoice.query.filter_by(tenant_id=tenant_id)
        if invoice_type:
            query = query.filter_by(invoice_type=invoice_type)
        if status:
            query = query.filter_by(status=status)
        
        return query.order_by(Invoice.date.desc()).all()
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(InvoiceSchema)
    @blp.response(201, InvoiceSchema)
    def post(self):
        """Create new invoice."""
        data = request.get_json()
        lines = data.pop('lines', [])
        
        tenant_id = TenantContext.get_tenant_id()
        if tenant_id is None:
            abort(403, message="Tenant context not found")
        
        invoice_number = self._generate_invoice_number(tenant_id, data['invoice_type'])
        
        invoice = Invoice(
            tenant_id=tenant_id, # type: ignore
            invoice_number=invoice_number, # type: ignore
            invoice_type=data['invoice_type'], # type: ignore
            party_id=data['party_id'], # type: ignore
            date=data.get('date', datetime.date.today()), # type: ignore
            due_date=data.get('due_date'), # type: ignore
            description=data.get('description') # type: ignore
        )
        
        subtotal = 0
        for line_data in lines:
            line = InvoiceLine(
                tenant_id=tenant_id, # type: ignore
                product_id=line_data.get('product_id'), # type: ignore
                description=line_data.get('description'), # type: ignore
                quantity=line_data.get('quantity', 1), # type: ignore
                unit_price=line_data.get('unit_price', 0), # type: ignore
                discount_percent=line_data.get('discount_percent', 0), # type: ignore
                tax_percent=line_data.get('tax_percent', 0) # type: ignore
            )
            line.calculate()
            invoice.lines.append(line)
            subtotal += line.amount
        
        invoice.subtotal = subtotal
        invoice.tax_amount = sum(l.amount - (l.amount / (1 + l.tax_percent/100)) for l in invoice.lines if l.tax_percent > 0) # type: ignore
        invoice.total = invoice.subtotal + invoice.tax_amount
        
        db.session.add(invoice)
        db.session.commit()
        
        try:
            from backend.webhook_triggers import on_invoice_created
            on_invoice_created(invoice)
        except Exception:
            pass
        
        return invoice, 201
    
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
    @blp.response(200, InvoiceSchema)
    def get(self, invoice_id):
        """Get invoice with lines."""
        tenant_id = TenantContext.get_tenant_id()
        if tenant_id is None:
            abort(403, message="Tenant context not found")
        invoice = Invoice.query.filter_by(id=invoice_id, tenant_id=tenant_id).first()
        if not invoice:
            abort(404, message="Invoice not found")
        return invoice
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, InvoiceSchema)
    def post(self, invoice_id):
        """Send/Confirm invoice."""
        tenant_id = TenantContext.get_tenant_id()
        if tenant_id is None:
            abort(403, message="Tenant context not found")
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
    @blp.response(200, fields.Dict())
    def get(self):
        """Generate trial balance report."""
        tenant_id = TenantContext.get_tenant_id()
        if tenant_id is None:
            abort(403, message="Tenant context not found")
        
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
