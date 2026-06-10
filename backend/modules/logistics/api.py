from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from marshmallow import Schema, fields

from backend.services.logistics_service import LogisticsService

logistics_blp = Blueprint(
    "logistics",
    __name__,
    url_prefix="/api/v1/logistics",
    description="Servizi Logistici — routing, distanze e geocoding",
)


class RouteRequestSchema(Schema):
    start = fields.List(
        fields.Float(),
        required=True,
        metadata={"description": "[lng, lat] partenza"},
    )
    end = fields.List(
        fields.Float(),
        required=True,
        metadata={"description": "[lng, lat] arrivo"},
    )
    profile = fields.String(dump_default="driving-car")


class AddressRouteSchema(Schema):
    start_address_id = fields.Integer(
        required=True,
        metadata={"description": "ID Indirizzo partenza"},
    )
    end_address_id = fields.Integer(
        required=True,
        metadata={"description": "ID Indirizzo arrivo"},
    )
    profile = fields.String(dump_default="driving-car")


class MatrixRequestSchema(Schema):
    locations = fields.List(
        fields.List(fields.Float()),
        required=True,
        metadata={"description": "[[lng, lat], ...]"},
    )
    profile = fields.String(dump_default="driving-car")


@logistics_blp.route("/directions")
class Directions(MethodView):
    @jwt_required()
    @logistics_blp.arguments(RouteRequestSchema)
    def post(self, args):
        """Calcola percorso tra due coordinate [lng, lat]."""
        try:
            svc = LogisticsService()
            return svc.get_directions(args["start"], args["end"], args.get("profile"))
        except Exception as e:
            abort(500, message=str(e))


@logistics_blp.route("/directions-by-address")
class DirectionsByAddress(MethodView):
    @jwt_required()
    @logistics_blp.arguments(AddressRouteSchema)
    def post(self, args):
        """Calcola percorso tra due indirizzi salvati (per ID)."""
        try:
            from backend.modules.entities.indirizzo import Indirizzo
            from backend.extensions import db

            start = db.session.get(Indirizzo, args["start_address_id"])
            end = db.session.get(Indirizzo, args["end_address_id"])
            if not start or not end:
                abort(404, message="Indirizzo non trovato")
            if not start.longitudine or not start.latitudine:
                abort(
                    400, message=f"Indirizzo '{start.denominazione}' non ha coordinate"
                )
            if not end.longitudine or not end.latitudine:
                abort(400, message=f"Indirizzo '{end.denominazione}' non ha coordinate")

            svc = LogisticsService()
            result = svc.get_directions(
                [start.longitudine, start.latitudine],
                [end.longitudine, end.latitudine],
                args.get("profile"),
            )
            result["start_address"] = start.to_dict()
            result["end_address"] = end.to_dict()
            return result
        except Exception as e:
            abort(500, message=str(e))


@logistics_blp.route("/matrix")
class DistanceMatrix(MethodView):
    @jwt_required()
    @logistics_blp.arguments(MatrixRequestSchema)
    def post(self, args):
        """Calcola matrice distanze moltimodale."""
        try:
            svc = LogisticsService()
            return svc.get_matrix(args["locations"], args.get("profile"))
        except Exception as e:
            abort(500, message=str(e))


@logistics_blp.route("/geocode")
class Geocode(MethodView):
    @jwt_required()
    def get(self):
        """Geocoding via OpenRouteService."""
        address = request.args.get("address", "")
        if not address:
            abort(400, message="Parametro 'address' richiesto")
        try:
            svc = LogisticsService()
            result = svc.geocode(address)
            if not result:
                abort(404, message="Indirizzo non trovato")
            return result
        except Exception as e:
            abort(500, message=str(e))
