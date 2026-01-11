from flask_smorest import Blueprint
from app.models.product import Product
from app.schemas import ProductSchema
from app.crud import register_crud_routes

blp = Blueprint("products", __name__, description="Operations on products")

register_crud_routes(
    blp,
    Product,
    ProductSchema,
    url_prefix="/products",
    search_fields=["name", "sku", "description", "supplier.name"], # Cerca anche per fornitore
    multipart=True, # Abilita upload file
    csv_fields=["id", "sku", "name", "price", "supplier_id"],
    eager_load=["supplier"] # Carica i dati del fornitore
)