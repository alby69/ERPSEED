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
from backend.core.schemas.schemas import BaseSchema
from backend.core.services.generic_service import generic_service
from backend.core.utils.utils import paginate, apply_filters, apply_sorting
from backend.core.decorators.decorators import tenant_required

blp = Blueprint("inventory", __name__, url_prefix="/inventory", description="Inventory Operations")

class InventoryLocationSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = InventoryLocation

class InventoryLocationUpdateSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = InventoryLocation
        load_instance = False

class ProductStockSchema(BaseSchema):
    available_quantity = fields.Function(lambda obj: obj.available_quantity, dump_only=True)
    class Meta(BaseSchema.Meta):
        model = ProductStock

class ProductStockUpdateSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = ProductStock
        load_instance = False

class StockMovementSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = StockMovement

class InventoryCountLineSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = InventoryCountLine
        exclude = BaseSchema.Meta.exclude + ('count',)

class InventoryCountLineUpdateSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = InventoryCountLine
        load_instance = False
        exclude = BaseSchema.Meta.exclude + ('count',)

class InventoryCountSchema(BaseSchema):
    scheduled_date = fields.Date(load_default=None)
    completed_date = fields.Date(load_default=None)
    lines = fields.List(fields.Nested(InventoryCountLineSchema))
    class Meta(BaseSchema.Meta):
        model = InventoryCount


@blp.route("/locations")
class LocationList(MethodView):
    """Inventory Locations endpoints."""

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.response(200, InventoryLocationSchema(many=True))
    def get(self, tenant_id):
        """List all inventory locations."""
        query = InventoryLocation.query.filter_by(tenant_id=tenant_id, is_active=True)
        query = apply_filters(query, InventoryLocation, ['name', 'code'])
        query = apply_sorting(query, InventoryLocation, default_sort_column='name')
        items, headers = paginate(query)
        return items, 200, headers

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.arguments(InventoryLocationSchema)
    @blp.response(201, InventoryLocationSchema)
    def post(self, location_instance, tenant_id):
        """Create new inventory location."""
        return generic_service.create_tenant_resource(
            InventoryLocation, location_instance, tenant_id, unique_fields=['code']
        )


@blp.route("/locations/<int:location_id>")
class LocationResource(MethodView):
    """Single Inventory Location."""

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.response(200, InventoryLocationSchema)
    def get(self, location_id, tenant_id):
        """Get location by ID."""
        return generic_service.get_tenant_resource(
            InventoryLocation, location_id, tenant_id, not_found_message="Location not found"
        )

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.arguments(InventoryLocationUpdateSchema(partial=True))
    @blp.response(200, InventoryLocationSchema)
    def put(self, data, location_id, tenant_id):
        """Update location."""
        return generic_service.update_tenant_resource(
            InventoryLocation, location_id, tenant_id, data, not_found_message="Location not found"
        )

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.response(204)
    def delete(self, location_id, tenant_id):
        """Deactivate location."""
        location = InventoryLocation.query.filter_by(id=location_id, tenant_id=tenant_id).first()
        if not location:
            abort(404, message="Location not found")

        # Check if there is any stock at this location
        stock_at_location = ProductStock.query.filter(
            ProductStock.location_id == location_id,
            ProductStock.quantity != 0
        ).first()
        if stock_at_location:
            abort(409, message="Cannot deactivate a location that has stock. Please move or adjust stock first.")

        location.is_active = False
        db.session.commit()
        return '', 204


@blp.route("/stock")
class StockList(MethodView):
    """Product Stock endpoints."""

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.response(200, ProductStockSchema(many=True))
    def get(self, tenant_id):
        """List stock levels (optionally filtered by product or location)."""
        query = ProductStock.query.filter_by(tenant_id=tenant_id)

        if request.args.get('product_id'):
            query = query.filter_by(product_id=request.args.get('product_id'))
        if request.args.get('location_id'):
            query = query.filter_by(location_id=request.args.get('location_id'))

        query = apply_sorting(query, ProductStock)
        items, headers = paginate(query)
        return items, 200, headers

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.arguments(ProductStockSchema)
    @blp.response(201, ProductStockSchema)
    def post(self, stock_instance, tenant_id):
        """Set initial stock level for a product at a location."""
        return generic_service.create_tenant_resource(
            ProductStock, stock_instance, tenant_id,
            unique_fields=['product_id', 'location_id']
        )


@blp.route("/stock/<int:stock_id>")
class StockResource(MethodView):
    """Single Product Stock."""

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.response(200, ProductStockSchema)
    def get(self, stock_id, tenant_id):
        """Get stock level."""
        return generic_service.get_tenant_resource(
            ProductStock, stock_id, tenant_id, not_found_message="Stock record not found"
        )

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.arguments(ProductStockUpdateSchema(partial=True))
    @blp.response(200, ProductStockSchema)
    def put(self, data, stock_id, tenant_id):
        """Update stock level."""
        return generic_service.update_tenant_resource(
            ProductStock, stock_id, tenant_id, data, not_found_message="Stock record not found"
        )


