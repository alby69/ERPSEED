"""
Tests for Sales Read Model (CQRS PoC).

This test suite demonstrates the Read Model pattern in CQRS,
separating read operations from write operations.
"""
import pytest
import os
os.environ.setdefault('JWT_SECRET_KEY', 'test-secret-key-for-testing-purposes-only-12345')

from backend import create_app
from backend.extensions import db
from backend.models import SalesOrder, SalesOrderLine, Tenant, User
from datetime import date


class TestSalesReadModel:
    """Test cases for Sales Order Read Model."""
    
    @pytest.fixture
    def app(self):
        """Create test app with in-memory database."""
        app = create_app(db_url="sqlite:///:memory:")
        app.config["TESTING"] = True
        with app.app_context():
            db.create_all()
            yield app
            db.session.remove()
            db.drop_all()
    
    @pytest.fixture
    def tenant(self, app):
        """Create a test tenant."""
        with app.app_context():
            tenant = Tenant(name="Test Company", slug="test-co")
            db.session.add(tenant)
            db.session.commit()
            return tenant.id
    
    @pytest.fixture
    def sample_orders(self, app, tenant):
        """Create sample sales orders for testing."""
        with app.app_context():
            orders = []
            for i in range(3):
                order = SalesOrder(
                    tenant_id=tenant,
                    number=f"SO-2024-{i+1:03d}",
                    date=date.today(),
                    customer_id=1,
                    status="confirmed" if i == 0 else "draft",
                    total_amount=100.0 * (i + 1),
                    notes=f"Test order {i+1}"
                )
                db.session.add(order)
                db.session.flush()
                
                line = SalesOrderLine(
                    tenant_id=tenant,
                    order_id=order.id,
                    product_id=1,
                    description=f"Product {i+1}",
                    quantity=1,
                    unit_price=100.0 * (i + 1),
                    total_price=100.0 * (i + 1)
                )
                db.session.add(line)
                orders.append(order)
            
            db.session.commit()
            
            for order in orders:
                db.session.refresh(order)
            
            yield tenant
    
    def test_list_orders_basic(self, app, sample_orders):
        """Test basic listing of sales orders."""
        with app.app_context():
            from backend.application.sales.queries import (
                SalesOrderListQuery,
                SalesOrderListQueryHandler,
            )
            
            query = SalesOrderListQuery(tenant_id=sample_orders)
            handler = SalesOrderListQueryHandler()
            result = handler.handle(query)
            
            assert result.total == 3
            assert len(result.items) == 3
            assert result.page == 1
            assert result.has_next is False
    
    def test_list_orders_filter_by_status(self, app, sample_orders):
        """Test filtering orders by status."""
        with app.app_context():
            from backend.application.sales.queries import (
                SalesOrderListQuery,
                SalesOrderListQueryHandler,
            )
            
            query = SalesOrderListQuery(tenant_id=sample_orders, status="confirmed")
            handler = SalesOrderListQueryHandler()
            result = handler.handle(query)
            
            assert result.total == 1
            assert result.items[0].status == "confirmed"
    
    def test_list_orders_pagination(self, app, sample_orders):
        """Test pagination of orders."""
        with app.app_context():
            from backend.application.sales.queries import (
                SalesOrderListQuery,
                SalesOrderListQueryHandler,
            )
            
            query = SalesOrderListQuery(tenant_id=sample_orders, page=1, page_size=2)
            handler = SalesOrderListQueryHandler()
            result = handler.handle(query)
            
            assert result.total == 3
            assert len(result.items) == 2
            assert result.page == 1
            assert result.has_next is True
    
    def test_list_orders_with_search(self, app, sample_orders):
        """Test search functionality."""
        with app.app_context():
            from backend.application.sales.queries import (
                SalesOrderListQuery,
                SalesOrderListQueryHandler,
            )
            
            query = SalesOrderListQuery(tenant_id=sample_orders, search="SO-2024-001")
            handler = SalesOrderListQueryHandler()
            result = handler.handle(query)
            
            assert result.total == 1
            assert result.items[0].number == "SO-2024-001"
    
    def test_get_order_detail(self, app, sample_orders):
        """Test getting order detail with lines."""
        with app.app_context():
            from backend.application.sales.queries import (
                SalesOrderDetailQuery,
                SalesOrderDetailQueryHandler,
            )
            
            query = SalesOrderDetailQuery(order_id=1, tenant_id=sample_orders)
            handler = SalesOrderDetailQueryHandler()
            result = handler.handle(query)
            
            assert result is not None
            assert result.number == "SO-2024-001"
            assert result.status == "confirmed"
            assert result.total_amount == 100.0
            assert len(result.lines) == 1
    
    def test_get_order_stats(self, app, sample_orders):
        """Test getting order statistics."""
        with app.app_context():
            from backend.application.sales.queries import (
                SalesOrderStatsQueryHandler,
            )
            
            handler = SalesOrderStatsQueryHandler()
            stats = handler.handle(tenant_id=sample_orders)
            
            assert stats['total_orders'] == 3
            assert stats['total_revenue'] == 600.0
            assert stats['confirmed_orders'] == 1
            assert stats['draft_orders'] == 2
    
    def test_order_not_found(self, app, sample_orders):
        """Test handling of non-existent order."""
        with app.app_context():
            from backend.application.sales.queries import (
                SalesOrderDetailQuery,
                SalesOrderDetailQueryHandler,
            )
            
            query = SalesOrderDetailQuery(order_id=9999, tenant_id=sample_orders)
            handler = SalesOrderDetailQueryHandler()
            result = handler.handle(query)
            
            assert result is None
    
    def test_read_model_is_read_only(self, app, sample_orders):
        """Verify that read model doesn't modify data."""
        with app.app_context():
            from backend.application.sales.queries import (
                SalesOrderListQuery,
                SalesOrderListQueryHandler,
            )
            
            handler = SalesOrderListQueryHandler()
            result1 = handler.handle(SalesOrderListQuery(tenant_id=sample_orders))
            
            assert result1.total == 3
            
            result2 = handler.handle(SalesOrderListQuery(tenant_id=sample_orders))
            
            assert result1.total == result2.total


