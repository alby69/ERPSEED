from flask import Blueprint, request, jsonify
from flask.views import MethodView
from flask_jwt_extended import jwt_required
from datetime import datetime

geographic_bp = Blueprint('geographic', __name__, url_prefix='/api/geographic')


REGIONI = [
    {"codice": "01", "nome": "Abruzzo"},
    {"codice": "02", "nome": "Basilicata"},
    {"codice": "03", "nome": "Calabria"},
    {"codice": "04", "nome": "Campania"},
    {"codice": "05", "nome": "Emilia-Romagna"},
    {"codice": "06", "nome": "Friuli-Venezia Giulia"},
    {"codice": "07", "nome": "Lazio"},
    {"codice": "08", "nome": "Liguria"},
    {"codice": "09", "nome": "Lombardia"},
    {"codice": "10", "nome": "Marche"},
    {"codice": "11", "nome": "Molise"},
    {"codice": "12", "nome": "Piemonte"},
    {"codice": "13", "nome": "Puglia"},
    {"codice": "14", "nome": "Sardegna"},
    {"codice": "15", "nome": "Sicilia"},
    {"codice": "16", "nome": "Toscana"},
    {"codice": "17", "nome": "Trentino-Alto Adige"},
    {"codice": "18", "nome": "Umbria"},
    {"codice": "19", "nome": "Valle d'Aosta"},
    {"codice": "20", "nome": "Veneto"}
]

