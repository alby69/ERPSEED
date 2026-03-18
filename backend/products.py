from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from .extensions import db
from .decorators import tenant_required
from .schemas import ProductSchema, BaseSchema
from backend.products_service import get_product_service

blp = Blueprint("products", __name__, description="Operations on products")


@blp.route("/products")
class ProductList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.response(200, ProductSchema(many=True))
    def get(self, tenant_id):
        """List all products"""
        service = get_product_service()
        result = service.execute({
            "command": "ListProducts",
            "tenant_id": tenant_id
        })
        
        if not result.get("success"):
            abort(400, message=result.get("error", "Failed to list products"))
        
        return result["data"]["items"]

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.arguments(ProductSchema)
    @blp.response(201, ProductSchema)
    def post(self, product_data, tenant_id):
        """Create a new product"""
        service = get_product_service()
        
        payload = {}
        if hasattr(product_data, 'items'):
            for key, value in product_data.items():
                payload[key] = value
        else:
            payload = dict(product_data)
        
        result = service.execute({
            "command": "CreateProduct",
            "tenant_id": tenant_id,
            **payload
        })
        
        if not result.get("success"):
            abort(400, message=result.get("error", "Failed to create product"))
        
        return result["data"], 201


@blp.route("/products/<int:product_id>")
class ProductResource(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.response(200, ProductSchema)
    def get(self, product_id, tenant_id):
        """Get product by ID"""
        service = get_product_service()
        result = service.execute({
            "command": "GetProduct",
            "tenant_id": tenant_id,
            "entity_id": product_id
        })
        
        if not result.get("success"):
            abort(404, message=result.get("error", "Product not found"))
        
        return result["data"]
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.arguments(BaseSchema)
    @blp.response(200, ProductSchema)
    def put(self, product_data, product_id, tenant_id):
        """Update a product"""
        service = get_product_service()
        
        payload = {}
        if hasattr(product_data, 'items'):
            for key, value in product_data.items():
                payload[key] = value
        else:
            payload = dict(product_data)
        
        result = service.execute({
            "command": "UpdateProduct",
            "tenant_id": tenant_id,
            "entity_id": product_id,
            **payload
        })
        
        if not result.get("success"):
            abort(400, message=result.get("error", "Failed to update product"))
        
        return result["data"]
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @tenant_required
    @blp.response(204)
    def delete(self, product_id, tenant_id):
        """Delete a product"""
        service = get_product_service()
        result = service.execute({
            "command": "DeleteProduct",
            "tenant_id": tenant_id,
            "entity_id": product_id
        })
        
        if not result.get("success"):
            abort(409, message=result.get("error", "Failed to delete product"))
        
        return '', 204
