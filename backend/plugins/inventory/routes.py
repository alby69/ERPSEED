"""
Inventory Plugin Routes.

API endpoints for inventory operations:
- Inventory Locations management
- Stock Levels
- Stock Movements
- Inventory Counts
"""
from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
import datetime
from marshmallow import fields

from .models import InventoryLocation, ProductStock, StockMovement, InventoryCount, InventoryCountLine
from backend.core.services.tenant_context import TenantContext
from backend.extensions import db, ma

blp = Blueprint("inventory", __name__, url_prefix="/inventory", description="Inventory Operations")

class InventoryLocationSchema(ma.SQLAlchemyAutoSchema):
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    class Meta:
        model = InventoryLocation
        load_instance = True

class ProductStockSchema(ma.SQLAlchemyAutoSchema):
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    class Meta:
        model = ProductStock
        load_instance = True
        include_fk = True

class StockMovementSchema(ma.SQLAlchemyAutoSchema):
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    class Meta:
        model = StockMovement
        load_instance = True
        include_fk = True

class InventoryCountLineSchema(ma.SQLAlchemyAutoSchema):
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    class Meta:
        model = InventoryCountLine
        load_instance = True
        include_fk = True
        exclude = ('count',)

class InventoryCountSchema(ma.SQLAlchemyAutoSchema):
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    scheduled_date = fields.Date()
    completed_date = fields.Date()
    lines = fields.List(fields.Nested(InventoryCountLineSchema))
    class Meta:
        model = InventoryCount
        load_instance = True
        include_fk = True


def get_tenant_query(model):
    """Get query filtered by current tenant."""
    tenant_id = TenantContext.get_tenant_id()
    if tenant_id is None:
        abort(403, message="Tenant context not found")
    return model.query.filter_by(tenant_id=tenant_id)


@blp.route("/locations")
class LocationList(MethodView):
    """Inventory Locations endpoints."""
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, InventoryLocationSchema(many=True))
    def get(self):
        """List all inventory locations."""
        tenant_id = TenantContext.get_tenant_id()
        if tenant_id is None:
            abort(403, message="Tenant context not found")
        query = InventoryLocation.query.filter_by(tenant_id=tenant_id, is_active=True).order_by(InventoryLocation.name)
        return query.all()
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(InventoryLocationSchema)
    @blp.response(201, InventoryLocationSchema)
    def post(self):
        """Create new inventory location."""
        data = request.get_json()
        tenant_id = TenantContext.get_tenant_id()
        if tenant_id is None:
            abort(403, message="Tenant context not found")
        
        existing = InventoryLocation.query.filter_by(tenant_id=tenant_id, code=data['code']).first()
        if existing:
            abort(409, message=f"Location code '{data['code']}' already exists.")
        
        location = InventoryLocation(
            tenant_id=tenant_id, # type: ignore
            name=data['name'], # type: ignore
            code=data['code'], # type: ignore
            description=data.get('description'), # type: ignore
            address=data.get('address'), # type: ignore
            city=data.get('city'), # type: ignore
            is_default=data.get('is_default', False) # type: ignore
        )
        
        db.session.add(location)
        db.session.commit()
        
        return location, 201


@blp.route("/locations/<int:location_id>")
class LocationResource(MethodView):
    """Single Inventory Location."""
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, InventoryLocationSchema)
    def get(self, location_id):
        """Get location by ID."""
        tenant_id = TenantContext.get_tenant_id()
        if tenant_id is None:
            abort(403, message="Tenant context not found")
        location = InventoryLocation.query.filter_by(id=location_id, tenant_id=tenant_id).first()
        if not location:
            abort(404, message="Location not found")
        return location
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(InventoryLocationSchema(partial=True))
    @blp.response(200, InventoryLocationSchema)
    def put(self, location_id):
        """Update location."""
        data = request.get_json()
        tenant_id = TenantContext.get_tenant_id()
        if tenant_id is None:
            abort(403, message="Tenant context not found")
        location = InventoryLocation.query.filter_by(id=location_id, tenant_id=tenant_id).first()
        if not location:
            abort(404, message="Location not found")
        
        for key, value in data.items():
            if hasattr(location, key):
                setattr(location, key, value)
        
        db.session.commit()
        return location
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(204)
    def delete(self, location_id):
        """Deactivate location."""
        tenant_id = TenantContext.get_tenant_id()
        if tenant_id is None:
            abort(403, message="Tenant context not found")
        location = InventoryLocation.query.filter_by(id=location_id, tenant_id=tenant_id).first()
        if not location:
            abort(404, message="Location not found")
        location.is_active = False
        db.session.commit()
        return '', 204