PROVINCE = [
    {"codice": "AG", "nome": "Agrigento", "regione": "15"},
    {"codice": "AL", "nome": "Alessandria", "regione": "12"},
    {"codice": "AN", "nome": "Ancona", "regione": "10"},
    {"codice": "AO", "nome": "Aosta", "regione": "19"},
    {"codice": "AP", "nome": "Ascoli Piceno", "regione": "10"},
    {"codice": "AQ", "nome": "L'Aquila", "regione": "01"},
    {"codice": "AR", "nome": "Arezzo", "regione": "16"},
    {"codice": "AT", "nome": "Asti", "regione": "12"},
    {"codice": "AV", "nome": "Avellino", "regione": "04"},
    {"codice": "BA", "nome": "Bari", "regione": "13"},
    {"codice": "BG", "nome": "Bergamo", "regione": "09"},
    {"codice": "BI", "nome": "Biella", "regione": "12"},
    {"codice": "BL", "nome": "Belluno", "regione": "20"},
    {"codice": "BN", "nome": "Benevento", "regione": "04"},
    {"codice": "BO", "nome": "Bologna", "regione": "05"},
    {"codice": "BR", "nome": "Brindisi", "regione": "13"},
    {"codice": "BS", "nome": "Brescia", "regione": "09"},
    {"codice": "BT", "nome": "Barletta-Andria-Trani", "regione": "13"},
    {"codice": "BZ", "nome": "Bolzano", "regione": "17"},
    {"codice": "CA", "nome": "Cagliari", "regione": "14"},
    {"codice": "CB", "nome": "Campobasso", "regione": "11"},
    {"codice": "CE", "nome": "Caserta", "regione": "04"},
    {"codice": "CH", "nome": "Chieti", "regione": "01"},
    {"codice": "CL", "nome": "Caltanissetta", "regione": "15"},
    {"codice": "CN", "nome": "Cuneo", "regione": "12"},
    {"codice": "CO", "nome": "Como", "regione": "09"},
    {"codice": "CR", "nome": "Cremona", "regione": "09"},
    {"codice": "CS", "nome": "Cosenza", "regione": "03"},
    {"codice": "CT", "nome": "Catania", "regione": "15"},
    {"codice": "CZ", "nome": "Catanzaro", "regione": "03"},
    {"codice": "EN", "nome": "Enna", "regione": "15"},
    {"codice": "FE", "nome": "Ferrara", "regione": "05"},
    {"codice": "FG", "nome": "Foggia", "regione": "13"},
    {"codice": "FI", "nome": "Firenze", "regione": "16"},
    {"codice": "FM", "nome": "Fermo", "regione": "10"},
    {"codice": "FO", "nome": "Forlì-Cesena", "regione": "05"},
    {"codice": "FR", "nome": "Frosinone", "regione": "07"},
    {"codice": "GE", "nome": "Genova", "regione": "08"},
    {"codice": "GO", "nome": "Gorizia", "regione": "06"},
    {"codice": "GR", "nome": "Grosseto", "regione": "16"},
    {"codice": "IM", "nome": "Imperia", "regione": "08"},
    {"codice": "IS", "nome": "Isernia", "regione": "11"},
    {"codice": "KR", "nome": "Crotone", "regione": "03"},
    {"codice": "LC", "nome": "Lecco", "regione": "09"},
    {"codice": "LE", "nome": "Lecce", "regione": "13"},
    {"codice": "LI", "nome": "Livorno", "regione": "16"},
    {"codice": "LO", "nome": "Lodi", "regione": "09"},
    {"codice": "LT", "nome": "Latina", "regione": "07"},
    {"codice": "LU", "nome": "Lucca", "regione": "16"},
    {"codice": "MB", "nome": "Monza e Brianza", "regione": "09"},
    {"codice": "MC", "nome": "Macerata", "regione": "10"},
    {"codice": "ME", "nome": "Messina", "regione": "15"},
    {"codice": "MI", "nome": "Milano", "regione": "09"},
    {"codice": "MN", "nome": "Mantova", "regione": "09"},
    {"codice": "MO", "nome": "Modena", "regione": "05"},
    {"codice": "MS", "nome": "Massa-Carrara", "regione": "16"},
    {"codice": "MT", "nome": "Matera", "regione": "02"},
    {"codice": "NA", "nome": "Napoli", "regione": "04"},
    {"codice": "NO", "nome": "Novara", "regione": "12"},
    {"codice": "NU", "nome": "Nuoro", "regione": "14"},
    {"codice": "OR", "nome": "Oristano", "regione": "14"},
    {"codice": "PA", "nome": "Palermo", "regione": "15"},
    {"codice": "PC", "nome": "Piacenza", "regione": "05"},
    {"codice": "PD", "nome": "Padova", "regione": "20"},
    {"codice": "PE", "nome": "Pescara", "regione": "01"},
    {"codice": "PG", "nome": "Perugia", "regione": "18"},
    {"codice": "PI", "nome": "Pisa", "regione": "16"},
    {"codice": "PN", "nome": "Pordenone", "regione": "06"},
    {"codice": "PO", "nome": "Prato", "regione": "16"},
    {"codice": "PR", "nome": "Parma", "regione": "05"},
    {"codice": "PT", "nome": "Pistoia", "regione": "16"},
    {"codice": "PU", "nome": "Pesaro e Urbino", "regione": "10"},
    {"codice": "PV", "nome": "Pavia", "regione": "09"},
    {"codice": "PZ", "nome": "Potenza", "regione": "02"},
    {"codice": "RA", "nome": "Ravenna", "regione": "05"},
    {"codice": "RC", "nome": "Reggio Calabria", "regione": "03"},
    {"codice": "RE", "nome": "Reggio Emilia", "regione": "05"},
    {"codice": "RG", "nome": "Ragusa", "regione": "15"},
    {"codice": "RI", "nome": "Rieti", "regione": "07"},
    {"codice": "RM", "nome": "Roma", "regione": "07"},
    {"codice": "RN", "nome": "Rimini", "regione": "05"},
    {"codice": "RO", "nome": "Rovigo", "regione": "20"},
    {"codice": "SA", "nome": "Salerno", "regione": "04"},
    {"codice": "SI", "nome": "Siena", "regione": "16"},
    {"codice": "SO", "nome": "Sondrio", "regione": "09"},
    {"codice": "SP", "nome": "La Spezia", "regione": "08"},
    {"codice": "SR", "nome": "Siracusa", "regione": "15"},
    {"codice": "SS", "nome": "Sassari", "regione": "14"},
    {"codice": "SV", "nome": "Savona", "regione": "08"},
    {"codice": "TA", "nome": "Taranto", "regione": "13"},
    {"codice": "TE", "nome": "Teramo", "regione": "01"},
    {"codice": "TN", "nome": "Trento", "regione": "17"},
    {"codice": "TO", "nome": "Torino", "regione": "12"},
    {"codice": "TP", "nome": "Trapani", "regione": "15"},
    {"codice": "TR", "nome": "Terni", "regione": "18"},
    {"codice": "TS", "nome": "Trieste", "regione": "06"},
    {"codice": "TV", "nome": "Treviso", "regione": "20"},
    {"codice": "UD", "nome": "Udine", "regione": "06"},
    {"codice": "VA", "nome": "Varese", "regione": "09"},
    {"codice": "VB", "nome": "Verbano-Cusio-Ossola", "regione": "12"},
    {"codice": "VC", "nome": "Vercelli", "regione": "12"},
    {"codice": "VE", "nome": "Venezia", "regione": "20"},
    {"codice": "VI", "nome": "Vicenza", "regione": "20"},
    {"codice": "VR", "nome": "Verona", "regione": "20"},
    {"codice": "VT", "nome": "Viterbo", "regione": "07"},
    {"codice": "VV", "nome": "Vibo Valentia", "regione": "03"},
]

