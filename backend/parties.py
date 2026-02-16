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
        """List all customers/suppliers"""
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
        """Create a new customer/supplier"""
        # party_data is already a Party instance due to load_instance=True in PartySchema
        if party_data.vat_number and Party.query.filter_by(vat_number=party_data.vat_number).first():
            abort(409, message=f"Party with VAT number '{party_data.vat_number}' already exists.")
        if party_data.email and Party.query.filter_by(email=party_data.email).first():
            abort(409, message=f"Party with email '{party_data.email}' already exists.")

        db.session.add(party_data)
        db.session.commit()
        return party_data

@blp.route("/parties/<int:party_id>")
class PartyResource(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, PartySchema)
    def get(self, party_id):
        """Customer/supplier detail"""
        return Party.query.get_or_404(party_id)