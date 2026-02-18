from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from .models import Party
from .extensions import db
from .schemas import PartySchema
from .utils import apply_filters, paginate, apply_sorting, apply_date_filters
from .core.services.tenant_context import TenantContext

blp = Blueprint("parties", __name__, description="Operations on parties (Customers/Suppliers)")

def get_tenant_query(model):
    """Get query filtered by current tenant."""
    tenant_id = TenantContext.get_tenant_id()
    if tenant_id is None:
        abort(403, message="Tenant context not found")
    return model.query.filter_by(tenant_id=tenant_id)

@blp.route("/parties")
class PartyList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, PartySchema(many=True))
    def get(self):
        """List all customers/suppliers"""
        query = get_tenant_query(Party)
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
        tenant_id = TenantContext.get_tenant_id()
        if tenant_id is None:
            abort(403, message="Tenant context not found")
        
        party_data.tenant_id = tenant_id
        
        if party_data.vat_number:
            existing = Party.query.filter_by(tenant_id=tenant_id, vat_number=party_data.vat_number).first()
            if existing:
                abort(409, message=f"Party with VAT number '{party_data.vat_number}' already exists.")
        if party_data.email:
            existing = Party.query.filter_by(tenant_id=tenant_id, email=party_data.email).first()
            if existing:
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
        query = get_tenant_query(Party)
        party = query.get(party_id)
        if not party:
            abort(404, message="Party not found")
        return party
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(PartySchema)
    @blp.response(200, PartySchema)
    def put(self, party_data, party_id):
        """Update a customer/supplier"""
        query = get_tenant_query(Party)
        party = query.get(party_id)
        if not party:
            abort(404, message="Party not found")
        
        for key, value in party_data.items():
            if hasattr(party, key):
                setattr(party, key, value)
        
        db.session.commit()
        return party
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(204)
    def delete(self, party_id):
        """Delete a customer/supplier"""
        query = get_tenant_query(Party)
        party = query.get(party_id)
        if not party:
            abort(404, message="Party not found")
        
        db.session.delete(party)
        db.session.commit()
        return '', 204