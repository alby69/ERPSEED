"""
Endpoint per dati geografici italiani e geocodifica.
"""
from flask.views import MethodView
from flask_smorest import Blueprint
from flask import request, jsonify
import requests

# Blueprint per dati geografici - SENZA autenticazione (dati pubblici)
geografico_blp = Blueprint("geografico", __name__, url_prefix="/api/v1", description="Dati geografici italiani")


# Cache per comuni dal database
_comuni_cache = None

def get_comuni_from_db():
    """Ottieni comuni dal database."""
    global _comuni_cache
    if _comuni_cache is not None:
        return _comuni_cache

    try:
        from modules.entities.comune import Comune
        from extensions import db

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


# Fallback hardcoded
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

# Alcuni comuni italiani con CAP e coordinate (fallback)
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
    {"codice": "075001", "nome": "Galatina", "CAP": "73013", "provincia": "LE", "regione": "Puglia", "latitudine": 40.1752, "longitudine": 18.1703},
    {"codice": "075002", "nome": "Gallipoli", "CAP": "73014", "provincia": "LE", "regione": "Puglia", "latitudine": 40.0547, "longitudine": 17.9936},
    {"codice": "075003", "nome": "Nardò", "CAP": "73048", "provincia": "LE", "regione": "Puglia", "latitudine": 40.1714, "longitudine": 18.0314},
    {"codice": "075004", "nome": "Otranto", "CAP": "73028", "provincia": "LE", "regione": "Puglia", "latitudine": 40.1474, "longitudine": 18.4864},
    {"codice": "075005", "nome": "Lecce", "CAP": "73100", "provincia": "LE", "regione": "Puglia", "latitudine": 40.3510, "longitudine": 18.1717},
    {"codice": "075006", "nome": "Brindisi", "CAP": "72100", "provincia": "BR", "regione": "Puglia", "latitudine": 40.6327, "longitudine": 17.9398},
    {"codice": "075007", "nome": "Taranto", "CAP": "74100", "provincia": "TA", "regione": "Puglia", "latitudine": 40.4643, "longitudine": 17.2471},
    {"codice": "075008", "nome": "Bari", "CAP": "70100", "provincia": "BA", "regione": "Puglia", "latitudine": 41.1171, "longitudine": 16.8543},
    {"codice": "075009", "nome": "Barletta", "CAP": "76121", "provincia": "BT", "regione": "Puglia", "latitudine": 41.3144, "longitudine": 16.2817},
    {"codice": "075010", "nome": "Andria", "CAP": "76123", "provincia": "BT", "regione": "Puglia", "latitudine": 41.2276, "longitudine": 16.2903},
    {"codice": "075011", "nome": "Foggia", "CAP": "71100", "provincia": "FG", "regione": "Puglia", "latitudine": 41.4644, "longitudine": 15.5469},
    {"codice": "075012", "nome": "Manfredonia", "CAP": "71043", "provincia": "FG", "regione": "Puglia", "latitudine": 41.6275, "longitudine": 15.9104},
    {"codice": "001005", "nome": "Velletri", "CAP": "00049", "provincia": "RM", "regione": "Lazio", "latitudine": 41.6867, "longitudine": 12.7761},
    {"codice": "001006", "nome": "Aprilia", "CAP": "04011", "provincia": "LT", "regione": "Lazio", "latitudine": 41.5951, "longitudine": 12.6556},
    {"codice": "001007", "nome": "Pomezia", "CAP": "00040", "provincia": "RM", "regione": "Lazio", "latitudine": 41.6687, "longitudine": 12.5012},
    {"codice": "001008", "nome": "Tivoli", "CAP": "00019", "provincia": "RM", "regione": "Lazio", "latitudine": 41.9594, "longitudine": 12.7966},
    {"codice": "015002", "nome": "Bergamo", "CAP": "24100", "provincia": "BG", "regione": "Lombardia", "latitudine": 45.6983, "longitudine": 9.6772},
    {"codice": "015003", "nome": "Brescia", "CAP": "25100", "provincia": "BS", "regione": "Lombardia", "latitudine": 45.5416, "longitudine": 10.2118},
    {"codice": "015004", "nome": "Monza", "CAP": "20900", "provincia": "MB", "regione": "Lombardia", "latitudine": 45.5801, "longitudine": 9.2724},
    {"codice": "015005", "nome": "Varese", "CAP": "21100", "provincia": "VA", "regione": "Lombardia", "latitudine": 45.8206, "longitudine": 8.8252},
    {"codice": "015006", "nome": "Como", "CAP": "22100", "provincia": "CO", "regione": "Lombardia", "latitudine": 45.8080, "longitudine": 9.0852},
    {"codice": "015007", "nome": "Mantova", "CAP": "46100", "provincia": "MN", "regione": "Lombardia", "latitudine": 45.1564, "longitudine": 10.7914},
    {"codice": "015008", "nome": "Cremona", "CAP": "26100", "provincia": "CR", "regione": "Lombardia", "latitudine": 45.1333, "longitudine": 10.0333},
    {"codice": "015009", "nome": "Lecco", "CAP": "23900", "provincia": "LC", "regione": "Lombardia", "latitudine": 45.8566, "longitudine": 9.3972},
    {"codice": "048002", "nome": "Novara", "CAP": "28100", "provincia": "NO", "regione": "Piemonte", "latitudine": 45.4469, "longitudine": 8.6222},
    {"codice": "048003", "nome": "Alessandria", "CAP": "15100", "provincia": "AL", "regione": "Piemonte", "latitudine": 44.9111, "longitudine": 8.6161},
    {"codice": "048004", "nome": "Asti", "CAP": "14100", "provincia": "AT", "regione": "Piemonte", "latitudine": 44.9007, "longitudine": 8.2065},
    {"codice": "048005", "nome": "Cuneo", "CAP": "12100", "provincia": "CN", "regione": "Piemonte", "latitudine": 44.3845, "longitudine": 7.5428},
    {"codice": "063002", "nome": "Salerno", "CAP": "84100", "provincia": "SA", "regione": "Campania", "latitudine": 40.6825, "longitudine": 14.7576},
    {"codice": "063003", "nome": "Avellino", "CAP": "83100", "provincia": "AV", "regione": "Campania", "latitudine": 40.9141, "longitudine": 14.7968},
    {"codice": "063004", "nome": "Benevento", "CAP": "82100", "provincia": "BN", "regione": "Campania", "latitudine": 41.1335, "longitudine": 14.7811},
    {"codice": "063005", "nome": "Caserta", "CAP": "81100", "provincia": "CE", "regione": "Campania", "latitudine": 41.0746, "longitudine": 14.3325},
    {"codice": "025002", "nome": "Modena", "CAP": "41100", "provincia": "MO", "regione": "Emilia-Romagna", "latitudine": 44.6471, "longitudine": 10.9254},
    {"codice": "025003", "nome": "Parma", "CAP": "43100", "provincia": "PR", "regione": "Emilia-Romagna", "latitudine": 44.8015, "longitudine": 10.3279},
    {"codice": "025004", "nome": "Reggio Emilia", "CAP": "42100", "provincia": "RE", "regione": "Emilia-Romagna", "latitudine": 44.6989, "longitudine": 10.6314},
    {"codice": "025005", "nome": "Rimini", "CAP": "47900", "provincia": "RN", "regione": "Emilia-Romagna", "latitudine": 44.0593, "longitudine": 12.5686},
    {"codice": "025006", "nome": "Ravenna", "CAP": "48100", "provincia": "RA", "regione": "Emilia-Romagna", "latitudine": 44.4184, "longitudine": 12.2037},
    {"codice": "033002", "nome": "Pistoia", "CAP": "51100", "provincia": "PT", "regione": "Toscana", "latitudine": 43.9148, "longitudine": 10.9046},
    {"codice": "033003", "nome": "Lucca", "CAP": "55100", "provincia": "LU", "regione": "Toscana", "latitudine": 43.8427, "longitudine": 10.5028},
    {"codice": "033004", "nome": "Massa", "CAP": "54100", "provincia": "MS", "regione": "Toscana", "latitudine": 44.0862, "longitudine": 10.1614},
    {"codice": "033005", "nome": "Carrara", "CAP": "54033", "provincia": "MS", "regione": "Toscana", "latitudine": 44.0782, "longitudine": 10.1036},
    {"codice": "021002", "nome": "Crotone", "CAP": "88900", "provincia": "KR", "regione": "Calabria", "latitudine": 39.0803, "longitudine": 17.1271},
    {"codice": "021003", "nome": "Cosenza", "CAP": "87100", "provincia": "CS", "regione": "Calabria", "latitudine": 39.3106, "longitudine": 16.2396},
    {"codice": "021004", "nome": "Reggio Calabria", "CAP": "89100", "provincia": "RC", "regione": "Calabria", "latitudine": 38.1036, "longitudine": 15.6462},
    {"codice": "021005", "nome": "Vibo Valentia", "CAP": "89900", "provincia": "VV", "regione": "Calabria", "latitudine": 38.6756, "longitudine": 16.1026},
    {"codice": "056003", "nome": "Olbia", "CAP": "07026", "provincia": "SS", "regione": "Sardegna", "latitudine": 40.9225, "longitudine": 9.4960},
    {"codice": "056004", "nome": "Tempio Pausania", "CAP": "07029", "provincia": "SS", "regione": "Sardegna", "latitudine": 40.8994, "longitudine": 9.1058},
    {"codice": "056005", "nome": "Oristano", "CAP": "09170", "provincia": "OR", "regione": "Sardegna", "latitudine": 39.9043, "longitudine": 8.5913},
    {"codice": "102002", "nome": "Merano", "CAP": "39012", "provincia": "BZ", "regione": "Trentino-Alto Adige", "latitudine": 46.6705, "longitudine": 11.1530},
    {"codice": "102003", "nome": "Trento", "CAP": "38100", "provincia": "TN", "regione": "Trentino-Alto Adige", "latitudine": 46.0748, "longitudine": 11.1211},
    {"codice": "101002", "nome": "Rovereto", "CAP": "38068", "provincia": "TN", "regione": "Trentino-Alto Adige", "latitudine": 45.8904, "longitudine": 11.0360},
]


