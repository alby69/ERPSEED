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

from .models import ChartOfAccounts, Account, JournalEntry, JournalEntryLine, Invoice, InvoiceLine

blp = Blueprint("accounting", __name__, url_prefix="/accounting", description="Accounting Operations")


@blp.route("/coa")
class COAList(MethodView):
    """Chart of Accounts endpoints."""
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        """List all accounts in Chart of Accounts."""
        query = ChartOfAccounts.query.filter_by(is_active=True).order_by(ChartOfAccounts.code)
        return query.all()
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        """Create new account in Chart of Accounts."""
        data = request.get_json()
        
        existing = ChartOfAccounts.query.filter_by(code=data['code']).first()
        if existing:
            abort(409, message=f"Account code '{data['code']}' already exists.")
        
        coa = ChartOfAccounts(
            code=data['code'],
            name=data['name'],
            type=data['type'],
            parent_id=data.get('parent_id'),
            allow_transaction=data.get('allow_transaction', True)
        )
        
        from backend.extensions import db
        db.session.add(coa)
        db.session.commit()
        
        return coa, 201


@blp.route("/coa/<int:coa_id>")
class COAResource(MethodView):
    """Single Chart of Accounts entry."""
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, coa_id):
        """Get account by ID."""
        coa = ChartOfAccounts.query.get_or_404(coa_id)
        return coa
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def put(self, coa_id):
        """Update account."""
        data = request.get_json()
        coa = ChartOfAccounts.query.get_or_404(coa_id)
        
        for key, value in data.items():
            if hasattr(coa, key):
                setattr(coa, key, value)
        
        from backend.extensions import db
        db.session.commit()
        return coa
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def delete(self, coa_id):
        """Deactivate account (soft delete)."""
        coa = ChartOfAccounts.query.get_or_404(coa_id)
        coa.is_active = False
        
        from backend.extensions import db
        db.session.commit()
        return '', 204


@blp.route("/accounts")
class AccountList(MethodView):
    """Account endpoints."""
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        """List all active accounts."""
        query = Account.query.filter_by(is_active=True).order_by(Account.code)
        return query.all()
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        """Create new account."""
        data = request.get_json()
        
        existing = Account.query.filter_by(code=data['code']).first()
        if existing:
            abort(409, message=f"Account code '{data['code']}' already exists.")
        
        account = Account(
            coa_id=data['coa_id'],
            code=data['code'],
            name=data['name'],
            description=data.get('description')
        )
        
        from backend.extensions import db
        db.session.add(account)
        db.session.commit()
        
        return account, 201