COMUNI = [
    {"codice": "001001", "nome": "Roma", "CAP": "00100", "provincia": "RM", "regione": "Lazio", "latitudine": 41.9028, "longitudine": 12.4964},
    {"codice": "015001", "nome": "Milano", "CAP": "20100", "provincia": "MI", "regione": "Lombardia", "latitudine": 45.4642, "longitudine": 9.1900},
    {"codice": "063001", "nome": "Napoli", "CAP": "80100", "provincia": "NA", "regione": "Campania", "latitudine": 40.8518, "longitudine": 14.2681},
    {"codice": "048001", "nome": "Torino", "CAP": "10100", "provincia": "TO", "regione": "Piemonte", "latitudine": 45.0703, "longitudine": 7.6869},
    {"codice": "058001", "nome": "Palermo", "CAP": "90100", "provincia": "PA", "regione": "Sicilia", "latitudine": 38.1157, "longitudine": 13.3615},
    {"codice": "027001", "nome": "Genova", "CAP": "16100", "provincia": "GE", "regione": "Liguria", "latitudine": 44.4056, "longitudine": 8.9463},
    {"codice": "025001", "nome": "Bologna", "CAP": "40100", "provincia": "BO", "regione": "Emilia-Romagna", "latitudine": 44.4949, "longitudine": 11.3426},
    {"codice": "033001", "nome": "Firenze", "CAP": "50100", "provincia": "FI", "regione": "Toscana", "latitudine": 43.7696, "longitudine": 11.2558},
    {"codice": "082001", "nome": "Bari", "CAP": "70100", "provincia": "BA", "regione": "Puglia", "latitudine": 41.1171, "longitudine": 16.8543},
    {"codice": "057001", "nome": "Catania", "CAP": "95100", "provincia": "CT", "regione": "Sicilia", "latitudine": 37.5079, "longitudine": 15.0833},
    {"codice": "069001", "nome": "Venezia", "CAP": "30100", "provincia": "VE", "regione": "Veneto", "latitudine": 45.4408, "longitudine": 12.3155},
    {"codice": "055001", "nome": "Verona", "CAP": "37100", "provincia": "VR", "regione": "Veneto", "latitudine": 45.4429, "longitudine": 10.9981},
    {"codice": "062001", "nome": "Messina", "CAP": "98100", "provincia": "ME", "regione": "Sicilia", "latitudine": 38.1938, "longitudine": 15.5540},
    {"codice": "043001", "nome": "Padova", "CAP": "35100", "provincia": "PD", "regione": "Veneto", "latitudine": 45.4068, "longitudine": 11.8765},
    {"codice": "028001", "nome": "Trieste", "CAP": "34100", "provincia": "TS", "regione": "Friuli-Venezia Giulia", "latitudine": 45.6495, "longitudine": 13.7768},
    {"codice": "070001", "nome": "Brescia", "CAP": "25100", "provincia": "BS", "regione": "Lombardia", "latitudine": 45.5416, "longitudine": 10.2118},
    {"codice": "050001", "nome": "Taranto", "CAP": "74100", "provincia": "TA", "regione": "Puglia", "latitudine": 40.4643, "longitudine": 17.2471},
    {"codice": "054001", "nome": "Prato", "CAP": "59100", "provincia": "PO", "regione": "Toscana", "latitudine": 43.8777, "longitudine": 11.1022},
    {"codice": "068001", "nome": "Reggio Calabria", "CAP": "89100", "provincia": "RC", "regione": "Calabria", "latitudine": 38.1036, "longitudine": 15.6462},
    {"codice": "034001", "nome": "Modena", "CAP": "41100", "provincia": "MO", "regione": "Emilia-Romagna", "latitudine": 44.6471, "longitudine": 10.9254},
    {"codice": "029001", "nome": "Parma", "CAP": "43100", "provincia": "PR", "regione": "Emilia-Romagna", "latitudine": 44.8015, "longitudine": 10.3279},
    {"codice": "047001", "nome": "Reggio Emilia", "CAP": "42100", "provincia": "RE", "regione": "Emilia-Romagna", "latitudine": 44.6989, "longitudine": 10.6314},
    {"codice": "040001", "nome": "Perugia", "CAP": "06100", "provincia": "PG", "regione": "Umbria", "latitudine": 43.1107, "longitudine": 12.3908},
    {"codice": "001002", "nome": "Latina", "CAP": "04100", "provincia": "LT", "regione": "Lazio", "latitudine": 41.5316, "longitudine": 12.8981},
    {"codice": "001003", "nome": "Frosinone", "CAP": "03100", "provincia": "FR", "regione": "Lazio", "latitudine": 41.6340, "longitudine": 13.2513},
    {"codice": "056001", "nome": "Cagliari", "CAP": "09100", "provincia": "CA", "regione": "Sardegna", "latitudine": 39.2074, "longitudine": 9.1456},
    {"codice": "090001", "nome": "Sassari", "CAP": "07100", "provincia": "SS", "regione": "Sardegna", "latitudine": 40.7279, "longitudine": 8.3233},
    {"codice": "021001", "nome": "Cosenza", "CAP": "87100", "provincia": "CS", "regione": "Calabria", "latitudine": 39.3106, "longitudine": 16.2396},
    {"codice": "070002", "nome": "Lecce", "CAP": "73100", "provincia": "LE", "regione": "Puglia", "latitudine": 40.3510, "longitudine": 18.1717},
    {"codice": "001004", "nome": "Rieti", "CAP": "02100", "provincia": "RI", "regione": "Lazio", "latitudine": 42.4184, "longitudine": 12.8551},
    {"codice": "012001", "nome": "Avellino", "CAP": "83100", "provincia": "AV", "regione": "Campania", "latitudine": 40.9141, "longitudine": 14.7968},
    {"codice": "017001", "nome": "Salerno", "CAP": "84100", "provincia": "SA", "regione": "Campania", "latitudine": 40.6825, "longitudine": 14.7576},
    {"codice": "053001", "nome": "Pisa", "CAP": "56100", "provincia": "PI", "regione": "Toscana", "latitudine": 43.7228, "longitudine": 10.4017},
    {"codice": "053002", "nome": "Livorno", "CAP": "57100", "provincia": "LI", "regione": "Toscana", "latitudine": 43.5485, "longitudine": 10.3106},
    {"codice": "046001", "nome": "Foggia", "CAP": "71100", "provincia": "FG", "regione": "Puglia", "latitudine": 41.4644, "longitudine": 15.5469},
    {"codice": "005001", "nome": "Catanzaro", "CAP": "88100", "provincia": "CZ", "regione": "Calabria", "latitudine": 38.9066, "longitudine": 16.5944},
    {"codice": "010001", "nome": "Campobasso", "CAP": "86100", "provincia": "CB", "regione": "Molise", "latitudine": 41.5595, "longitudine": 14.6674},
    {"codice": "022001", "nome": "Potenza", "CAP": "85100", "provincia": "PZ", "regione": "Basilicata", "latitudine": 40.6333, "longitudine": 15.8000},
    {"codice": "065001", "nome": "Pescara", "CAP": "65100", "provincia": "PE", "regione": "Abruzzo", "latitudine": 42.4644, "longitudine": 14.2148},
    {"codice": "065002", "nome": "L'Aquila", "CAP": "67100", "provincia": "AQ", "regione": "Abruzzo", "latitudine": 42.3570, "longitudine": 13.3980},
    {"codice": "044001", "nome": "Siena", "CAP": "53100", "provincia": "SI", "regione": "Toscana", "latitudine": 43.3188, "longitudine": 11.3308},
    {"codice": "051001", "nome": "Arezzo", "CAP": "52100", "provincia": "AR", "regione": "Toscana", "latitudine": 43.4631, "longitudine": 11.8793},
]

