"""
Tests for multi-tenant isolation.
"""
import pytest
from backend.entities.soggetto import Soggetto
from backend.models import Product, SalesOrder, User
from backend.core.models import Tenant


class TestTenantIsolation:
    """Test cases for tenant data isolation."""
    
    def test_users_isolated_by_tenant(self, app, db, session, tenant, tenant2):
        """Test users are isolated by tenant."""
        with app.app_context():
            # Create users in different tenants
            user1 = User(
                tenant_id=tenant.id,
                email='user1@test.com',
                role='user'
            )
            user1.set_password('password')
            session.add(user1)
            
            user2 = User(
                tenant_id=tenant2.id,
                email='user2@test.com',
                role='user'
            )
            user2.set_password('password')
            session.add(user2)
            session.commit()
            
            # Each tenant should only see their users
            users_tenant1 = User.query.filter_by(tenant_id=tenant.id).all()
            users_tenant2 = User.query.filter_by(tenant_id=tenant2.id).all()
            
            assert len(users_tenant1) == 1
            assert len(users_tenant2) == 1
            assert users_tenant1[0].email == 'user1@test.com'
            assert users_tenant2[0].email == 'user2@test.com'
    
    def test_parties_isolated_by_tenant(self, app, db, session, tenant, tenant2):
        """Test parties are isolated by tenant."""
        with app.app_context():
            # Create parties in different tenants
            party1 = Soggetto(
                tenant_id=tenant.id,
                nome='Customer One',
                tipo_soggetto='persona_fisica',
                email_principale='customer1@test.com'
            )
            session.add(party1)
            
            party2 = Soggetto(
                tenant_id=tenant2.id,
                nome='Customer Two',
                tipo_soggetto='persona_fisica',
                email_principale='customer2@test.com'
            )
            session.commit()
            
            # Each tenant should only see their parties
            parties_tenant1 = Soggetto.query.filter_by(tenant_id=tenant.id).all()
            parties_tenant2 = Soggetto.query.filter_by(tenant_id=tenant2.id).all()
            
            assert len(parties_tenant1) == 1
            assert len(parties_tenant2) == 1
            assert parties_tenant1[0].nome == 'Customer One'
            assert parties_tenant2[0].nome == 'Customer Two'
    
    def test_products_isolated_by_tenant(self, app, db, session, tenant, tenant2):
        """Test products are isolated by tenant."""
        with app.app_context():
            # Create products in different tenants
            product1 = Product(
                tenant_id=tenant.id,
                name='Product One',
                code='P1',
                unit_price=100.00
            )
            session.add(product1)
            
            product2 = Product(
                tenant_id=tenant2.id,
                name='Product Two',
                code='P2',
                unit_price=200.00
            )
            session.add(product2)
            session.commit()
            
            # Each tenant should only see their products
            products_tenant1 = Product.query.filter_by(tenant_id=tenant.id).all()
            products_tenant2 = Product.query.filter_by(tenant_id=tenant2.id).all()
            
            assert len(products_tenant1) == 1
            assert len(products_tenant2) == 1
            assert products_tenant1[0].name == 'Product One'
            assert products_tenant2[0].name == 'Product Two'
    
    def test_sales_orders_isolated_by_tenant(self, app, db, session, tenant, tenant2, party, product):
        """Test sales orders are isolated by tenant."""
        with app.app_context():
            # Create parties for tenant2
            party2 = Soggetto(
                tenant_id=tenant2.id,
                nome='Customer Two',
                tipo_soggetto='persona_fisica'
            )
            session.add(party2)
            session.flush()
            
            product2 = Product(
                tenant_id=tenant2.id,
                name='Product Two',
                code='P2'
            )
            session.add(product2)
            session.flush()
            
            # Create orders in different tenants
            order1 = SalesOrder(
                tenant_id=tenant.id,
                number='ORD-001',
                customer_id=party.id,
                status='draft'
            )
            session.add(order1)
            
            order2 = SalesOrder(
                tenant_id=tenant2.id,
                number='ORD-002',
                customer_id=party2.id,
                status='draft'
            )
            session.add(order2)
            session.commit()
            
            # Each tenant should only see their orders
            orders_tenant1 = SalesOrder.query.filter_by(tenant_id=tenant.id).all()
            orders_tenant2 = SalesOrder.query.filter_by(tenant_id=tenant2.id).all()
            
            assert len(orders_tenant1) == 1
            assert len(orders_tenant2) == 1
            assert orders_tenant1[0].number == 'ORD-001'
            assert orders_tenant2[0].number == 'ORD-002'
    
    def test_tenant_cannot_access_other_tenant_data(self, app, db, session, tenant, tenant2):
        """Test tenant2 cannot access tenant1's data."""
        with app.app_context():
            # Create data for tenant1
            user1 = User(
                tenant_id=tenant.id,
                email='secret@test.com',
                role='user'
            )
            user1.set_password('password')
            session.add(user1)
            
            party1 = Soggetto(
                tenant_id=tenant.id,
                nome='Secret Customer',
                tipo_soggetto='persona_fisica'
            )
            session.add(party1)
            session.commit()
            
            # Query from tenant2 perspective
            users = User.query.filter_by(tenant_id=tenant2.id).all()
            parties = Soggetto.query.filter_by(tenant_id=tenant2.id).all()
            
            # Should not find tenant1's data
            assert len(users) == 0
            assert len(parties) == 0
    
    def test_tenant_model_relationships(self, app, db, session, tenant):
        """Test tenant relationships are correctly set up."""
        with app.app_context():
            # Create user for tenant
            user = User(
                tenant_id=tenant.id,
                email='test@test.com',
                role='user'
            )
            user.set_password('password')
            session.add(user)
            session.commit()
            
            # Check relationship
            assert tenant.users.count() == 1
            assert tenant.users.first().email == 'test@test.com'
    
    def test_tenant_can_add_users_within_limit(self, app, db, session, tenant):
        """Test tenant user limit functionality."""
        with app.app_context():
            # Default max_users is 3
            assert tenant.can_add_user() is True
            
            # Add users up to limit
            for i in range(2):
                user = User(
                    tenant_id=tenant.id,
                    email=f'user{i}@test.com',
                    role='user'
                )
                user.set_password('password')
                session.add(user)
            session.commit()
            
            assert tenant.users.count() == 2
            assert tenant.can_add_user() is True
            
            # Add one more to reach limit
            user3 = User(
                tenant_id=tenant.id,
                email='user3@test.com',
                role='user'
            )
            user3.set_password('password')
            session.add(user3)
            session.commit()
            
            assert tenant.users.count() == 3
            assert tenant.can_add_user() is False
    
    def test_tenant_plan_expiration(self, app, db, session, tenant):
        """Test tenant plan expiration check."""
        from datetime import datetime, timedelta
        
        with app.app_context():
            # No expiration date
            assert tenant.is_plan_expired is False
            
            # Set expired date
            tenant.plan_expires_at = datetime.utcnow() - timedelta(days=1)
            assert tenant.is_plan_expired is True
            
            # Set future date
            tenant.plan_expires_at = datetime.utcnow() + timedelta(days=30)
            assert tenant.is_plan_expired is False


