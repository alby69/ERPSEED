from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from .models import Product
from .extensions import db
from .schemas import ProductSchema
from .utils import apply_filters, paginate, apply_sorting

blp = Blueprint("products", __name__, description="Operations on products")

@blp.route("/products")
class ProductList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, ProductSchema(many=True))
    def get(self):
        """Lista tutti i prodotti"""
        query = Product.query
        query = apply_filters(query, Product, ['name', 'code', 'description'])
        query = apply_sorting(query, Product)
        items, headers = paginate(query)
        return items, 200, headers

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(ProductSchema)
    @blp.response(201, ProductSchema)
    def post(self, product_data):
        """Crea un nuovo prodotto"""
        # product_data is already a Product instance due to load_instance=True in ProductSchema
        if product_data.code and Product.query.filter_by(code=product_data.code).first():
            abort(409, message="Product code already exists")
            
        db.session.add(product_data)
        db.session.commit()
        return product_data