_comuni_cache = None


def get_comuni_from_db():
    global _comuni_cache
    if _comuni_cache is not None:
        return _comuni_cache

    try:
        from backend.infrastructure.entities.models import Comune
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
    except Exception:
        return []


class RegioniView(MethodView):
    def get(self):
        try:
            from backend.infrastructure.entities.models import Regione
            regioni = Regione.query.order_by(Regione.nome).all()
            return jsonify([{"codice": r.codice, "nome": r.nome} for r in regioni])
        except Exception:
            return jsonify(REGIONI)


class ProvinceView(MethodView):
    def get(self):
        regione = request.args.get("regione", "")

        try:
            from backend.infrastructure.entities.models import Provincia
            query = Provincia.query
            if regione:
                query = query.filter_by(codice_regione=regione)
            province = query.order_by(Provincia.nome).all()
            return jsonify([{"codice": p.codice, "nome": p.nome, "regione": p.codice_regione} for p in province])
        except Exception:
            if regione:
                province = [p for p in PROVINCE if p["regione"] == regione]
                return jsonify(province)
            return jsonify(PROVINCE)


class ComuniView(MethodView):
    def get(self):
        provincia = request.args.get("provincia", "")

        if provincia:
            comuni = [c for c in COMUNI if c["provincia"] == provincia]
            return jsonify(comuni)

        return jsonify(COMUNI[:50])


