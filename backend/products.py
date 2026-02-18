from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from .models import Product
from .extensions import db
from .schemas import ProductSchema
from .utils import apply_filters, paginate, apply_sorting
from .core.services.tenant_context import TenantContext

blp = Blueprint("products", __name__, description="Operations on products")

def get_tenant_query(model):
    """Get query filtered by current tenant."""
    tenant_id = TenantContext.get_tenant_id()
    if tenant_id is None:
        abort(403, message="Tenant context not found")
    return model.query.filter_by(tenant_id=tenant_id)

@blp.route("/products")
class ProductList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, ProductSchema(many=True))
    def get(self):
        """List all products"""
        query = get_tenant_query(Product)
        query = apply_filters(query, Product, ['name', 'code', 'description'])
        query = apply_sorting(query, Product)
        items, headers = paginate(query)
        return items, 200, headers

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(ProductSchema)
    @blp.response(201, ProductSchema)
    def post(self, product_data):
        """Create a new product"""
        tenant_id = TenantContext.get_tenant_id()
        if tenant_id is None:
            abort(403, message="Tenant context not found")
        
        product_data.tenant_id = tenant_id
        
        if product_data.code:
            existing = Product.query.filter_by(tenant_id=tenant_id, code=product_data.code).first()
            if existing:
                abort(409, message="Product code already exists")
            
        db.session.add(product_data)
        db.session.commit()
        return product_data

@blp.route("/products/<int:product_id>")
class ProductResource(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, ProductSchema)
    def get(self, product_id):
        """Get product by ID"""
        query = get_tenant_query(Product)
        product = query.get(product_id)
        if not product:
            abort(404, message="Product not found")
        return product
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(ProductSchema)
    @blp.response(200, ProductSchema)
    def put(self, product_data, product_id):
        """Update a product"""
        query = get_tenant_query(Product)
        product = query.get(product_id)
        if not product:
            abort(404, message="Product not found")
        
        for key, value in product_data.items():
            if hasattr(product, key):
                setattr(product, key, value)
        
        db.session.commit()
        return product
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(204)
    def delete(self, product_id):
        """Delete a product"""
        query = get_tenant_query(Product)
        product = query.get(product_id)
        if not product:
            abort(404, message="Product not found")
        
        db.session.delete(product)
        db.session.commit()
        return '', 204