@blp.route("/movements")
class StockMovementList(MethodView):
    """Stock Movement endpoints."""

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.response(200, StockMovementSchema(many=True))
    def get(self, tenant_id):
        """List stock movements."""
        query = StockMovement.query.filter_by(tenant_id=tenant_id)

        if request.args.get('product_id'):
            query = query.filter_by(product_id=request.args.get('product_id'))
        if request.args.get('location_id'):
            query = query.filter_by(location_id=request.args.get('location_id'))
        if request.args.get('type'):
            query = query.filter_by(movement_type=request.args.get('type'))

        query = apply_filters(query, StockMovement, ['movement_number', 'notes'])

        sort_by = request.args.get('sort_by')
        if not sort_by:
             query = query.order_by(StockMovement.created_at.desc())
        else:
             query = apply_sorting(query, StockMovement)

        items, headers = paginate(query)
        return items, 200, headers

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.arguments(StockMovementSchema)
    @blp.response(201, StockMovementSchema)
    def post(self, movement_instance, tenant_id):
        """Create stock movement (in, out, transfer, adjustment)."""
        movement_type = movement_instance.movement_type
        quantity = movement_instance.quantity
        product_id = movement_instance.product_id
        location_id = movement_instance.location_id

        movement_number = self._generate_movement_number(tenant_id, movement_type)

        # Set server-side fields
        movement_instance.tenant_id = tenant_id
        movement_instance.movement_number = movement_number
        movement_instance.created_by_id = get_jwt_identity()

        db.session.add(movement_instance)

        # Update stock levels
        stock = ProductStock.query.filter_by(
            tenant_id=tenant_id, product_id=product_id, location_id=location_id
        ).first()

        if not stock:
            stock = ProductStock()
            stock.tenant_id=tenant_id
            stock.product_id=product_id
            stock.location_id=location_id
            stock.quantity=0
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

        return movement_instance, 201

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
    @tenant_required
    @blp.response(200, InventoryCountSchema(many=True))
    def get(self, tenant_id):
        """List inventory counts."""
        query = InventoryCount.query.filter_by(tenant_id=tenant_id)
        if request.args.get('status'):
            query = query.filter_by(status=request.args.get('status'))

        query = apply_filters(query, InventoryCount, ['count_number', 'notes'])

        sort_by = request.args.get('sort_by')
        if not sort_by:
             query = query.order_by(InventoryCount.created_at.desc())
        else:
             query = apply_sorting(query, InventoryCount)

        items, headers = paginate(query)
        return items, 200, headers

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.arguments(InventoryCountSchema)
    @blp.response(201, InventoryCountSchema)
    def post(self, count_instance, tenant_id):
        """Create new inventory count."""
        count_number = self._generate_count_number(tenant_id)

        # Set server-side fields
        count_instance.tenant_id = tenant_id
        count_instance.count_number = count_number
        count_instance.created_by_id = get_jwt_identity()

        db.session.add(count_instance)
        db.session.flush()

        # Create count lines with current stock levels
        stock_levels = ProductStock.query.filter_by(
            tenant_id=tenant_id, location_id=count_instance.location_id
        ).all()

        for stock in stock_levels:
            line = InventoryCountLine()
            line.tenant_id=tenant_id
            line.count_id=count_instance.id
            line.product_id=stock.product_id
            line.expected_quantity=stock.quantity
            db.session.add(line)

        db.session.commit()

        return count_instance, 201

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
    @tenant_required
    @blp.response(200, InventoryCountSchema)
    def get(self, count_id, tenant_id):
        """Get inventory count with lines."""
        return generic_service.get_tenant_resource(
            InventoryCount, count_id, tenant_id, not_found_message="Inventory count not found"
        )

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.response(200, InventoryCountSchema)
    def post(self, count_id, tenant_id):
        """Complete inventory count (process variances)."""
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
                        movement = StockMovement()
                        movement.tenant_id=tenant_id
                        movement.movement_number=f'INV-ADJ-{datetime.date.today().year}{datetime.date.today().month:02d}-{count.id:05d}'
                        movement.movement_type='adjustment'
                        movement.product_id=line.product_id
                        movement.location_id=count.location_id
                        movement.quantity=line.counted_quantity
                        movement.reference_type='inventory_count'
                        movement.reference_id=count.id
                        movement.notes=f"Inventory count adjustment: {line.variance:+.0f}"
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
    @tenant_required
    @blp.arguments(InventoryCountLineUpdateSchema(partial=True))
    @blp.response(200, InventoryCountLineSchema)
    def put(self, data, count_id, line_id, tenant_id):
        """Update counted quantity for a line."""
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
    @tenant_required
    @blp.response(200, fields.List(fields.Dict()))
    def get(self, tenant_id):
        """Get stock summary (all products with total stock levels)."""

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
    @tenant_required
    @blp.response(200, fields.List(fields.Dict()))
    def get(self, tenant_id):
        """Get products below reorder level."""

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
