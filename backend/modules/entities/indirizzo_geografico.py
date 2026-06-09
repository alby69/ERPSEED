"""
Endpoint per dati geografici italiani e geocodifica.
Usa il database comuni popolato da geocoded.me (tutti i ~7900 comuni italiani).
Nominatim (OSM) per geocoding stradale.
"""
from flask.views import MethodView
from flask_smorest import Blueprint
from flask import request, jsonify
import requests
import math
from backend.modules.entities.comune import Comune, Regione, Provincia
from backend.extensions import db

geografico_blp = Blueprint(
    "geografico", __name__, url_prefix="/api/v1",
    description="Dati geografici italiani"
)

_comuni_cache = None

def _load_comuni_cache():
    global _comuni_cache
    if _comuni_cache is not None:
        return _comuni_cache
    try:
        comuni = Comune.query.filter(
            Comune.latitudine.isnot(None),
            Comune.longitudine.isnot(None)
        ).all()
        _comuni_cache = [{
            'nome': c.nome.upper(),
            'latitudine': c.latitudine,
            'longitudine': c.longitudine,
            'provincia': c.codice_provincia,
            'regione': c.codice_regione,
            'cap': c.cap
        } for c in comuni]
        return _comuni_cache
    except Exception as e:
        print(f"Error loading comuni from DB: {e}")
        return []

def _clear_comuni_cache():
    global _comuni_cache
    _comuni_cache = None


@geografico_blp.route("/indirizzi/regioni")
class RegioniView(MethodView):
    def get(self):
        regioni = Regione.query.order_by(Regione.nome).all()
        return jsonify([{"codice": r.codice, "nome": r.nome} for r in regioni])


@geografico_blp.route("/indirizzi/province")
class ProvinceView(MethodView):
    def get(self):
        regione = request.args.get("regione", "")
        query = Provincia.query
        if regione:
            query = query.filter_by(codice_regione=regione)
        province = query.order_by(Provincia.nome).all()
        return jsonify([
            {"codice": p.codice, "nome": p.nome, "regione": p.codice_regione}
            for p in province
        ])


@geografico_blp.route("/indirizzi/comuni")
class ComuniView(MethodView):
    def get(self):
        provincia = request.args.get("provincia", "")
        query = Comune.query.order_by(Comune.nome)
        if provincia:
            query = query.filter_by(codice_provincia=provincia)
        comuni = query.limit(500).all()
        return jsonify([c.to_dict() for c in comuni])


@geografico_blp.route("/indirizzi/cerca")
class CercaComune(MethodView):
    def get(self):
        q = request.args.get("q", "")
        if not q or len(q) < 2:
            return jsonify([])

        comuni = Comune.query.filter(
            Comune.nome.ilike(f"%{q}%")
        ).order_by(Comune.nome).limit(20).all()

        return jsonify([{
            "codice": c.codice_istat or "",
            "nome": c.nome,
            "CAP": c.cap or "",
            "provincia": c.codice_provincia or "",
            "regione": c.codice_regione or "",
            "latitudine": c.latitudine,
            "longitudine": c.longitudine,
            "display": f"{c.nome} ({c.codice_provincia})"
        } for c in comuni])


