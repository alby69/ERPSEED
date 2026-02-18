"""
Tests for Accounting plugin with multi-tenant isolation.
"""
import pytest
from backend.plugins.accounting.models import (
    ChartOfAccounts, Account, JournalEntry, JournalEntryLine, 
    Invoice, InvoiceLine
)


class TestChartOfAccountsIsolation:
    """Test Chart of Accounts isolation between tenants."""
    
    def test_create_coa(self, app, db, session, tenant):
        """Test creating Chart of Accounts."""
        with app.app_context():
            coa = ChartOfAccounts(
                tenant_id=tenant.id,
                code='1000',
                name='Cash',
                type='asset'
            )
            session.add(coa)
            session.commit()
            
            assert coa.id is not None
            assert coa.code == '1000'
            assert coa.type == 'asset'
            assert coa.tenant_id == tenant.id
    
    def test_coa_isolated_between_tenants(self, app, db, session, tenant, tenant2):
        """Test COA is isolated between tenants."""
        with app.app_context():
            # Create COA for tenant 1
            coa1 = ChartOfAccounts(
                tenant_id=tenant.id,
                code='1000',
                name='Cash',
                type='asset'
            )
            session.add(coa1)
            
            # Create COA for tenant 2
            coa2 = ChartOfAccounts(
                tenant_id=tenant2.id,
                code='1000',  # Same code, different tenant
                name='Different Cash',
                type='asset'
            )
            session.add(coa2)
            session.commit()
            
            # Each tenant should only see their COA
            coas1 = ChartOfAccounts.query.filter_by(tenant_id=tenant.id).all()
            coas2 = ChartOfAccounts.query.filter_by(tenant_id=tenant2.id).all()
            
            assert len(coas1) == 1
            assert len(coas2) == 1
            assert coas1[0].name == 'Cash'
            assert coas2[0].name == 'Different Cash'


class TestAccountIsolation:
    """Test Account isolation between tenants."""
    
    def test_create_account(self, app, db, session, tenant):
        """Test creating an Account."""
        with app.app_context():
            # First create COA
            coa = ChartOfAccounts(
                tenant_id=tenant.id,
                code='1000',
                name='Cash',
                type='asset'
            )
            session.add(coa)
            session.flush()
            
            account = Account(
                tenant_id=tenant.id,
                coa_id=coa.id,
                code='1000-001',
                name='Petty Cash',
                balance=0.0
            )
            session.add(account)
            session.commit()
            
            assert account.id is not None
            assert account.code == '1000-001'
            assert account.tenant_id == tenant.id