@blp.route("/journal")
class JournalEntryList(MethodView):
    """Journal Entry endpoints."""
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        """List journal entries."""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        query = JournalEntry.query.order_by(JournalEntry.date.desc(), JournalEntry.entry_number.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return pagination.items
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        """Create journal entry with double-entry validation."""
        data = request.get_json()
        lines = data.pop('lines', [])
        
        from backend.extensions import db
        
        total_debit = sum(l.get('debit', 0) for l in lines)
        total_credit = sum(l.get('credit', 0) for l in lines)
        
        if abs(total_debit - total_credit) > 0.01:
            abort(400, message=f"Debits ({total_debit}) must equal credits ({total_credit}).")
        
        entry_number = self._generate_entry_number()
        
        entry = JournalEntry(
            entry_number=entry_number,
            date=data.get('date', datetime.date.today()),
            description=data['description'],
            reference=data.get('reference'),
            created_by=get_jwt_identity()
        )
        db.session.add(entry)
        db.session.flush()
        
        for line_data in lines:
            line = JournalEntryLine(
                entry_id=entry.id,
                account_id=line_data['account_id'],
                debit=line_data.get('debit', 0),
                credit=line_data.get('credit', 0),
                description=line_data.get('description')
            )
            db.session.add(line)
            
            account = Account.query.get(line_data['account_id'])
            if account:
                account.balance += line_data.get('debit', 0) - line_data.get('credit', 0)
        
        db.session.commit()
        
        try:
            from backend.webhook_triggers import on_journal_entry_created
            on_journal_entry_created(entry)
        except Exception:
            pass
        
        return entry, 201
    
    def _generate_entry_number(self):
        """Generate unique entry number."""
        today = datetime.date.today()
        year = today.year
        
        last_entry = JournalEntry.query.filter(
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
    def get(self, entry_id):
        """Get journal entry with lines."""
        entry = JournalEntry.query.get_or_404(entry_id)
        return entry
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self, entry_id):
        """Post (validate and finalize) journal entry."""
        entry = JournalEntry.query.get_or_404(entry_id)
        
        if entry.status != 'draft':
            abort(400, message="Only draft entries can be posted.")
        
        if not entry.is_balanced:
            abort(400, message="Entry must be balanced before posting.")
        
        entry.status = 'posted'
        
        from backend.extensions import db
        db.session.commit()
        
        return entry


@blp.route("/invoices")
class InvoiceList(MethodView):
    """Invoice endpoints."""
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        """List invoices."""
        invoice_type = request.args.get('type')
        status = request.args.get('status')
        
        query = Invoice.query
        if invoice_type:
            query = query.filter_by(invoice_type=invoice_type)
        if status:
            query = query.filter_by(status=status)
        
        return query.order_by(Invoice.date.desc()).all()
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        """Create new invoice."""
        data = request.get_json()
        lines = data.pop('lines', [])
        
        from backend.extensions import db
        
        invoice_number = self._generate_invoice_number(data['invoice_type'])
        
        invoice = Invoice(
            invoice_number=invoice_number,
            invoice_type=data['invoice_type'],
            party_id=data['party_id'],
            date=data.get('date', datetime.date.today()),
            due_date=data.get('due_date'),
            description=data.get('description')
        )
        
        subtotal = 0
        for line_data in lines:
            line = InvoiceLine(
                product_id=line_data.get('product_id'),
                description=line_data.get('description'),
                quantity=line_data.get('quantity', 1),
                unit_price=line_data.get('unit_price', 0),
                discount_percent=line_data.get('discount_percent', 0),
                tax_percent=line_data.get('tax_percent', 0)
            )
            line.calculate()
            invoice.lines.append(line)
            subtotal += line.amount
        
        invoice.subtotal = subtotal
        invoice.tax_amount = sum(l.amount - (l.amount / (1 + l.tax_percent/100)) for l in invoice.lines if l.tax_percent > 0)
        invoice.total = invoice.subtotal + invoice.tax_amount
        
        db.session.add(invoice)
        db.session.commit()
        
        try:
            from backend.webhook_triggers import on_invoice_created
            on_invoice_created(invoice)
        except Exception:
            pass
        
        return invoice, 201
    
    def _generate_invoice_number(self, invoice_type):
        """Generate unique invoice number."""
        prefix = 'AR' if invoice_type == 'AR' else 'AP'
        today = datetime.date.today()
        
        last_invoice = Invoice.query.filter(
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
    def get(self, invoice_id):
        """Get invoice with lines."""
        invoice = Invoice.query.get_or_404(invoice_id)
        return invoice
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self, invoice_id):
        """Send/Confirm invoice."""
        invoice = Invoice.query.get_or_404(invoice_id)
        
        if invoice.status != 'draft':
            abort(400, message="Only draft invoices can be sent.")
        
        invoice.status = 'sent'
        
        from backend.extensions import db
        db.session.commit()
        
        return invoice


@blp.route("/reports/trial-balance")
class TrialBalance(MethodView):
    """Trial Balance Report."""
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        """Generate trial balance report."""
        accounts = Account.query.filter_by(is_active=True).all()
        
        from backend.extensions import db
        
        result = []
        total_debit = 0
        total_credit = 0
        
        for account in accounts:
            balance = db.session.query(
                func.coalesce(func.sum(JournalEntryLine.debit), 0) - 
                func.coalesce(func.sum(JournalEntryLine.credit), 0)
            ).filter(JournalEntryLine.account_id == account.id).scalar()
            
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
