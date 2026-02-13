from flask_smorest import Blueprint
from backend.models import Party
from app.schemas import PartySchema
from backend.crud import register_crud_routes

blp = Blueprint("parties", __name__, description="Operations on parties (Customers/Suppliers)")

# Automatically generate all CRUD routes for Parties
register_crud_routes(
    blp, 
    Party, 
    PartySchema, 
    url_prefix="/parties", 
    search_fields=["name", "email", "vat_number", "fiscal_code"],
    csv_fields=["id", "name", "party_type", "email", "phone", "vat_number", "fiscal_code"] # Custom order and selection
)