class TestJournalEntryIsolation:
    """Test Journal Entry isolation between tenants."""
    
    def test_create_journal_entry(self, app, db, session, tenant):
        """Test creating a Journal Entry."""
        with app.app_context():
            # Create COA
            coa1 = ChartOfAccounts(
                tenant_id=tenant.id,
                code='1000',
                name='Cash',
                type='asset'
            )
            coa2 = ChartOfAccounts(
                tenant_id=tenant.id,
                code='4000',
                name='Revenue',
                type='revenue'
            )
            session.add(coa1)
            session.add(coa2)
            session.flush()
            
            # Create accounts
            account1 = Account(
                tenant_id=tenant.id,
                coa_id=coa1.id,
                code='1000-001',
                name='Petty Cash'
            )
            account2 = Account(
                tenant_id=tenant.id,
                coa_id=coa2.id,
                code='4000-001',
                name='Sales Revenue'
            )
            session.add(account1)
            session.add(account2)
            session.flush()
            
            # Create journal entry
            entry = JournalEntry(
                tenant_id=tenant.id,
                entry_number='JE-2026-00001',
                description='Test entry',
                status='draft'
            )
            session.add(entry)
            session.flush()
            
            # Add lines
            line1 = JournalEntryLine(
                tenant_id=tenant.id,
                entry_id=entry.id,
                account_id=account1.id,
                debit=1000.00,
                credit=0.0
            )
            line2 = JournalEntryLine(
                tenant_id=tenant.id,
                entry_id=entry.id,
                account_id=account2.id,
                debit=0.0,
                credit=1000.00
            )
            session.add(line1)
            session.add(line2)
            session.commit()
            
            assert entry.id is not None
            assert entry.is_balanced is True
            assert entry.total_debit == 1000.00
            assert entry.total_credit == 1000.00
    
    def test_journal_entry_is_balanced(self, app, db, session, tenant):
        """Test journal entry balanced check."""
        with app.app_context():
            coa1 = ChartOfAccounts(tenant_id=tenant.id, code='1000', name='Cash', type='asset')
            coa2 = ChartOfAccounts(tenant_id=tenant.id, code='4000', name='Revenue', type='revenue')
            session.add(coa1)
            session.add(coa2)
            session.flush()
            
            acc1 = Account(tenant_id=tenant.id, coa_id=coa1.id, code='1000-01', name='Cash')
            acc2 = Account(tenant_id=tenant.id, coa_id=coa2.id, code='4000-01', name='Rev')
            session.add(acc1)
            session.add(acc2)
            session.flush()
            
            entry = JournalEntry(
                tenant_id=tenant.id,
                entry_number='JE-2026-00002',
                description='Balanced entry',
                status='draft'
            )
            session.add(entry)
            session.flush()
            
            line1 = JournalEntryLine(tenant_id=tenant.id, entry_id=entry.id, account_id=acc1.id, debit=500, credit=0)
            line2 = JournalEntryLine(tenant_id=tenant.id, entry_id=entry.id, account_id=acc2.id, debit=0, credit=500)
            session.add(line1)
            session.add(line2)
            session.commit()
            
            assert entry.is_balanced is True
    
    def test_journal_entry_unbalanced_fails(self, app, db, session, tenant):
        """Test unbalanced journal entry is detected."""
        with app.app_context():
            coa1 = ChartOfAccounts(tenant_id=tenant.id, code='1000', name='Cash', type='asset')
            coa2 = ChartOfAccounts(tenant_id=tenant.id, code='4000', name='Revenue', type='revenue')
            session.add(coa1)
            session.add(coa2)
            session.flush()
            
            acc1 = Account(tenant_id=tenant.id, coa_id=coa1.id, code='1000-01', name='Cash')
            acc2 = Account(tenant_id=tenant.id, coa_id=coa2.id, code='4000-01', name='Rev')
            session.add(acc1)
            session.add(acc2)
            session.flush()
            
            entry = JournalEntry(
                tenant_id=tenant.id,
                entry_number='JE-2026-00003',
                description='Unbalanced',
                status='draft'
            )
            session.add(entry)
            session.flush()
            
            line1 = JournalEntryLine(tenant_id=tenant.id, entry_id=entry.id, account_id=acc1.id, debit=500, credit=0)
            line2 = JournalEntryLine(tenant_id=tenant.id, entry_id=entry.id, account_id=acc2.id, debit=0, credit=400)  # Not balanced
            session.add(line1)
            session.add(line2)
            session.commit()
            
            assert entry.is_balanced is False


class TestInvoiceIsolation:
    """Test Invoice isolation between tenants."""
    
    def test_create_invoice(self, app, db, session, tenant, party):
        """Test creating an Invoice."""
        with app.app_context():
            invoice = Invoice(
                tenant_id=tenant.id,
                invoice_number='AR-202602-00001',
                invoice_type='AR',
                party_id=party.id,
                status='draft',
                subtotal=1000.00,
                tax_amount=220.00,
                total=1220.00
            )
            session.add(invoice)
            session.commit()
            
            assert invoice.id is not None
            assert invoice.invoice_number == 'AR-202602-00001'
            assert invoice.invoice_type == 'AR'
            assert invoice.total == 1220.00
    
    def test_invoice_isolated_between_tenants(self, app, db, session, tenant, tenant2, party, party2):
        """Test invoices are isolated between tenants."""
        with app.app_context():
            # Create invoice for tenant 1
            inv1 = Invoice(
                tenant_id=tenant.id,
                invoice_number='AR-001',
                invoice_type='AR',
                party_id=party.id,
                status='draft'
            )
            session.add(inv1)
            
            # Create invoice for tenant 2
            inv2 = Invoice(
                tenant_id=tenant2.id,
                invoice_number='AR-002',
                invoice_type='AR',
                party_id=party2.id,
                status='draft'
            )
            session.add(inv2)
            session.commit()
            
            # Each tenant should only see their invoices
            invs1 = Invoice.query.filter_by(tenant_id=tenant.id).all()
            invs2 = Invoice.query.filter_by(tenant_id=tenant2.id).all()
            
            assert len(invs1) == 1
            assert len(invs2) == 1
    
    def test_invoice_status_flow(self, app, db, session, tenant, party):
        """Test invoice status flow."""
        with app.app_context():
            invoice = Invoice(
                tenant_id=tenant.id,
                invoice_number='AR-003',
                invoice_type='AR',
                party_id=party.id,
                status='draft'
            )
            session.add(invoice)
            session.commit()
            
            assert invoice.status == 'draft'
            
            invoice.status = 'sent'
            session.commit()
            assert invoice.status == 'sent'
            
            invoice.status = 'paid'
            session.commit()
            assert invoice.status == 'paid'
