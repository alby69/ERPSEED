from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask import request
from backend.extensions import db
from backend.modules.geografia.nazione import Nazione
from backend.modules.entities.comune import Regione, Provincia, Comune

nazioni_blp = Blueprint(
    "nazioni", __name__,
    description="Nazioni (Geography module)"
)

regioni_blp = Blueprint(
    "regioni_geo", __name__,
    description="Regioni (Geography module)"
)

province_blp = Blueprint(
    "province_geo", __name__,
    description="Province (Geography module)"
)

comuni_geo_blp = Blueprint(
    "comuni_geo", __name__,
    description="Comuni (Geography module)"
)


# ---- NAZIONI ----

@nazioni_blp.route("/nazioni")
class NazioniListAPI(MethodView):
    def get(self):
        q = request.args.get("q", "")
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 50, type=int)
        query = Nazione.query
        if q:
            query = query.filter(Nazione.nome.ilike(f"%{q}%") | Nazione.nome_inglese.ilike(f"%{q}%"))
        query = query.order_by(Nazione.nome)
        pagination = query.paginate(page=page, per_page=min(per_page, 100), error_out=False)
        return {
            "items": [n.to_dict() for n in pagination.items],
            "total": pagination.total,
            "page": pagination.page,
            "pages": pagination.pages,
        }

    @nazioni_blp.doc(security=[{"jwt": []}])
    def post(self):
        data = request.get_json()
        if not data or not data.get("codice_iso"):
            abort(400, message="codice_iso richiesto")
        if Nazione.query.get(data["codice_iso"]):
            abort(409, message="Nazione già esistente")
        n = Nazione(**data)
        db.session.add(n)
        db.session.commit()
        return n.to_dict(), 201


@nazioni_blp.route("/nazioni/<string:codice_iso>")
class NazioneAPI(MethodView):
    def get(self, codice_iso):
        n = Nazione.query.get_or_404(codice_iso)
        return n.to_dict()

    @nazioni_blp.doc(security=[{"jwt": []}])
    def put(self, codice_iso):
        n = Nazione.query.get_or_404(codice_iso)
        data = request.get_json()
        for key in ["nome", "nome_inglese", "continente", "nazionalita", "valuta", "prefisso_telefonico"]:
            if key in data:
                setattr(n, key, data[key])
        db.session.commit()
        return n.to_dict()

    @nazioni_blp.doc(security=[{"jwt": []}])
    def delete(self, codice_iso):
        n = Nazione.query.get_or_404(codice_iso)
        db.session.delete(n)
        db.session.commit()
        return "", 204


# ---- REGIONI ----

@regioni_blp.route("/regioni")
class RegioniListAPI(MethodView):
    def get(self):
        q = request.args.get("q", "")
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 50, type=int)
        query = Regione.query
        if q:
            query = query.filter(Regione.nome.ilike(f"%{q}%"))
        query = query.order_by(Regione.nome)
        pagination = query.paginate(page=page, per_page=min(per_page, 100), error_out=False)
        return {
            "items": [r.to_dict() for r in pagination.items],
            "total": pagination.total,
            "page": pagination.page,
            "pages": pagination.pages,
        }


@regioni_blp.route("/regioni/<string:codice>")
class RegioneAPI(MethodView):
    def get(self, codice):
        r = Regione.query.filter_by(codice=codice).first_or_404()
        return r.to_dict()


# ---- PROVINCE ----

@province_blp.route("/province")
class ProvinceListAPI(MethodView):
    def get(self):
        q = request.args.get("q", "")
        regione = request.args.get("regione")
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 50, type=int)
        query = Provincia.query
        if q:
            query = query.filter(Provincia.nome.ilike(f"%{q}%"))
        if regione:
            query = query.filter_by(codice_regione=regione)
        query = query.order_by(Provincia.nome)
        pagination = query.paginate(page=page, per_page=min(per_page, 100), error_out=False)
        return {
            "items": [p.to_dict() for p in pagination.items],
            "total": pagination.total,
            "page": pagination.page,
            "pages": pagination.pages,
        }


# ---- COMUNI (read-only) ----

@comuni_geo_blp.route("/comuni-geo")
class ComuniGeoListAPI(MethodView):
    def get(self):
        q = request.args.get("q", "")
        provincia = request.args.get("provincia")
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 50, type=int)
        query = Comune.query
        if q:
            query = query.filter(Comune.nome.ilike(f"%{q}%"))
        if provincia:
            query = query.filter_by(codice_provincia=provincia)
        query = query.order_by(Comune.nome)
        pagination = query.paginate(page=page, per_page=min(per_page, 100), error_out=False)
        return {
            "items": [c.to_dict() for c in pagination.items],
            "total": pagination.total,
            "page": pagination.page,
            "pages": pagination.pages,
        }