class TestAuditLogIsolation:
    """Test audit logs are isolated by tenant."""
    
    def test_audit_logs_isolated_by_tenant(self, app, db, session, tenant, tenant2):
        """Test audit logs are isolated by tenant."""
        from backend.core.models.audit import AuditLog
        
        with app.app_context():
            # Create users for audit
            user1 = User(
                tenant_id=tenant.id,
                email='user1@test.com',
                role='user'
            )
            user1.set_password('password')
            session.add(user1)
            
            user2 = User(
                tenant_id=tenant2.id,
                email='user2@test.com',
                role='user'
            )
            user2.set_password('password')
            session.add(user2)
            session.flush()
            
            # Create audit logs
            AuditLog.log_create(
                user_id=user1.id,
                tenant_id=tenant.id,
                resource_type='user',
                resource_id=user1.id,
                new_values={'action': 'create'}
            )
            
            AuditLog.log_create(
                user_id=user2.id,
                tenant_id=tenant2.id,
                resource_type='user',
                resource_id=user2.id,
                new_values={'action': 'create'}
            )
            session.commit()
            
            # Each tenant should only see their audit logs
            logs_tenant1 = AuditLog.query.filter_by(tenant_id=tenant.id).all()
            logs_tenant2 = AuditLog.query.filter_by(tenant_id=tenant2.id).all()
            
            assert len(logs_tenant1) == 1
            assert len(logs_tenant2) == 1
    
    def test_audit_log_login_tracking(self, app, db, session, admin_user):
        """Test login audit logging."""
        from backend.core.models.audit import AuditLog
        
        with app.app_context():
            # Log successful login
            AuditLog.log_login(
                user_id=admin_user.id,
                tenant_id=admin_user.tenant_id,
                success=True
            )
            
            # Log failed login
            AuditLog.log_login(
                user_id=admin_user.id,
                tenant_id=admin_user.tenant_id,
                success=False,
                error_message="Wrong password"
            )
            session.commit()
            
            # Verify logs created
            logs = AuditLog.query.filter_by(
                tenant_id=admin_user.tenant_id,
                action=AuditLog.ACTION_LOGIN
            ).all()
            
            assert len(logs) == 2
            assert logs[0].status == 'success'
            assert logs[1].status == 'failure'
