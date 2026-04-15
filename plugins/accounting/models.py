"""
Accounting Plugin Models.

Provides double-entry accounting functionality:
- Chart of Accounts
- General Journal
- Invoices (Accounts Receivable/Payable)
"""
from datetime import datetime, date
from extensions import db


class ChartOfAccounts(db.Model):
    """Chart of Accounts - master list of all accounts."""
    __tablename__ = 'coa'

    # Multi-tenant support
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), nullable=False, index=True)
    name = db.Column(db.String(150), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # asset, liability, equity, revenue, expense
    parent_id = db.Column(db.Integer, db.ForeignKey('coa.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    allow_transaction = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    parent = db.relationship('ChartOfAccounts', remote_side=[id], backref='children')
    accounts = db.relationship('Account', back_populates='coa', lazy='dynamic', foreign_keys='Account.coa_id')
    tenant = db.relationship('Tenant', backref=db.backref('coa_accounts', lazy='dynamic'))

    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'code', name='uix_tenant_coa_code'),
        db.Index('ix_coa_tenant_type', 'tenant_id', 'type'),
    )

    def __repr__(self):
        return f'<COA {self.code}: {self.name}>'


class Account(db.Model):
    """Individual account within the Chart of Accounts."""
    __tablename__ = 'accounts'

    # Multi-tenant support
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)

    id = db.Column(db.Integer, primary_key=True)
    coa_id = db.Column(db.Integer, db.ForeignKey('coa.id'), nullable=False)
    code = db.Column(db.String(20), nullable=False, index=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    balance = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    coa = db.relationship('ChartOfAccounts', back_populates='accounts', foreign_keys=[coa_id])
    journal_lines = db.relationship('JournalEntryLine', back_populates='account', lazy='dynamic')
    tenant = db.relationship('Tenant', backref=db.backref('accounts', lazy='dynamic'))

    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'code', name='uix_tenant_account_code'),
    )

    def __repr__(self):
        return f'<Account {self.code}: {self.name}>'


class JournalEntry(db.Model):
    """General Journal Entry - records all financial transactions."""
    __tablename__ = 'journal_entries'

    # Multi-tenant support
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)

    id = db.Column(db.Integer, primary_key=True)
    entry_number = db.Column(db.String(50), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, default=date.today)
    description = db.Column(db.String(255), nullable=False)
    reference = db.Column(db.String(100))
    status = db.Column(db.String(20), default='draft')  # draft, posted, cancelled
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    lines = db.relationship('JournalEntryLine', back_populates='entry', cascade='all, delete-orphan', lazy='dynamic')
    creator = db.relationship('User')
    tenant = db.relationship('Tenant', backref=db.backref('journal_entries', lazy='dynamic'))

    __table_args__ = (
        db.Index('ix_journal_tenant_number', 'tenant_id', 'entry_number'),
        db.Index('ix_journal_tenant_date', 'tenant_id', 'date'),
    )

    def __repr__(self):
        return f'<JournalEntry {self.entry_number}>'

    @property
    def total_debit(self):
        """Calculate total debit amount."""
        return sum(line.debit for line in self.lines)

    @property
    def total_credit(self):
        """Calculate total credit amount."""
        return sum(line.credit for line in self.lines)

    @property
    def is_balanced(self):
        """Check if entry is balanced (debits = credits)."""
        return abs(self.total_debit - self.total_credit) < 0.01


class JournalEntryLine(db.Model):
    """Individual line in a Journal Entry."""
    __tablename__ = 'journal_entry_lines'

    # Multi-tenant support
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)

    id = db.Column(db.Integer, primary_key=True)
    entry_id = db.Column(db.Integer, db.ForeignKey('journal_entries.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    debit = db.Column(db.Float, default=0.0)
    credit = db.Column(db.Float, default=0.0)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    entry = db.relationship('JournalEntry', back_populates='lines')
    account = db.relationship('Account', back_populates='journal_lines')
    tenant = db.relationship('Tenant', backref=db.backref('journal_lines', lazy='dynamic'))

    def __repr__(self):
        return f'<JournalLine {self.account_id}: Dr {self.debit} / Cr {self.credit}>'


class Invoice(db.Model):
    """Invoice - Accounts Receivable or Payable."""
    __tablename__ = 'invoices'

    # Multi-tenant support
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)

    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), nullable=False, index=True)
    invoice_type = db.Column(db.String(10), nullable=False)  # AR (receivable), AP (payable)
    party_id = db.Column(db.Integer, db.ForeignKey('soggetti.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    due_date = db.Column(db.Date)
    description = db.Column(db.String(255))
    subtotal = db.Column(db.Float, default=0.0)
    tax_amount = db.Column(db.Float, default=0.0)
    total = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='draft')  # draft, sent, paid, cancelled
    journal_entry_id = db.Column(db.Integer, db.ForeignKey('journal_entries.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    party = db.relationship('Soggetto')
    lines = db.relationship('InvoiceLine', back_populates='invoice', cascade='all, delete-orphan')
    journal_entry = db.relationship('JournalEntry')
    tenant = db.relationship('Tenant', backref=db.backref('invoices', lazy='dynamic'))

    __table_args__ = (
        db.Index('ix_invoice_tenant_number', 'tenant_id', 'invoice_number'),
    )

    def __repr__(self):
        return f'<Invoice {self.invoice_number}>'


class InvoiceLine(db.Model):
    """Individual line in an Invoice."""
    __tablename__ = 'invoice_lines'

    # Multi-tenant support
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)

    id = db.Column(db.Integer, primary_key=True)
    invoiceId = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    description = db.Column(db.String(255))
    quantity = db.Column(db.Float, nullable=False, default=1.0)
    unit_price = db.Column(db.Float, nullable=False, default=0.0)
    discount_percent = db.Column(db.Float, default=0.0)
    tax_percent = db.Column(db.Float, default=0.0)
    amount = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    invoice = db.relationship('Invoice', back_populates='lines')
    product = db.relationship('Product')
    tenant = db.relationship('Tenant', backref=db.backref('invoice_lines', lazy='dynamic'))

    def calculate(self):
        """Calculate line amount."""
        subtotal = self.quantity * self.unit_price
        discount = subtotal * (self.discount_percent / 100)
        taxable = subtotal - discount
        tax = taxable * (self.tax_percent / 100)
        self.amount = taxable + tax
        return self.amount