@geografico_blp.route("/indirizzi/geocodifica")
class Geocodifica(MethodView):
    def get(self):
        indirizzo = request.args.get("indirizzo", "")
        if not indirizzo:
            return jsonify({"error": "Indirizzo richiesto"}), 400

        indirizzo_lower = indirizzo.lower().strip()
        has_street = any(
            word in indirizzo_lower
            for word in ['via ', 'viale ', 'piazza ', 'corso ', 'strada ', 'largo ']
        )

        if has_street:
            try:
                resp = requests.get(
                    "https://nominatim.openstreetmap.org/search",
                    params={
                        "q": indirizzo + ", Italia",
                        "format": "json", "limit": 1,
                        "addressdetails": 1, "countrycodes": "it"
                    },
                    headers={"User-Agent": "ERPSeed/1.0"},
                    timeout=10
                )
                resp.raise_for_status()
                data = resp.json()
                if data:
                    r = data[0]
                    return jsonify({
                        "latitudine": float(r.get("lat", 0)),
                        "longitudine": float(r.get("lon", 0)),
                        "indirizzo_formattato": r.get("display_name", ""),
                        "qualita": r.get("importance", 0),
                        "fonte": "nominatim"
                    })
            except Exception:
                pass

        comuni_db = _load_comuni_cache()
        for c in comuni_db:
            if c['nome'].lower() == indirizzo_lower:
                return jsonify({
                    "latitudine": c['latitudine'],
                    "longitudine": c['longitudine'],
                    "indirizzo_formattato": f"{c['nome']}, {c['provincia']}, Italia",
                    "qualita": 1.0, "fonte": "db"
                })

        words = indirizzo_lower.replace(',', ' ').split()
        for c in comuni_db:
            if c['nome'].lower() in words:
                return jsonify({
                    "latitudine": c['latitudine'],
                    "longitudine": c['longitudine'],
                    "indirizzo_formattato": f"{c['nome']}, {c['provincia']}, Italia",
                    "qualita": 0.9, "fonte": "db"
                })

        try:
            resp = requests.get(
                "https://nominatim.openstreetmap.org/search",
                params={
                    "q": indirizzo + ", Italia",
                    "format": "json", "limit": 1,
                    "addressdetails": 1, "countrycodes": "it"
                },
                headers={"User-Agent": "ERPSeed/1.0"},
                timeout=10
            )
            resp.raise_for_status()
            data = resp.json()
            if data:
                r = data[0]
                return jsonify({
                    "latitudine": float(r.get("lat", 0)),
                    "longitudine": float(r.get("lon", 0)),
                    "indirizzo_formattato": r.get("display_name", ""),
                    "qualita": r.get("importance", 0),
                    "fonte": "nominatim"
                })
        except Exception:
            pass

        return jsonify({"error": "Indirizzo non trovato"}), 404


@geografico_blp.route("/indirizzi/geocodifica-inversa")
class GeocodificaInversa(MethodView):
    def get(self):
        lat = request.args.get("lat")
        lon = request.args.get("lon")
        if not lat or not lon:
            return jsonify({"error": "Coordinate richieste"}), 400

        lat_f = float(lat)
        lon_f = float(lon)

        comuni = _load_comuni_cache()
        closest = None
        min_dist = float('inf')
        for c in comuni:
            if c['latitudine'] is None or c['longitudine'] is None:
                continue
            dist = math.hypot(c['latitudine'] - lat_f, c['longitudine'] - lon_f)
            if dist < min_dist:
                min_dist = dist
                closest = c

        if closest and min_dist < 2.0:
            return jsonify({
                "indirizzo": f"{closest['nome']}, {closest['provincia']}, Italia",
                "via": "", "numero": "", "CAP": closest.get("cap", ""),
                "comune": closest['nome'],
                "provincia": closest['provincia'],
                "regione": closest['regione'],
                "nazione": "IT"
            })

        try:
            resp = requests.get(
                "https://nominatim.openstreetmap.org/reverse",
                params={
                    "lat": lat, "lon": lon,
                    "format": "json", "addressdetails": 1, "zoom": 18
                },
                headers={"User-Agent": "ERPSeed/1.0"},
                timeout=10
            )
            resp.raise_for_status()
            data = resp.json()
            if not data:
                return jsonify({"error": "Coordinate non valide"}), 404
            addr = data.get("address", {})
            return jsonify({
                "indirizzo": data.get("display_name", ""),
                "via": addr.get("road", ""),
                "numero": addr.get("house_number", ""),
                "CAP": addr.get("postcode", ""),
                "comune": addr.get("city", addr.get("town", addr.get("village", ""))),
                "provincia": addr.get("county", ""),
                "regione": addr.get("state", ""),
                "nazione": addr.get("country_code", "").upper()
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
