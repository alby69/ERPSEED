from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from .models import Product
from .extensions import db, ma
from .schemas import ProductSchema, BaseSchema
from .utils import apply_filters, paginate, apply_sorting
from .decorators import tenant_required
from .services.generic_service import generic_service

blp = Blueprint("products", __name__, description="Operations on products")

class ProductUpdateSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = Product
        load_instance = False

@blp.route("/products")
class ProductList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.response(200, ProductSchema(many=True))
    def get(self, tenant_id):
        """List all products"""
        query = Product.query.filter_by(tenant_id=tenant_id)
        query = apply_filters(query, Product, ['name', 'code', 'description'])
        query = apply_sorting(query, Product)
        items, headers = paginate(query)
        return items, 200, headers

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.arguments(ProductSchema)
    @blp.response(201, ProductSchema)
    def post(self, product_data, tenant_id):
        """Create a new product"""
        return generic_service.create_tenant_resource(
            Product, product_data, tenant_id, unique_fields=['code']
        )

@blp.route("/products/<int:product_id>")
class ProductResource(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.response(200, ProductSchema)
    def get(self, product_id, tenant_id):
        """Get product by ID"""
        return generic_service.get_tenant_resource(
            Product, product_id, tenant_id, not_found_message="Product not found"
        )
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.arguments(ProductUpdateSchema(partial=True))
    @blp.response(200, ProductSchema)
    def put(self, product_data, product_id, tenant_id):
        """Update a product"""
        return generic_service.update_tenant_resource(
            Product, product_id, tenant_id, product_data, not_found_message="Product not found"
        )
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.response(204)
    def delete(self, product_id, tenant_id):
        """Delete a product"""
        def check_dependencies(product):
            from .models import SalesOrderLine, PurchaseOrderLine
            if SalesOrderLine.query.filter_by(product_id=product.id).first() or \
               PurchaseOrderLine.query.filter_by(product_id=product.id).first() or \
               product.stock_levels.first():
                abort(409, message="Cannot delete a product that has associated orders or stock records. "
                                   "Consider deactivating it instead.")

        generic_service.delete_tenant_resource(
            Product, product_id, tenant_id,
            pre_delete_check=check_dependencies,
            not_found_message="Product not found"
        )
        return '', 204