class CercaIndirizzoView(MethodView):
    def get(self):
        q = request.args.get("q", "")

        if not q or len(q) < 2:
            return jsonify([])

        q_lower = q.lower()
        risultati = [
            c for c in COMUNI
            if q_lower in c["nome"].lower()
        ][:20]

        return jsonify([
            {
                "codice": c["codice"],
                "nome": c["nome"],
                "CAP": c["CAP"],
                "provincia": c["provincia"],
                "regione": c["regione"],
                "latitudine": c["latitudine"],
                "longitudine": c["longitudine"],
                "display": f"{c['nome']} ({c['provincia']}) - {c['regione']}"
            }
            for c in risultati
        ])


class GeocodificaView(MethodView):
    def get(self):
        import requests
        indirizzo = request.args.get("indirizzo", "")

        if not indirizzo:
            return jsonify({"error": "Indirizzo richiesto"}), 400

        indirizzo_lower = indirizzo.lower().strip()

        has_street = any(word in indirizzo_lower for word in ['via ', 'viale ', 'piazza ', 'corso ', 'strada ', 'largo '])

        if has_street:
            nominatim_url = "https://nominatim.openstreetmap.org/search"
            params = {
                "q": indirizzo + ", Italia",
                "format": "json",
                "limit": 1,
                "addressdetails": 1,
                "countrycodes": "it"
            }
            headers = {"User-Agent": "ERPSeed/1.0"}

            try:
                response = requests.get(nominatim_url, params=params, headers=headers, timeout=10)
                response.raise_for_status()
                data = response.json()

                if data:
                    result = data[0]
                    return jsonify({
                        "latitudine": float(result.get("lat", 0)),
                        "longitudine": float(result.get("lon", 0)),
                        "indirizzo_formattato": result.get("display_name", ""),
                        "qualita": result.get("importance", 0),
                        "fonte": "nominatim"
                    })
            except Exception:
                pass

        comuni_db = get_comuni_from_db()

        for c in comuni_db:
            if c['nome'].lower() == indirizzo_lower:
                return jsonify({
                    "latitudine": c['latitudine'],
                    "longitudine": c['longitudine'],
                    "indirizzo_formattato": f"{c['nome']}, {c['provincia']}, Italia",
                    "qualita": 1.0,
                    "fonte": "db"
                })

        words = indirizzo_lower.replace(',', ' ').split()
        for c in comuni_db:
            nome_lower = c['nome'].lower()
            if nome_lower in words:
                return jsonify({
                    "latitudine": c['latitudine'],
                    "longitudine": c['longitudine'],
                    "indirizzo_formattato": f"{c['nome']}, {c['provincia']}, Italia",
                    "qualita": 0.9,
                    "fonte": "db"
                })

        for c in COMUNI:
            if q_lower in c["nome"].lower():
                return jsonify({
                    "latitudine": c["latitudine"],
                    "longitudine": c["longitudine"],
                    "indirizzo_formattato": f"{c['nome']}, {c['provincia']}, {c['regione']}",
                    "qualita": 0.8,
                    "fonte": "fallback"
                })

        return jsonify({"error": "Indirizzo non trovato"}), 404


