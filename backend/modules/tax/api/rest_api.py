from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity

from backend.modules.tax import get_tax_service

blp = Blueprint("tax_api", __name__, url_prefix="/api/v1/tax-rates", description="Tax Rates API")


def get_service():
    return get_tax_service()


@blp.route("")
class TaxRateList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        tenant_id = request.headers.get('X-Tenant-ID', 1, type=int)
        userId = get_jwt_identity()

        result = get_service().execute({
            "command": "ListTaxRates",
            "tenant_id": tenant_id,
            "userId": userId,
            "pagination": {
                "page": request.args.get('page', 1, type=int),
                "per_page": request.args.get('per_page', 20, type=int)
            }
        })

        if not result.get("success"):
            abort(400, message=result.get("error", "Failed to list tax rates"))

        return result.get("data", {})

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        tenant_id = request.headers.get('X-Tenant-ID', 1, type=int)
        userId = get_jwt_identity()
        data = request.get_json()

        result = get_service().execute({
            "command": "CreateTaxRate",
            "tenant_id": tenant_id,
            "userId": userId,
            **data
        })

        if not result.get("success"):
            abort(400, message=result.get("error", "Failed to create tax rate"))

        return result.get("data", {}), 201


@blp.route("/<int:tax_rate_id>")
class TaxRateDetail(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, tax_rate_id):
        tenant_id = request.headers.get('X-Tenant-ID', 1, type=int)
        userId = get_jwt_identity()

        result = get_service().execute({
            "command": "GetTaxRate",
            "tenant_id": tenant_id,
            "userId": userId,
            "entity_id": tax_rate_id
        })

        if not result.get("success"):
            abort(404, message=result.get("error", "Tax rate not found"))

        return result.get("data", {})

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def put(self, tax_rate_id):
        tenant_id = request.headers.get('X-Tenant-ID', 1, type=int)
        userId = get_jwt_identity()
        data = request.get_json()

        result = get_service().execute({
            "command": "UpdateTaxRate",
            "tenant_id": tenant_id,
            "userId": userId,
            "entity_id": tax_rate_id,
            **data
        })

        if not result.get("success"):
            abort(404, message=result.get("error", "Tax rate not found"))

        return result.get("data", {})

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def delete(self, tax_rate_id):
        tenant_id = request.headers.get('X-Tenant-ID', 1, type=int)
        userId = get_jwt_identity()

        result = get_service().execute({
            "command": "DeleteTaxRate",
            "tenant_id": tenant_id,
            "userId": userId,
            "entity_id": tax_rate_id
        })

        if not result.get("success"):
            abort(404, message=result.get("error", "Tax rate not found"))

        return {"message": "Tax rate deleted"}, 204
