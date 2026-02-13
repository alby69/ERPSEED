from flask_smorest import Blueprint
from backend.models import Product
from app.schemas import ProductSchema
from backend.crud import register_crud_routes

blp = Blueprint("products", __name__, description="Operations on products")

register_crud_routes(
    blp,
    Product,
    ProductSchema,
    url_prefix="/products",
    search_fields=["name", "code", "description"], 
    # multipart=True, # Enable file uploads if needed
    csv_fields=["id", "code", "name", "description", "unit_price"],
    # eager_load=["supplier"] # Eager load supplier data if there is a relation
)