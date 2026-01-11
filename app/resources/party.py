from flask_smorest import Blueprint
from app.models.party import Party
from app.schemas import PartySchema
from app.crud import register_crud_routes

blp = Blueprint("parties", __name__, description="Operations on parties (Customers/Suppliers)")

# Genera automaticamente tutte le rotte CRUD per i Party
register_crud_routes(
    blp, 
    Party, 
    PartySchema, 
    url_prefix="/parties", 
    search_fields=["name", "email", "vat_number", "fiscal_code"],
    csv_fields=["id", "name", "type", "email", "phone", "vat_number", "fiscal_code"] # Ordine e selezione personalizzati
)