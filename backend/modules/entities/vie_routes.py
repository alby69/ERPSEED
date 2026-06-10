"""API per ricerca strade — cache locale + Nominatim fallback."""

from urllib.request import urlopen, Request
from urllib.parse import urlencode
import json as json_lib
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from marshmallow import Schema, fields

from backend.extensions import db
from backend.modules.entities.indirizzo import Via

vie_blp = Blueprint(
    "vie",
    __name__,
    url_prefix="/api/v1/vie",
    description="Ricerca strade per comune",
)

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"


class ViaSearchSchema(Schema):
    comune_id = fields.Integer(required=True, metadata={"description": "ID comune"})
    q = fields.String(
        required=True, metadata={"description": "Query parziale nome via"}
    )


def search_nominatim(comune_nome, query, limit=20):
    """Cerca strade su Nominatim e restituisce risultati grezzi.
    Usa urllib per evitare conflitti con eventlet/gevent monkey patch.
    """
    params = {
        "format": "json",
        "q": f"{query}, {comune_nome}, Italia",
        "countrycodes": "IT",
        "limit": limit,
        "addressdetails": 1,
    }
    url = f"{NOMINATIM_URL}?{urlencode(params)}"
    try:
        req = Request(url, headers={"User-Agent": "ERPSeed/1.0"})
        with urlopen(req, timeout=8) as resp:
            return json_lib.loads(resp.read().decode())
    except Exception:
        return []


@vie_blp.route("/")
class ViaSearch(MethodView):
    @jwt_required()
    @vie_blp.arguments(ViaSearchSchema, location="query")
    def get(self, args):
        """Cerca strade per comune (cache locale + Nominatim)."""
        comune_id = args["comune_id"]
        q = args["q"].strip()
        if len(q) < 2:
            abort(400, message="Inserisci almeno 2 caratteri")

        from backend.modules.entities.comune import Comune

        comune = db.session.get(Comune, comune_id)
        if not comune:
            abort(404, message="Comune non trovato")

        results = []

        # 1. Cerca nella cache locale
        locali = (
            Via.query.filter(Via.comune_id == comune_id, Via.nome.ilike(f"%{q}%"))
            .order_by(Via.nome)
            .limit(20)
            .all()
        )
        seen = set()
        for v in locali:
            results.append(
                {
                    "id": v.id,
                    "nome": v.nome,
                    "comune_id": v.comune_id,
                    "source": "cache",
                }
            )
            seen.add(v.nome.lower())

        # 2. Se pochi risultati locali, interroga Nominatim
        if len(locali) < 5:
            nomi_results = search_nominatim(comune.nome, q)
            for nr in nomi_results:
                road = (nr.get("address") or {}).get("road", "")
                if road and road.lower() not in seen:
                    # Salva in cache locale
                    try:
                        nuova = Via(nome=road, comune_id=comune_id)
                        db.session.add(nuova)
                        db.session.commit()
                        results.append(
                            {
                                "id": nuova.id,
                                "nome": road,
                                "comune_id": comune_id,
                                "source": "nominatim",
                            }
                        )
                        seen.add(road.lower())
                    except Exception:
                        db.session.rollback()

        return results[:20]


@vie_blp.route("/bulk")
class ViaBulkCache(MethodView):
    @jwt_required()
    def post(self):
        """Pre-carica tutte le strade di un comune (uso esplicito)."""
        comune_id = request.args.get("comune_id", type=int)
        if not comune_id:
            abort(400, message="comune_id richiesto")

        from backend.modules.entities.comune import Comune

        comune = db.session.get(Comune, comune_id)
        if not comune:
            abort(404, message="Comune non trovato")

        # Carica fino a 50 strade da Nominatim per popolare la cache
        params = {
            "format": "json",
            "q": f"{comune.nome}, Italia",
            "countrycodes": "IT",
            "limit": 50,
            "addressdetails": 1,
        }
        url = f"{NOMINATIM_URL}?{urlencode(params)}"
        try:
            req = Request(url, headers={"User-Agent": "ERPSeed/1.0"})
            with urlopen(req, timeout=10) as resp:
                items = json_lib.loads(resp.read().decode())
        except Exception as e:
            abort(502, message=f"Errore Nominatim: {e}")

        count = 0
        for item in items:
            road = (item.get("address") or {}).get("road", "")
            if not road:
                continue
            existing = Via.query.filter_by(nome=road, comune_id=comune_id).first()
            if not existing:
                try:
                    db.session.add(Via(nome=road, comune_id=comune_id))
                    count += 1
                except Exception:
                    db.session.rollback()
        db.session.commit()

        return {"cached": count, "comune_id": comune_id}