@blp.route("/stock")
class StockList(MethodView):
    """Product Stock endpoints."""
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, ProductStockSchema(many=True))
    def get(self):
        """List stock levels (optionally filtered by product or location)."""
        tenant_id = TenantContext.get_tenant_id()
        if tenant_id is None:
            abort(403, message="Tenant context not found")
        
        product_id = request.args.get('product_id', type=int)
        location_id = request.args.get('location_id', type=int)
        
        query = ProductStock.query.filter_by(tenant_id=tenant_id)
        
        if product_id:
            query = query.filter_by(product_id=product_id)
        if location_id:
            query = query.filter_by(location_id=location_id)
        
        return query.all()
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(ProductStockSchema)
    @blp.response(201, ProductStockSchema)
    def post(self):
        """Set initial stock level for a product at a location."""
        data = request.get_json()
        tenant_id = TenantContext.get_tenant_id()
        if tenant_id is None:
            abort(403, message="Tenant context not found")
        
        existing = ProductStock.query.filter_by(
            tenant_id=tenant_id,
            product_id=data['product_id'],
            location_id=data['location_id']
        ).first()
        
        if existing:
            abort(409, message="Stock record already exists for this product at this location.")
        
        stock = ProductStock(
            tenant_id=tenant_id, # type: ignore
            product_id=data['product_id'], # type: ignore
            location_id=data['location_id'], # type: ignore
            quantity=data.get('quantity', 0), # type: ignore
            reorder_level=data.get('reorder_level', 0), # type: ignore
            reorder_quantity=data.get('reorder_quantity', 0) # type: ignore
        )
        
        db.session.add(stock)
        db.session.commit()
        
        return stock, 201


@blp.route("/stock/<int:stock_id>")
class StockResource(MethodView):
    """Single Product Stock."""
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, ProductStockSchema)
    def get(self, stock_id):
        """Get stock level."""
        tenant_id = TenantContext.get_tenant_id()
        if tenant_id is None:
            abort(403, message="Tenant context not found")
        stock = ProductStock.query.filter_by(id=stock_id, tenant_id=tenant_id).first()
        if not stock:
            abort(404, message="Stock record not found")
        return stock
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(ProductStockSchema(partial=True))
    @blp.response(200, ProductStockSchema)
    def put(self, stock_id):
        """Update stock level."""
        data = request.get_json()
        tenant_id = TenantContext.get_tenant_id()
        if tenant_id is None:
            abort(403, message="Tenant context not found")
        stock = ProductStock.query.filter_by(id=stock_id, tenant_id=tenant_id).first()
        if not stock:
            abort(404, message="Stock record not found")
        
        for key, value in data.items():
            if hasattr(stock, key):
                setattr(stock, key, value)
        
        db.session.commit()
        return stock


