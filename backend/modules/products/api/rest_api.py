"""
Products Service REST API - Flask endpoints for Products Service.

Provides REST API to access ProductService functionality.
"""

from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity

from backend.modules.products import get_product_service

blp = Blueprint("products_api", __name__, url_prefix="/api/v1/products", description="Products API")


def get_service():
    """Get the product service instance."""
    return get_product_service()


@blp.route("")
class ProductList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        """List all products."""
        tenant_id = request.headers.get('X-Tenant-ID', 1, type=int)
        user_id = get_jwt_identity()

        result = get_service().execute({
            "command": "ListProducts",
            "tenant_id": tenant_id,
            "user_id": user_id,
            "pagination": {
                "page": request.args.get('page', 1, type=int),
                "per_page": request.args.get('per_page', 20, type=int)
            }
        })

        if not result.get("success"):
            abort(400, message=result.get("error", "Failed to list products"))

        return result.get("data", {})

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        """Create a new product."""
        tenant_id = request.headers.get('X-Tenant-ID', 1, type=int)
        user_id = get_jwt_identity()
        data = request.get_json()

        result = get_service().execute({
            "command": "CreateProduct",
            "tenant_id": tenant_id,
            "user_id": user_id,
            **data
        })

        if not result.get("success"):
            abort(400, message=result.get("error", "Failed to create product"))

        return result.get("data", {}), 201


@blp.route("/<int:product_id>")
class ProductDetail(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, product_id):
        """Get a product by ID."""
        tenant_id = request.headers.get('X-Tenant-ID', 1, type=int)
        user_id = get_jwt_identity()

        result = get_service().execute({
            "command": "GetProduct",
            "tenant_id": tenant_id,
            "user_id": user_id,
            "entity_id": product_id
        })

        if not result.get("success"):
            abort(404, message=result.get("error", "Product not found"))

        return result.get("data", {})

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def put(self, product_id):
        """Update a product."""
        tenant_id = request.headers.get('X-Tenant-ID', 1, type=int)
        user_id = get_jwt_identity()
        data = request.get_json()

        result = get_service().execute({
            "command": "UpdateProduct",
            "tenant_id": tenant_id,
            "user_id": user_id,
            "entity_id": product_id,
            **data
        })

        if not result.get("success"):
            abort(404, message=result.get("error", "Product not found"))

        return result.get("data", {})

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def delete(self, product_id):
        """Delete a product."""
        tenant_id = request.headers.get('X-Tenant-ID', 1, type=int)
        user_id = get_jwt_identity()

        result = get_service().execute({
            "command": "DeleteProduct",
            "tenant_id": tenant_id,
            "user_id": user_id,
            "entity_id": product_id
        })

        if not result.get("success"):
            abort(404, message=result.get("error", "Product not found"))

        return {"message": "Product deleted"}, 204


@blp.route("/<int:product_id>/stock")
class ProductStock(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def put(self, product_id):
        """Update product stock."""
        tenant_id = request.headers.get('X-Tenant-ID', 1, type=int)
        user_id = get_jwt_identity()
        data = request.get_json()

        result = get_service().execute({
            "command": "UpdateStock",
            "tenant_id": tenant_id,
            "user_id": user_id,
            "entity_id": product_id,
            "quantity": data.get("quantity", 0),
            "operation": data.get("operation", "set")  # set, add, remove
        })

        if not result.get("success"):
            abort(400, message=result.get("error", "Failed to update stock"))

        return result.get("data", {})