@geografico_blp.route("/indirizzi/regioni")
class Regioni(MethodView):
    def get(self):
        """Lista di tutte le regioni italiane"""
        # Usa il database se disponibile, altrimenti ritorna hardcoded
        try:
            from modules.entities.comune import Regione
            from extensions import db

            regioni = Regione.query.order_by(Regione.nome).all()
            return jsonify([{"codice": r.codice, "nome": r.nome} for r in regioni])
        except:
            return jsonify(REGIONI)


@geografico_blp.route("/indirizzi/province")
class Province(MethodView):
    def get(self):
        """Lista province italiane, filtrate per regione"""
        regione = request.args.get("regione", "")

        try:
            from modules.entities.comune import Provincia

            query = Provincia.query
            if regione:
                query = query.filter_by(codice_regione=regione)
            province = query.order_by(Provincia.nome).all()
            return jsonify([{"codice": p.codice, "nome": p.nome, "regione": p.codice_regione} for p in province])
        except:
            if regione:
                province = [p for p in PROVINCE if p["regione"] == regione]
                return jsonify(province)
            return jsonify(PROVINCE)


@geografico_blp.route("/indirizzi/comuni")
class Comuni(MethodView):
    def get(self):
        """Lista comuni italiani, filtrati per provincia"""
        provincia = request.args.get("provincia", "")

        if provincia:
            comuni = [c for c in COMUNI if c["provincia"] == provincia]
            return jsonify(comuni)

        return jsonify(COMUNI[:50])  # Ritorna solo i primi 50 se nessun filtro