@blp.route("/movements")
class StockMovementList(MethodView):
    """Stock Movement endpoints."""
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, StockMovementSchema(many=True))
    def get(self):
        """List stock movements."""
        tenant_id = TenantContext.get_tenant_id()
        if tenant_id is None:
            abort(403, message="Tenant context not found")
        
        product_id = request.args.get('product_id', type=int)
        location_id = request.args.get('location_id', type=int)
        movement_type = request.args.get('type')
        
        query = StockMovement.query.filter_by(tenant_id=tenant_id)
        
        if product_id:
            query = query.filter_by(product_id=product_id)
        if location_id:
            query = query.filter_by(location_id=location_id)
        if movement_type:
            query = query.filter_by(movement_type=movement_type)
        
        return query.order_by(StockMovement.created_at.desc()).limit(100).all()
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(StockMovementSchema)
    @blp.response(201, StockMovementSchema)
    def post(self):
        """Create stock movement (in, out, transfer, adjustment)."""
        data = request.get_json()
        tenant_id = TenantContext.get_tenant_id()
        if tenant_id is None:
            abort(403, message="Tenant context not found")
        
        movement_type = data.get('movement_type')
        quantity = data.get('quantity', 0)
        product_id = data['product_id']
        location_id = data['location_id']
        
        movement_number = self._generate_movement_number(tenant_id, movement_type)
        
        movement = StockMovement(
            tenant_id=tenant_id, # type: ignore
            movement_number=movement_number, # type: ignore
            movement_type=movement_type, # type: ignore
            product_id=product_id, # type: ignore
            location_id=location_id, # type: ignore
            quantity=quantity, # type: ignore
            reference_type=data.get('reference_type'), # type: ignore
            reference_id=data.get('reference_id'), # type: ignore
            notes=data.get('notes'), # type: ignore
            created_by_id=get_jwt_identity() # type: ignore
        )
        
        db.session.add(movement)
        
        # Update stock levels
        stock = ProductStock.query.filter_by(
            tenant_id=tenant_id,
            product_id=product_id,
            location_id=location_id
        ).first()
        
        if not stock:
            stock = ProductStock(
                tenant_id=tenant_id, # type: ignore
                product_id=product_id, # type: ignore
                location_id=location_id, # type: ignore
                quantity=0 # type: ignore
            )
            db.session.add(stock)
            db.session.flush()
        
        if movement_type == 'in':
            stock.quantity += quantity
        elif movement_type == 'out':
            if stock.quantity < quantity:
                abort(400, message=f"Insufficient stock. Available: {stock.quantity}")
            stock.quantity -= quantity
        elif movement_type == 'adjustment':
            stock.quantity = quantity
        
        db.session.commit()
        
        return movement, 201
    
    def _generate_movement_number(self, tenant_id, movement_type):
        """Generate unique movement number."""
        prefix = {
            'in': 'STK-IN',
            'out': 'STK-OUT',
            'transfer': 'STK-TRF',
            'adjustment': 'STK-ADJ'
        }.get(movement_type, 'STK')
        
        today = datetime.date.today()
        
        last_movement = StockMovement.query.filter(
            StockMovement.tenant_id == tenant_id,
            StockMovement.movement_number.like(f'{prefix}%')
        ).order_by(StockMovement.movement_number.desc()).first()
        
        if last_movement:
            last_num = int(last_movement.movement_number.split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1
        
        return f'{prefix}-{today.year}{today.month:02d}-{new_num:05d}'


@blp.route("/counts")
class InventoryCountList(MethodView):
    """Inventory Count endpoints."""
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, InventoryCountSchema(many=True))
    def get(self):
        """List inventory counts."""
        tenant_id = TenantContext.get_tenant_id()
        if tenant_id is None:
            abort(403, message="Tenant context not found")
        
        status = request.args.get('status')
        
        query = InventoryCount.query.filter_by(tenant_id=tenant_id)
        if status:
            query = query.filter_by(status=status)
        
        return query.order_by(InventoryCount.created_at.desc()).all()
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(InventoryCountSchema)
    @blp.response(201, InventoryCountSchema)
    def post(self):
        """Create new inventory count."""
        data = request.get_json()
        tenant_id = TenantContext.get_tenant_id()
        if tenant_id is None:
            abort(403, message="Tenant context not found")
        
        count_number = self._generate_count_number(tenant_id)
        
        count = InventoryCount(
            tenant_id=tenant_id, # type: ignore
            count_number=count_number, # type: ignore
            location_id=data['location_id'], # type: ignore
            scheduled_date=data.get('scheduled_date'), # type: ignore
            notes=data.get('notes'), # type: ignore
            created_by_id=get_jwt_identity() # type: ignore
        )
        
        db.session.add(count)
        db.session.flush()
        
        # Create count lines with current stock levels
        stock_levels = ProductStock.query.filter_by(
            tenant_id=tenant_id,
            location_id=data['location_id']
        ).all()
        
        for stock in stock_levels:
            line = InventoryCountLine(
                tenant_id=tenant_id, # type: ignore
                count_id=count.id, # type: ignore
                product_id=stock.product_id, # type: ignore
                expected_quantity=stock.quantity # type: ignore
            )
            db.session.add(line)
        
        db.session.commit()
        
        return count, 201
    
    def _generate_count_number(self, tenant_id):
        """Generate unique count number."""
        today = datetime.date.today()
        
        last_count = InventoryCount.query.filter(
            InventoryCount.tenant_id == tenant_id,
            InventoryCount.count_number.like(f'INV%')
        ).order_by(InventoryCount.count_number.desc()).first()
        
        if last_count:
            last_num = int(last_count.count_number.split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1
        
        return f'INV-{today.year}{today.month:02d}-{new_num:05d}'


@blp.route("/counts/<int:count_id>")
class InventoryCountResource(MethodView):
    """Single Inventory Count."""
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, InventoryCountSchema)
    def get(self, count_id):
        """Get inventory count with lines."""
        tenant_id = TenantContext.get_tenant_id()
        if tenant_id is None:
            abort(403, message="Tenant context not found")
        count = InventoryCount.query.filter_by(id=count_id, tenant_id=tenant_id).first()
        if not count:
            abort(404, message="Inventory count not found")
        return count
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, InventoryCountSchema)
    def post(self, count_id):
        """Complete inventory count (process variances)."""
        tenant_id = TenantContext.get_tenant_id()
        if tenant_id is None:
            abort(403, message="Tenant context not found")
        count = InventoryCount.query.filter_by(id=count_id, tenant_id=tenant_id).first()
        if not count:
            abort(404, message="Inventory count not found")
        
        if count.status != 'draft':
            abort(400, message="Only draft counts can be completed.")
        
        # Process each line and update stock
        for line in count.lines:
            if line.counted_quantity is not None:
                line.calculate_variance()
                
                # Update stock if there's a variance
                if line.variance != 0:
                    stock = ProductStock.query.filter_by(
                        tenant_id=tenant_id,
                        product_id=line.product_id,
                        location_id=count.location_id
                    ).first()
                    
                    if stock:
                        stock.quantity = line.counted_quantity
                        
                        # Create adjustment movement
                        movement = StockMovement(
                            tenant_id=tenant_id, # type: ignore
                            movement_number=f'INV-ADJ-{datetime.date.today().year}{datetime.date.today().month:02d}-{count.id:05d}', # type: ignore
                            movement_type='adjustment', # type: ignore
                            product_id=line.product_id, # type: ignore
                            location_id=count.location_id, # type: ignore
                            quantity=line.counted_quantity, # type: ignore
                            reference_type='inventory_count', # type: ignore
                            reference_id=count.id, # type: ignore
                            notes=f"Inventory count adjustment: {line.variance:+.0f}" # type: ignore
                        )
                        db.session.add(movement)
        
        count.status = 'completed'
        count.completed_date = datetime.date.today()
        db.session.commit()
        
        return count


