from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.extensions import db
from backend.models import ProductCategory

blp = Blueprint("product_categories", __name__, description="Product Categories API")


def category_to_dict(cat):
    return {
        "id": cat.id,
        "tenant_id": cat.tenant_id,
        "name": cat.name,
        "code": cat.code,
        "description": cat.description,
        "parent_id": cat.parent_id,
        "is_active": cat.is_active,
        "sort_order": cat.sort_order,
        "created_at": cat.created_at.isoformat() if cat.created_at else None,
        "updated_at": cat.updated_at.isoformat() if cat.updated_at else None,
    }


@blp.route("/api/v1/product-categories")
class CategoryList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        tenant_id = request.headers.get('X-Tenant-ID', 1, type=int)
        categories = ProductCategory.query.filter_by(tenant_id=tenant_id, deleted_at=None).order_by(ProductCategory.sort_order, ProductCategory.name).all()
        return [category_to_dict(c) for c in categories]

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        tenant_id = request.headers.get('X-Tenant-ID', 1, type=int)
        data = request.get_json() or {}

        if not data.get("name") or not data.get("code"):
            abort(400, message="name and code are required")

        existing = ProductCategory.query.filter_by(tenant_id=tenant_id, code=data["code"]).first()
        if existing:
            abort(400, message=f"Category with code '{data['code']}' already exists")

        cat = ProductCategory(
            tenant_id=tenant_id,
            name=data["name"],
            code=data["code"],
            description=data.get("description", ""),
            parent_id=data.get("parent_id"),
            is_active=data.get("is_active", True),
            sort_order=data.get("sort_order", 0),
        )
        db.session.add(cat)
        db.session.commit()
        return category_to_dict(cat), 201


@blp.route("/api/v1/product-categories/<int:category_id>")
class CategoryDetail(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, category_id):
        tenant_id = request.headers.get('X-Tenant-ID', 1, type=int)
        cat = ProductCategory.query.filter_by(id=category_id, tenant_id=tenant_id, deleted_at=None).first()
        if not cat:
            abort(404, message="Category not found")
        return category_to_dict(cat)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def put(self, category_id):
        tenant_id = request.headers.get('X-Tenant-ID', 1, type=int)
        cat = ProductCategory.query.filter_by(id=category_id, tenant_id=tenant_id, deleted_at=None).first()
        if not cat:
            abort(404, message="Category not found")
        data = request.get_json() or {}

        if "name" in data:
            cat.name = data["name"]
        if "code" in data:
            existing = ProductCategory.query.filter_by(tenant_id=tenant_id, code=data["code"]).first()
            if existing and existing.id != category_id:
                abort(400, message=f"Category with code '{data['code']}' already exists")
            cat.code = data["code"]
        if "description" in data:
            cat.description = data["description"]
        if "parent_id" in data:
            cat.parent_id = data["parent_id"]
        if "is_active" in data:
            cat.is_active = data["is_active"]
        if "sort_order" in data:
            cat.sort_order = data["sort_order"]

        db.session.commit()
        return category_to_dict(cat)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def delete(self, category_id):
        tenant_id = request.headers.get('X-Tenant-ID', 1, type=int)
        cat = ProductCategory.query.filter_by(id=category_id, tenant_id=tenant_id, deleted_at=None).first()
        if not cat:
            abort(404, message="Category not found")
        db.session.delete(cat)
        db.session.commit()
        return {"message": "Category deleted"}, 204
