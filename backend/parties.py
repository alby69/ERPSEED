from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from .models import Party
from .extensions import db
from .schemas import PartySchema
from .utils import apply_filters, paginate, apply_sorting, apply_date_filters

blp = Blueprint("parties", __name__, description="Operations on parties (Customers/Suppliers)")

@blp.route("/parties")
class PartyList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, PartySchema(many=True))
    def get(self):
        """Lista tutti i clienti/fornitori"""
        query = Party.query
        query = apply_filters(query, Party, ['name', 'email', 'vat_number'])
        query = apply_date_filters(query, Party)
        query = apply_sorting(query, Party)
        items, headers = paginate(query)
        return items, 200, headers

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(PartySchema)
    @blp.response(201, PartySchema)
    def post(self, party_data):
        """Crea un nuovo cliente/fornitore"""
        party = Party(**party_data)
        db.session.add(party)
        db.session.commit()
        return party

@blp.route("/parties/<int:party_id>")
class PartyResource(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, PartySchema)
    def get(self, party_id):
        """Dettaglio cliente/fornitore"""
        return Party.query.get_or_404(party_id)