@blp.route("/counts/<int:count_id>/lines/<int:line_id>")
class InventoryCountLineResource(MethodView):
    """Update inventory count line."""
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(InventoryCountLineSchema(partial=True))
    @blp.response(200, InventoryCountLineSchema)
    def put(self, count_id, line_id):
        """Update counted quantity for a line."""
        data = request.get_json()
        tenant_id = TenantContext.get_tenant_id()
        if tenant_id is None:
            abort(403, message="Tenant context not found")
        
        count = InventoryCount.query.filter_by(id=count_id, tenant_id=tenant_id).first()
        if not count:
            abort(404, message="Inventory count not found")
        
        if count.status != 'draft':
            abort(400, message="Cannot modify a completed count.")
        
        line = InventoryCountLine.query.filter_by(id=line_id, tenant_id=tenant_id, count_id=count_id).first()
        if not line:
            abort(404, message="Count line not found")
        
        if 'counted_quantity' in data:
            line.counted_quantity = data['counted_quantity']
            line.calculate_variance()
        
        if 'notes' in data:
            line.notes = data['notes']
        
        db.session.commit()
        
        return line


@blp.route("/reports/stock-summary")
class StockSummary(MethodView):
    """Stock Summary Report."""
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, fields.List(fields.Dict()))
    def get(self):
        """Get stock summary (all products with total stock levels)."""
        tenant_id = TenantContext.get_tenant_id()
        if tenant_id is None:
            abort(403, message="Tenant context not found")
        
        from backend.models import Product
        from sqlalchemy import func
        
        # Get total stock per product
        results = db.session.query(
            Product.id,
            Product.name,
            Product.code,
            func.sum(ProductStock.quantity).label('total_quantity'),
            func.sum(ProductStock.reserved_quantity).label('total_reserved')
        ).join(
            ProductStock, Product.id == ProductStock.product_id
        ).filter(
            ProductStock.tenant_id == tenant_id
        ).group_by(Product.id).all()
        
        summary = []
        for r in results:
            summary.append({
                'product_id': r.id,
                'product_name': r.name,
                'product_code': r.code,
                'total_quantity': r.total_quantity or 0,
                'total_reserved': r.total_reserved or 0,
                'available': (r.total_quantity or 0) - (r.total_reserved or 0)
            })
        
        return summary


@blp.route("/reports/low-stock")
class LowStockReport(MethodView):
    """Low Stock Report."""
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, fields.List(fields.Dict()))
    def get(self):
        """Get products below reorder level."""
        tenant_id = TenantContext.get_tenant_id()
        if tenant_id is None:
            abort(403, message="Tenant context not found")
        
        # Products where available stock <= reorder level
        from backend.models import Product
        from sqlalchemy import func, case
        
        results = db.session.query(
            Product.id,
            Product.name,
            Product.code,
            func.sum(ProductStock.quantity).label('total_quantity'),
            func.sum(ProductStock.reserved_quantity).label('total_reserved'),
            func.max(ProductStock.reorder_level).label('reorder_level')
        ).join(
            ProductStock, Product.id == ProductStock.product_id
        ).filter(
            ProductStock.tenant_id == tenant_id
        ).group_by(Product.id).having(
            (func.sum(ProductStock.quantity) - func.coalesce(func.sum(ProductStock.reserved_quantity), 0)) <= func.max(ProductStock.reorder_level)
        ).all()
        
        low_stock = []
        for r in results:
            available = (r.total_quantity or 0) - (r.total_reserved or 0)
            low_stock.append({
                'product_id': r.id,
                'product_name': r.name,
                'product_code': r.code,
                'current_stock': r.total_quantity or 0,
                'reserved': r.total_reserved or 0,
                'available': available,
                'reorder_level': r.reorder_level or 0,
                'needs_reorder': available <= (r.reorder_level or 0)
            })
        
        return low_stock
