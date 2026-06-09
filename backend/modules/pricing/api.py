from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from backend.extensions import db
from backend.models import PriceList, PriceListItem

blp = Blueprint("pricing", __name__, description="Price Lists API")


def pricelist_to_dict(pl):
    return {
        "id": pl.id,
        "tenant_id": pl.tenant_id,
        "code": pl.code,
        "name": pl.name,
        "currency": pl.currency,
        "description": pl.description,
        "is_active": pl.is_active,
        "valid_from": pl.valid_from.isoformat() if pl.valid_from else None,
        "valid_to": pl.valid_to.isoformat() if pl.valid_to else None,
        "created_at": pl.created_at.isoformat() if pl.created_at else None,
        "updated_at": pl.updated_at.isoformat() if pl.updated_at else None,
    }


def item_to_dict(item):
    return {
        "id": item.id,
        "tenant_id": item.tenant_id,
        "price_list_id": item.price_list_id,
        "product_id": item.product_id,
        "price": item.price,
        "max_discount": item.max_discount,
        "min_quantity": item.min_quantity,
        "created_at": item.created_at.isoformat() if item.created_at else None,
        "updated_at": item.updated_at.isoformat() if item.updated_at else None,
    }


@blp.route("/api/v1/price-lists")
class PriceListList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        tenant_id = request.headers.get('X-Tenant-ID', 1, type=int)
        lists = PriceList.query.filter_by(tenant_id=tenant_id, deleted_at=None).order_by(PriceList.code).all()
        result = []
        for pl in lists:
            d = pricelist_to_dict(pl)
            d["items_count"] = PriceListItem.query.filter_by(price_list_id=pl.id).count()
            result.append(d)
        return result

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        tenant_id = request.headers.get('X-Tenant-ID', 1, type=int)
        data = request.get_json() or {}
        if not data.get("code") or not data.get("name"):
            abort(400, message="code and name are required")
        existing = PriceList.query.filter_by(tenant_id=tenant_id, code=data["code"]).first()
        if existing:
            abort(400, message=f"Price list with code '{data['code']}' already exists")
        pl = PriceList(tenant_id=tenant_id, code=data["code"], name=data["name"],
                       currency=data.get("currency", "EUR"), description=data.get("description"),
                       is_active=data.get("is_active", True))
        db.session.add(pl)
        db.session.commit()
        return pricelist_to_dict(pl), 201


@blp.route("/api/v1/price-lists/<int:list_id>")
class PriceListDetail(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, list_id):
        tenant_id = request.headers.get('X-Tenant-ID', 1, type=int)
        pl = PriceList.query.filter_by(id=list_id, tenant_id=tenant_id, deleted_at=None).first()
        if not pl:
            abort(404, message="Price list not found")
        return pricelist_to_dict(pl)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def put(self, list_id):
        tenant_id = request.headers.get('X-Tenant-ID', 1, type=int)
        pl = PriceList.query.filter_by(id=list_id, tenant_id=tenant_id, deleted_at=None).first()
        if not pl:
            abort(404, message="Price list not found")
        data = request.get_json() or {}
        for field in ("code", "name", "currency", "description", "is_active"):
            if field in data:
                setattr(pl, field, data[field])
        db.session.commit()
        return pricelist_to_dict(pl)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def delete(self, list_id):
        tenant_id = request.headers.get('X-Tenant-ID', 1, type=int)
        pl = PriceList.query.filter_by(id=list_id, tenant_id=tenant_id, deleted_at=None).first()
        if not pl:
            abort(404, message="Price list not found")
        PriceListItem.query.filter_by(price_list_id=list_id).delete()
        db.session.delete(pl)
        db.session.commit()
        return {"message": "Deleted"}, 204


@blp.route("/api/v1/price-lists/<int:list_id>/items")
class PriceListItemList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, list_id):
        tenant_id = request.headers.get('X-Tenant-ID', 1, type=int)
        pl = PriceList.query.filter_by(id=list_id, tenant_id=tenant_id, deleted_at=None).first()
        if not pl:
            abort(404, message="Price list not found")
        items = PriceListItem.query.filter_by(price_list_id=list_id).order_by(PriceListItem.product_id).all()
        return [item_to_dict(i) for i in items]

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self, list_id):
        tenant_id = request.headers.get('X-Tenant-ID', 1, type=int)
        pl = PriceList.query.filter_by(id=list_id, tenant_id=tenant_id, deleted_at=None).first()
        if not pl:
            abort(404, message="Price list not found")
        data = request.get_json() or {}
        if not data.get("product_id") or data.get("price") is None:
            abort(400, message="product_id and price are required")
        existing = PriceListItem.query.filter_by(price_list_id=list_id, product_id=data["product_id"]).first()
        if existing:
            abort(400, message="Item already exists in this price list")
        item = PriceListItem(tenant_id=tenant_id, price_list_id=list_id,
                             product_id=data["product_id"], price=float(data["price"]),
                             max_discount=float(data.get("max_discount", 0)),
                             min_quantity=float(data.get("min_quantity", 0)))
        db.session.add(item)
        db.session.commit()
        return item_to_dict(item), 201


@blp.route("/api/v1/price-lists/<int:list_id>/items/<int:item_id>")
class PriceListItemDetail(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def put(self, list_id, item_id):
        tenant_id = request.headers.get('X-Tenant-ID', 1, type=int)
        item = PriceListItem.query.filter_by(id=item_id, price_list_id=list_id, tenant_id=tenant_id).first()
        if not item:
            abort(404, message="Item not found")
        data = request.get_json() or {}
        for field in ("price", "max_discount", "min_quantity"):
            if field in data:
                setattr(item, field, float(data[field]))
        db.session.commit()
        return item_to_dict(item)

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def delete(self, list_id, item_id):
        tenant_id = request.headers.get('X-Tenant-ID', 1, type=int)
        item = PriceListItem.query.filter_by(id=item_id, price_list_id=list_id, tenant_id=tenant_id).first()
        if not item:
            abort(404, message="Item not found")
        db.session.delete(item)
        db.session.commit()
        return {"message": "Deleted"}, 204
