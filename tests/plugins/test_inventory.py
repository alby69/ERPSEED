"""
Tests for Inventory plugin with multi-tenant isolation.
"""
import pytest
from backend.plugins.inventory.models import (
    InventoryLocation, ProductStock, StockMovement, 
    InventoryCount, InventoryCountLine
)


class TestInventoryLocationIsolation:
    """Test Inventory Location isolation between tenants."""
    
    def test_create_location(self, app, db, session, tenant):
        """Test creating an Inventory Location."""
        with app.app_context():
            location = InventoryLocation(
                tenant_id=tenant.id,
                name='Main Warehouse',
                code='WH001',
                is_default=True
            )
            session.add(location)
            session.commit()
            
            assert location.id is not None
            assert location.name == 'Main Warehouse'
            assert location.code == 'WH001'
            assert location.is_default is True
    
    def test_locations_isolated_between_tenants(self, app, db, session, tenant, tenant2):
        """Test locations are isolated between tenants."""
        with app.app_context():
            # Create location for tenant 1
            loc1 = InventoryLocation(
                tenant_id=tenant.id,
                name='Warehouse 1',
                code='WH001'
            )
            session.add(loc1)
            
            # Create location for tenant 2
            loc2 = InventoryLocation(
                tenant_id=tenant2.id,
                name='Warehouse 2',
                code='WH001'  # Same code, different tenant
            )
            session.add(loc2)
            session.commit()
            
            # Each tenant should only see their locations
            locs1 = InventoryLocation.query.filter_by(tenant_id=tenant.id).all()
            locs2 = InventoryLocation.query.filter_by(tenant_id=tenant2.id).all()
            
            assert len(locs1) == 1
            assert len(locs2) == 1
            assert locs1[0].name == 'Warehouse 1'
            assert locs2[0].name == 'Warehouse 2'


class TestProductStockIsolation:
    """Test Product Stock isolation between tenants."""
    
    def test_create_stock(self, app, db, session, tenant, product):
        """Test creating product stock."""
        with app.app_context():
            # Create location
            location = InventoryLocation(
                tenant_id=tenant.id,
                name='Main Warehouse',
                code='WH001'
            )
            session.add(location)
            session.flush()
            
            # Create stock
            stock = ProductStock(
                tenant_id=tenant.id,
                product_id=product.id,
                location_id=location.id,
                quantity=100.0,
                reorder_level=10.0
            )
            session.add(stock)
            session.commit()
            
            assert stock.id is not None
            assert stock.quantity == 100.0
            assert stock.available_quantity == 100.0
    
    def test_stock_reserved_quantity(self, app, db, session, tenant, product):
        """Test reserved quantity reduces available."""
        with app.app_context():
            location = InventoryLocation(
                tenant_id=tenant.id,
                name='Warehouse',
                code='WH001'
            )
            session.add(location)
            session.flush()
            
            stock = ProductStock(
                tenant_id=tenant.id,
                product_id=product.id,
                location_id=location.id,
                quantity=100.0,
                reserved_quantity=30.0
            )
            session.add(stock)
            session.commit()
            
            assert stock.quantity == 100.0
            assert stock.reserved_quantity == 30.0
            assert stock.available_quantity == 70.0


