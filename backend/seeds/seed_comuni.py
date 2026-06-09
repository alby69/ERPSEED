"""
Seed data per comuni italiani tramite geocoded.me API.
Esegue: flask seed-comuni

Popola regioni, province e tutti i ~7900 comuni italiani
con coordinate geografiche da https://geocoded.me (gratuito, no API key).
"""
import sys
import time
from backend import create_app
from backend.extensions import db
from backend.modules.entities.comune import Comune, Regione, Provincia
from backend.services.geocoded_client import geocoded_client

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
    {"codice": "20", "nome": "Veneto"},
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
    {"codice": "FC", "nome": "Forlì-Cesena", "regione": "05"},
    {"codice": "FE", "nome": "Ferrara", "regione": "05"},
    {"codice": "FG", "nome": "Foggia", "regione": "13"},
    {"codice": "FI", "nome": "Firenze", "regione": "16"},
    {"codice": "FM", "nome": "Fermo", "regione": "10"},
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
    {"codice": "SU", "nome": "Sud Sardegna", "regione": "14"},
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

GEOCODED_STATE_MAP = {
    "23": "AO",
}

def _map_state_code(geocoded_iso2):
    return GEOCODED_STATE_MAP.get(geocoded_iso2, geocoded_iso2)

def _get_regione_codice(provincia_codice):
    for p in PROVINCE:
        if p["codice"] == provincia_codice:
            return p["regione"]
    return None

def seed_comuni():
    app = create_app()
    with app.app_context():
        db.create_all()

        print("Inserimento regioni...")
        for r in REGIONI:
            if not Regione.query.filter_by(codice=r["codice"]).first():
                db.session.add(Regione(**r))
        db.session.commit()
        print(f"  {Regione.query.count()} regioni")

        print("Inserimento province...")
        for p in PROVINCE:
            if not Provincia.query.filter_by(codice=p["codice"]).first():
                db.session.add(Provincia(
                    codice=p["codice"],
                    nome=p["nome"],
                    codice_regione=p["regione"]
                ))
        db.session.commit()
        print(f"  {Provincia.query.count()} province")

        print("Fetch stati/ province da geocoded.me...")
        try:
            api_states = geocoded_client.get_states("IT", limit=200)
            print(f"  Trovati {len(api_states)} stati/ province su geocoded.me")
        except Exception as e:
            print(f"  ERRORE: {e}")
            sys.exit(1)

        total_inserted = 0
        total_skipped = 0

        for state in api_states:
            state_code = state.get("iso2", "")
            prov_code = _map_state_code(state_code)
            reg_codice = _get_regione_codice(prov_code)

            if not reg_codice:
                print(f"  ⚠️  Provincia {prov_code} non trovata, salto {state.get('name')}")
                total_skipped += 1
                continue

            print(f"  Fetch città per {state.get('name')} ({state_code})...", end=" ", flush=True)
            try:
                cities = geocoded_client.get_all_cities("IT", state_code)
            except Exception as e:
                print(f"ERRORE: {e}")
                continue

            inserted = 0
            skipped = 0
            for city in cities:
                nome = city.get("name", "").strip()
                if not nome:
                    continue
                if Comune.query.filter_by(codice_istat=None).filter(
                    Comune.nome == nome,
                    Comune.codice_provincia == prov_code
                ).first():
                    skipped += 1
                    continue
                if Comune.query.filter_by(nome=nome, codice_provincia=prov_code).first():
                    skipped += 1
                    continue
                db.session.add(Comune(
                    nome=nome,
                    codice_provincia=prov_code,
                    codice_regione=reg_codice,
                    latitudine=city.get("latitude"),
                    longitudine=city.get("longitude"),
                    popolazione=city.get("population"),
                    source='GEOCODED',
                    is_manuale=False
                ))
                inserted += 1

            db.session.commit()
            total_inserted += inserted
            total_skipped += skipped
            print(f"{inserted} inseriti, {skipped} già presenti")
            time.sleep(0.3)

        print(f"\n📊 Riepilogo:")
        print(f"  Regioni: {Regione.query.count()}")
        print(f"  Province: {Provincia.query.count()}")
        print(f"  Comuni: {Comune.query.count()}")
        print(f"  Inseriti: {total_inserted}, Saltati: {total_skipped}")
        print("✅ Seed completato!")


if __name__ == '__main__':
    seed_comuni()
