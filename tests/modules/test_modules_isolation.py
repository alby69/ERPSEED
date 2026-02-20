"""
Tests for Parties, Products, and Sales modules with multi-tenant isolation.
"""
import pytest
from backend.entities.soggetto import Soggetto
from backend.models import Product, SalesOrder


class TestPartiesIsolation:
    """Test party isolation between tenants."""
    
    def test_create_party_in_tenant(self, app, db, session, tenant):
        """Test creating a party."""
        with app.app_context():
            party = Soggetto(
                tenant_id=tenant.id,
                nome='Test Customer',
                tipo_soggetto='persona_fisica',
                email_principale='test@test.com'
            )
            session.add(party)
            session.commit()
            
            assert party.id is not None
            assert party.nome == 'Test Customer'
            assert party.tenant_id == tenant.id
    
    def test_parties_isolated_between_tenants(self, app, db, session, tenant, tenant2):
        """Test parties are isolated between tenants."""
        with app.app_context():
            # Create party for tenant 1
            party1 = Soggetto(
                tenant_id=tenant.id,
                nome='Customer One',
                tipo_soggetto='persona_fisica'
            )
            session.add(party1)
            
            # Create party for tenant 2
            party2 = Soggetto(
                tenant_id=tenant2.id,
                nome='Customer Two',
                tipo_soggetto='persona_fisica'
            )
            session.add(party2)
            session.commit()
            
            # Each tenant should only see their parties
            parties1 = Soggetto.query.filter_by(tenant_id=tenant.id).all()
            parties2 = Soggetto.query.filter_by(tenant_id=tenant2.id).all()
            
            assert len(parties1) == 1
            assert len(parties2) == 1
            assert parties1[0].nome == 'Customer One'
            assert parties2[0].nome == 'Customer Two'
    
    def test_party_unique_constraint_per_tenant(self, app, db, session, tenant):
        """Test same email can exist in different tenants."""
        with app.app_context():
            # Create party in tenant 1
            party1 = Soggetto(
                tenant_id=tenant.id,
                nome='Customer One',
                tipo_soggetto='persona_fisica',
                email_principale='same@test.com'
            )
            session.add(party1)
            session.commit()
            
            # Should be able to create another with same email in different tenant
            from backend.core.models import Tenant
            tenant2 = Tenant(
                name='Tenant 2',
                slug='tenant2-' + str(id(session)),
                email='admin2@test.com'
            )
            session.add(tenant2)
            session.flush()
            
            party2 = Soggetto(
                tenant_id=tenant2.id,
                nome='Customer Two',
                tipo_soggetto='persona_fisica',
                email_principale='same@test.com'  # Same email, different tenant
            )
            session.add(party2)
            session.commit()  # Should not raise


class TestProductsIsolation:
    """Test product isolation between tenants."""
    
    def test_create_product_in_tenant(self, app, db, session, tenant):
        """Test creating a product."""
        with app.app_context():
            product = Product(
                tenant_id=tenant.id,
                name='Test Product',
                code='TEST001',
                unit_price=100.00
            )
            session.add(product)
            session.commit()
            
            assert product.id is not None
            assert product.name == 'Test Product'
            assert product.tenant_id == tenant.id
    
    def test_products_isolated_between_tenants(self, app, db, session, tenant, tenant2):
        """Test products are isolated between tenants."""
        with app.app_context():
            # Create product for tenant 1
            product1 = Product(
                tenant_id=tenant.id,
                name='Product One',
                code='PROD1',
                unit_price=100.00
            )
            session.add(product1)
            
            # Create product for tenant 2
            product2 = Product(
                tenant_id=tenant2.id,
                name='Product Two',
                code='PROD2',
                unit_price=200.00
            )
            session.add(product2)
            session.commit()
            
            # Each tenant should only see their products
            products1 = Product.query.filter_by(tenant_id=tenant.id).all()
            products2 = Product.query.filter_by(tenant_id=tenant2.id).all()
            
            assert len(products1) == 1
            assert len(products2) == 1
            assert products1[0].name == 'Product One'
            assert products2[0].name == 'Product Two'
    
    def test_product_with_extended_fields(self, app, db, session, tenant):
        """Test product with all extended fields."""
        with app.app_context():
            product = Product(
                tenant_id=tenant.id,
                name='Extended Product',
                code='EXT001',
                unit_price=150.00,
                category='Electronics',
                sku='SKU001',
                barcode='123456789',
                track_inventory=True,
                current_stock=100,
                reorder_level=10
            )
            session.add(product)
            session.commit()
            
            assert product.category == 'Electronics'
            assert product.sku == 'SKU001'
            assert product.barcode == '123456789'
            assert product.track_inventory is True
            assert product.current_stock == 100
            assert product.reorder_level == 10


class TestSalesOrdersIsolation:
    """Test sales order isolation between tenants."""
    
    def test_create_sales_order(self, app, db, session, tenant, party, product):
        """Test creating a sales order."""
        with app.app_context():
            order = SalesOrder(
                tenant_id=tenant.id,
                number='SO-001',
                customer_id=party.id,
                status='draft',
                total_amount=500.00
            )
            session.add(order)
            session.commit()
            
            assert order.id is not None
            assert order.number == 'SO-001'
            assert order.tenant_id == tenant.id
    
    def test_sales_orders_isolated_between_tenants(self, app, db, session, tenant, tenant2, party, party2):
        """Test sales orders are isolated between tenants."""
        with app.app_context():
            # Create order for tenant 1
            order1 = SalesOrder(
                tenant_id=tenant.id,
                number='SO-001',
                customer_id=party.id,
                status='draft'
            )
            session.add(order1)
            
            # Create order for tenant 2
            order2 = SalesOrder(
                tenant_id=tenant2.id,
                number='SO-002',
                customer_id=party2.id,
                status='draft'
            )
            session.add(order2)
            session.commit()
            
            # Each tenant should only see their orders
            orders1 = SalesOrder.query.filter_by(tenant_id=tenant.id).all()
            orders2 = SalesOrder.query.filter_by(tenant_id=tenant2.id).all()
            
            assert len(orders1) == 1
            assert len(orders2) == 1
            assert orders1[0].number == 'SO-001'
            assert orders2[0].number == 'SO-002'
    
    def test_sales_order_status_flow(self, app, db, session, tenant, party):
        """Test sales order status flow."""
        with app.app_context():
            order = SalesOrder(
                tenant_id=tenant.id,
                number='SO-003',
                customer_id=party.id,
                status='draft'
            )
            session.add(order)
            session.commit()
            
            assert order.status == 'draft'
            
            order.status = 'confirmed'
            session.commit()
            
            session.refresh(order)
            assert order.status == 'confirmed'
            
            order.status = 'completed'
            session.commit()
            
            session.refresh(order)
            assert order.status == 'completed'