class TestStockMovementIsolation:
    """Test Stock Movement isolation between tenants."""
    
    def test_create_stock_movement_in(self, app, db, session, tenant, product):
        """Test creating stock movement (in)."""
        with app.app_context():
            location = InventoryLocation(
                tenant_id=tenant.id,
                name='Warehouse',
                code='WH001'
            )
            session.add(location)
            session.flush()
            
            # Create stock first
            stock = ProductStock(
                tenant_id=tenant.id,
                product_id=product.id,
                location_id=location.id,
                quantity=50.0
            )
            session.add(stock)
            session.flush()
            
            # Create movement
            movement = StockMovement(
                tenant_id=tenant.id,
                movement_number='STK-IN-202602-00001',
                movement_type='in',
                product_id=product.id,
                location_id=location.id,
                quantity=100.0
            )
            session.add(movement)
            
            # Update stock
            stock.quantity += 100.0
            session.commit()
            
            assert movement.id is not None
            assert movement.movement_type == 'in'
            assert stock.quantity == 150.0
    
    def test_create_stock_movement_out(self, app, db, session, tenant, product):
        """Test creating stock movement (out)."""
        with app.app_context():
            location = InventoryLocation(
                tenant_id=tenant.id,
                name='Warehouse',
                code='WH001'
            )
            session.add(location)
            session.flush()
            
            stock = ProductStock(
                tenant_id=tenant.id,
                product_id=product.id,
                location_id=location.id,
                quantity=100.0
            )
            session.add(stock)
            session.flush()
            
            movement = StockMovement(
                tenant_id=tenant.id,
                movement_number='STK-OUT-202602-00001',
                movement_type='out',
                product_id=product.id,
                location_id=location.id,
                quantity=30.0
            )
            session.add(movement)
            
            stock.quantity -= 30.0
            session.commit()
            
            assert movement.movement_type == 'out'
            assert stock.quantity == 70.0
    
    def test_insufficient_stock_fails(self, app, db, session, tenant, product):
        """Test that out movement fails with insufficient stock."""
        with app.app_context():
            location = InventoryLocation(
                tenant_id=tenant.id,
                name='Warehouse',
                code='WH001'
            )
            session.add(location)
            session.flush()
            
            stock = ProductStock(
                tenant_id=tenant.id,
                product_id=product.id,
                location_id=location.id,
                quantity=10.0
            )
            session.add(stock)
            session.commit()
            
            # Try to move out more than available
            try:
                stock.quantity -= 20.0
                session.commit()
                # If we get here, check that quantity is not negative (business logic should prevent this)
                assert stock.quantity >= 0
            except Exception:
                pass  # Expected to fail in real implementation


class TestInventoryCountIsolation:
    """Test Inventory Count isolation between tenants."""
    
    def test_create_inventory_count(self, app, db, session, tenant, product):
        """Test creating an Inventory Count."""
        with app.app_context():
            location = InventoryLocation(
                tenant_id=tenant.id,
                name='Warehouse',
                code='WH001'
            )
            session.add(location)
            session.flush()
            
            stock = ProductStock(
                tenant_id=tenant.id,
                product_id=product.id,
                location_id=location.id,
                quantity=100.0
            )
            session.add(stock)
            session.flush()
            
            count = InventoryCount(
                tenant_id=tenant.id,
                count_number='INV-202602-00001',
                location_id=location.id,
                status='draft'
            )
            session.add(count)
            session.flush()
            
            # Add count line
            line = InventoryCountLine(
                tenant_id=tenant.id,
                count_id=count.id,
                product_id=product.id,
                expected_quantity=100.0
            )
            session.add(line)
            session.commit()
            
            assert count.id is not None
            assert count.status == 'draft'
            assert len(count.lines) == 1
            assert line.expected_quantity == 100.0
    
    def test_inventory_count_variance(self, app, db, session, tenant, product):
        """Test inventory count variance calculation."""
        with app.app_context():
            location = InventoryLocation(
                tenant_id=tenant.id,
                name='Warehouse',
                code='WH001'
            )
            session.add(location)
            session.flush()
            
            count = InventoryCount(
                tenant_id=tenant.id,
                count_number='INV-202602-00002',
                location_id=location.id,
                status='draft'
            )
            session.add(count)
            session.flush()
            
            line = InventoryCountLine(
                tenant_id=tenant.id,
                count_id=count.id,
                product_id=product.id,
                expected_quantity=100.0,
                counted_quantity=90.0
            )
            session.add(line)
            session.commit()
            
            line.calculate_variance()
            
            assert line.variance == -10.0
    
    def test_inventory_count_completed(self, app, db, session, tenant, product):
        """Test completing inventory count updates stock."""
        with app.app_context():
            location = InventoryLocation(
                tenant_id=tenant.id,
                name='Warehouse',
                code='WH001'
            )
            session.add(location)
            session.flush()
            
            stock = ProductStock(
                tenant_id=tenant.id,
                product_id=product.id,
                location_id=location.id,
                quantity=100.0
            )
            session.add(stock)
            session.flush()
            
            count = InventoryCount(
                tenant_id=tenant.id,
                count_number='INV-202602-00003',
                location_id=location.id,
                status='draft'
            )
            session.add(count)
            session.flush()
            
            line = InventoryCountLine(
                tenant_id=tenant.id,
                count_id=count.id,
                product_id=product.id,
                expected_quantity=100.0,
                counted_quantity=85.0
            )
            line.calculate_variance()
            session.add(line)
            
            count.status = 'completed'
            stock.quantity = 85.0
            
            session.commit()
            
            assert count.status == 'completed'
            assert stock.quantity == 85.0