@geografico_blp.route("/indirizzi/cerca")
class CercaIndirizzo(MethodView):
    def get(self):
        """Cerca comune per nome"""
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


@geografico_blp.route("/indirizzi/geocodifica")
class Geocodifica(MethodView):
    def get(self):
        """Geocodifica: converte indirizzo in coordinate lat/lon"""
        indirizzo = request.args.get("indirizzo", "")

        if not indirizzo:
            return jsonify({"error": "Indirizzo richiesto"}), 400

        indirizzo_lower = indirizzo.lower().strip()

        # 1. Se c'è una via specifica (via, viale, piazza, etc.), usa direttamente Nominatim
        # perché l'utente vuole l'indirizzo preciso, non solo il comune
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
            headers = {
                "User-Agent": "ERPSeed/1.0"
            }

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
            except Exception as e:
                pass  # Fallback to DB search

        # 2. Altrimenti cerca prima nel database comuni (7900+ comuni con coordinate)
        comuni_db = get_comuni_from_db()

        # Cerca prima match esatto (case insensitive)
        for c in comuni_db:
            if c['nome'].lower() == indirizzo_lower:
                return jsonify({
                    "latitudine": c['latitudine'],
                    "longitudine": c['longitudine'],
                    "indirizzo_formattato": f"{c['nome']}, {c['provincia']}, Italia",
                    "qualita": 1.0,
                    "fonte": "db"
                })

        # Poi cerca match dove il nome del comune è una parola intera nell'indirizzo
        # (non una sottostringa)
        words = indirizzo_lower.replace(',', ' ').split()
        for c in comuni_db:
            nome_lower = c['nome'].lower()
            # Verifica che il nome sia una parola intera nell'indirizzo
            if nome_lower in words:
                return jsonify({
                    "latitudine": c['latitudine'],
                    "longitudine": c['longitudine'],
                    "indirizzo_formattato": f"{c['nome']}, {c['provincia']}, Italia",
                    "qualita": 0.9,
                    "fonte": "db"
                })
            nominatim_url = "https://nominatim.openstreetmap.org/search"
            params = {
                "q": indirizzo + ", Italia",
                "format": "json",
                "limit": 1,
                "addressdetails": 1,
                "countrycodes": "it"
            }
            headers = {
                "User-Agent": "ERPSeed/1.0"
            }

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
            except Exception as e:
                pass

        # 3. Se non trovato, prova nei comuni hardcoded come ultimo fallback
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


@geografico_blp.route("/indirizzi/geocodifica-inversa")
class GeocodificaInversa(MethodView):
    def get(self):
        """Reverse geocodifica: converte coordinate lat/lon in indirizzo"""
        lat = request.args.get("lat")
        lon = request.args.get("lon")

        if not lat or not lon:
            return jsonify({"error": "Coordinate richieste"}), 400

        # Trova il comune più vicino
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

        # Fallback a Nominatim
        nominatim_url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            "lat": lat,
            "lon": lon,
            "format": "json",
            "addressdetails": 1,
            "zoom": 18
        }
        headers = {
            "User-Agent": "ERPSeed/1.0"
        }

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