class TestReadWriteSeparation:
    """Test that demonstrates CQRS read/write separation."""
    
    @pytest.fixture
    def app(self):
        app = create_app(db_url="sqlite:///:memory:")
        app.config["TESTING"] = True
        with app.app_context():
            db.create_all()
            yield app
            db.session.remove()
            db.drop_all()
    
    @pytest.fixture
    def tenant(self, app):
        with app.app_context():
            tenant = Tenant(name="Test", slug="test")
            db.session.add(tenant)
            db.session.commit()
            return tenant.id
    
    def test_write_creates_order(self, app, tenant):
        """Test that write model (repository) creates orders."""
        with app.app_context():
            from backend.infrastructure.sales.repository import SalesOrderRepository
            
            repo = SalesOrderRepository(db)
            order_data = {
                'tenant_id': tenant,
                'number': 'SO-TEST-001',
                'date': '2024-01-15',
                'customer_id': 1,
                'lines': [
                    {'product_id': 1, 'description': 'Test', 'quantity': 1, 'unit_price': 100}
                ]
            }
            
            result = repo.create(order_data)
            
            assert result['id'] is not None
            assert result['number'] == 'SO-TEST-001'
    
    def test_read_model_reads_order(self, app, tenant):
        """Test that read model can read the created order."""
        with app.app_context():
            from backend.infrastructure.sales.repository import SalesOrderRepository
            from backend.application.sales.queries import (
                SalesOrderDetailQuery,
                SalesOrderDetailQueryHandler,
            )
            
            repo = SalesOrderRepository(db)
            order_data = {
                'tenant_id': tenant,
                'number': 'SO-TEST-002',
                'date': '2024-01-16',
                'customer_id': 1,
                'lines': []
            }
            created = repo.create(order_data)
            
            query = SalesOrderDetailQuery(order_id=created['id'], tenant_id=tenant)
            handler = SalesOrderDetailQueryHandler()
            result = handler.handle(query)
            
            assert result is not None
            assert result.number == 'SO-TEST-002'
    
    def test_read_model_optimizations(self, app, tenant):
        """
        Demonstrate read model optimizations.
        
        The read model uses:
        - Optimized SQL with JOINs
        - Denormalized data (customer_name directly in result)
        - Aggregation (line_count)
        """
        with app.app_context():
            from backend.infrastructure.sales.repository import SalesOrderRepository
            from backend.application.sales.queries import (
                SalesOrderListQuery,
                SalesOrderListQueryHandler,
            )
            
            repo = SalesOrderRepository(db)
            for i in range(5):
                repo.create({
                    'tenant_id': tenant,
                    'number': f'SO-OPT-{i+1}',
                    'date': '2024-01-17',
                    'customer_id': 1,
                    'lines': [
                        {'product_id': 1, 'description': f'Item {j}', 'quantity': 1, 'unit_price': 10}
                        for j in range(3)
                    ]
                })
            
            query = SalesOrderListQuery(tenant_id=tenant)
            handler = SalesOrderListQueryHandler()
            result = handler.handle(query)
            
            assert result.total == 5
            for item in result.items:
                assert item.line_count == 3
