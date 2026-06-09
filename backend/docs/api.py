from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from .service import LogisticsService
from marshmallow import Schema, fields

api = Blueprint('logistics', __name__, url_prefix='/api/v1/logistics', description='Servizi Logistici e Routing')

class RouteRequestSchema(Schema):
    start = fields.List(fields.Float(), required=True, description="[lng, lat] di partenza")
    end = fields.List(fields.Float(), required=True, description="[lng, lat] di arrivo")
    profile = fields.String(dump_default='driving-car')

class GeocodeRequestSchema(Schema):
    address = fields.String(required=True)

@api.route('/directions')
class Directions(MethodView):
    @jwt_required()
    @api.arguments(RouteRequestSchema)
    def post(self, args):
        """Calcola percorso e distanza tra due punti."""
        service = LogisticsService()
        try:
            return service.get_directions(args['start'], args['end'], args.get('profile'))
        except Exception as e:
            abort(500, message=str(e))

@api.route('/matrix')
class DistanceMatrix(MethodView):
    @jwt_required()
    def post(self):
        """Calcola matrice di distanze (molti-a-molti)."""
        data = request.json
        service = LogisticsService()
        try:
            return service.get_matrix(data.get('locations'), data.get('profile', 'driving-car'))
        except Exception as e:
            abort(500, message=str(e))

@api.route('/geocode')
class Geocode(MethodView):
    @jwt_required()
    @api.arguments(GeocodeRequestSchema, location='query')
    def get(self, args):
        """Geocoding: da indirizzo a coordinate."""
        service = LogisticsService()
        try:
            result = service.geocode(args['address'])
            if not result:
                abort(404, message="Indirizzo non trovato")
            return result
        except Exception as e:
            abort(500, message=str(e))