"""
Inventory Plugin Models.

Provides inventory management functionality:
- Inventory Locations (warehouses)
- Stock Movements (in/out transfers)
- Inventory Counts
"""
from datetime import datetime, date
from backend.extensions import db


class InventoryLocation(db.Model):
    """Inventory Location - warehouse or storage location."""
    __tablename__ = 'inventory_locations'

    # Multi-tenant support
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    code = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    address = db.Column(db.String(255))
    city = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tenant = db.relationship('Tenant', backref=db.backref('inventory_locations', lazy='dynamic'))
    stock_lines = db.relationship('ProductStock', back_populates='location', lazy='dynamic')
    movements = db.relationship('StockMovement', back_populates='location', lazy='dynamic')

    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'code', name='uix_tenant_location_code'),
    )

    def __repr__(self):
        return f'<InventoryLocation {self.code}: {self.name}>'


class ProductStock(db.Model):
    """Current stock levels for products at locations."""
    __tablename__ = 'product_stock'

    # Multi-tenant support
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('inventory_locations.id'), nullable=False)
    quantity = db.Column(db.Float, default=0.0)
    reserved_quantity = db.Column(db.Float, default=0.0)
    reorder_level = db.Column(db.Float, default=0.0)
    reorder_quantity = db.Column(db.Float, default=0.0)
    last_counted_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    product = db.relationship('Product', backref=db.backref('stock_levels', lazy='dynamic'))
    location = db.relationship('InventoryLocation', back_populates='stock_lines')
    tenant = db.relationship('Tenant', backref=db.backref('product_stock', lazy='dynamic'))

    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'product_id', 'location_id', name='uix_tenant_product_location'),
    )

    @property
    def available_quantity(self):
        """Quantity available for sale (total - reserved)."""
        return max(0, self.quantity - self.reserved_quantity)

    def __repr__(self):
        return f'<ProductStock {self.product_id}@{self.location_id}: {self.quantity}>'


class StockMovement(db.Model):
    """Stock Movement - tracks all inventory changes."""
    __tablename__ = 'stock_movements'

    # Multi-tenant support
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)

    id = db.Column(db.Integer, primary_key=True)
    movement_number = db.Column(db.String(50), nullable=False, index=True)
    movement_type = db.Column(db.String(20), nullable=False)  # in, out, transfer, adjustment
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('inventory_locations.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    reference_type = db.Column(db.String(50))  # purchase_order, sales_order, etc.
    reference_id = db.Column(db.Integer)
    notes = db.Column(db.Text)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship('Product', backref=db.backref('stock_movements', lazy='dynamic'))
    location = db.relationship('InventoryLocation', back_populates='movements')
    creator = db.relationship('User')
    tenant = db.relationship('Tenant', backref=db.backref('stock_movements', lazy='dynamic'))

    __table_args__ = (
        db.Index('ix_stock_movement_tenant_date', 'tenant_id', 'created_at'),
    )

    def __repr__(self):
        return f'<StockMovement {self.movement_number}: {self.movement_type} {self.quantity}>'


class InventoryCount(db.Model):
    """Inventory Count - scheduled physical inventory checks."""
    __tablename__ = 'inventory_counts'

    # Multi-tenant support
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)

    id = db.Column(db.Integer, primary_key=True)
    count_number = db.Column(db.String(50), nullable=False, index=True)
    location_id = db.Column(db.Integer, db.ForeignKey('inventory_locations.id'), nullable=False)
    status = db.Column(db.String(20), default='draft')  # draft, in_progress, completed, cancelled
    scheduled_date = db.Column(db.Date)
    completed_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    location = db.relationship('InventoryLocation')
    creator = db.relationship('User')
    lines = db.relationship('InventoryCountLine', back_populates='count', cascade='all, delete-orphan')
    tenant = db.relationship('Tenant', backref=db.backref('inventory_counts', lazy='dynamic'))

    def __repr__(self):
        return f'<InventoryCount {self.count_number}>'


class InventoryCountLine(db.Model):
    """Individual line in an Inventory Count."""
    __tablename__ = 'inventory_count_lines'

    # Multi-tenant support
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)

    id = db.Column(db.Integer, primary_key=True)
    count_id = db.Column(db.Integer, db.ForeignKey('inventory_counts.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    expected_quantity = db.Column(db.Float, default=0.0)
    counted_quantity = db.Column(db.Float)
    variance = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    count = db.relationship('InventoryCount', back_populates='lines')
    product = db.relationship('Product')
    tenant = db.relationship('Tenant', backref=db.backref('inventory_count_lines', lazy='dynamic'))

    def calculate_variance(self):
        """Calculate variance between expected and counted."""
        if self.counted_quantity is not None:
            self.variance = self.counted_quantity - (self.expected_quantity or 0)
        return self.variance

    def __repr__(self):
        return f'<InventoryCountLine {self.product_id}: {self.counted_quantity} vs {self.expected_quantity}>'