class GeocodificaInversaView(MethodView):
    def get(self):
        import requests
        lat = request.args.get("lat")
        lon = request.args.get("lon")

        if not lat or not lon:
            return jsonify({"error": "Coordinate richieste"}), 400

        lat_float = float(lat)
        lon_float = float(lon)

        closest = None
        min_dist = float('inf')

        for c in COMUNI:
            dist = ((c["latitudine"] - lat_float) ** 2 + (c["longitudine"] - lon_float) ** 2) ** 0.5
            if dist < min_dist:
                min_dist = dist
                closest = c

        if closest:
            return jsonify({
                "indirizzo": f"{closest['nome']}, {closest['provincia']}, {closest['regione']}",
                "via": "",
                "numero": "",
                "CAP": closest["CAP"],
                "comune": closest["nome"],
                "provincia": closest["provincia"],
                "regione": closest["regione"],
                "nazione": "IT"
            })

        nominatim_url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            "lat": lat,
            "lon": lon,
            "format": "json",
            "addressdetails": 1,
            "zoom": 18
        }
        headers = {"User-Agent": "ERPSeed/1.0"}

        try:
            response = requests.get(nominatim_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

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


geographic_bp.add_url_rule('/regioni', view_func=RegioniView.as_view('regioni'))
geographic_bp.add_url_rule('/province', view_func=ProvinceView.as_view('province'))
geographic_bp.add_url_rule('/comuni', view_func=ComuniView.as_view('comuni'))
geographic_bp.add_url_rule('/cerca', view_func=CercaIndirizzoView.as_view('cerca'))
geographic_bp.add_url_rule('/geocodifica', view_func=GeocodificaView.as_view('geocodifica'))
geographic_bp.add_url_rule('/geocodifica-inversa', view_func=GeocodificaInversaView.as_view('geocodifica_inversa'))
