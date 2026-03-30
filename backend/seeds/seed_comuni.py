"""
Seed data per comuni italiani.
Esegue: flask seed-comuni
"""
from backend import create_app
from backend.extensions import db
from backend.modules.entities.comune import Comune, Regione, Provincia

# Dati base - 20 regioni
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

# Province con codice regione
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

# Principali comuni con coordinate
COMUNI = [
    {"codice": "001001", "nome": "Roma", "provincia": "RM", "regione": "07", "cap": "00100", "lat": 41.9028, "lon": 12.4964},
    {"codice": "015001", "nome": "Milano", "provincia": "MI", "regione": "09", "cap": "20100", "lat": 45.4642, "lon": 9.1900},
    {"codice": "063001", "nome": "Napoli", "provincia": "NA", "regione": "04", "cap": "80100", "lat": 40.8518, "lon": 14.2681},
    {"codice": "048001", "nome": "Torino", "provincia": "TO", "regione": "12", "cap": "10100", "lat": 45.0703, "lon": 7.6869},
    {"codice": "058001", "nome": "Palermo", "provincia": "PA", "regione": "15", "cap": "90100", "lat": 38.1157, "lon": 13.3615},
    {"codice": "027001", "nome": "Genova", "provincia": "GE", "regione": "08", "cap": "16100", "lat": 44.4056, "lon": 8.9463},
    {"codice": "025001", "nome": "Bologna", "provincia": "BO", "regione": "05", "cap": "40100", "lat": 44.4949, "lon": 11.3426},
    {"codice": "033001", "nome": "Firenze", "provincia": "FI", "regione": "16", "cap": "50100", "lat": 43.7696, "lon": 11.2558},
    {"codice": "082001", "nome": "Bari", "provincia": "BA", "regione": "13", "cap": "70100", "lat": 41.1171, "lon": 16.8543},
    {"codice": "057001", "nome": "Catania", "provincia": "CT", "regione": "15", "cap": "95100", "lat": 37.5079, "lon": 15.0833},
    {"codice": "069001", "nome": "Venezia", "provincia": "VE", "regione": "20", "cap": "30100", "lat": 45.4408, "lon": 12.3155},
    {"codice": "072001", "nome": "Verona", "provincia": "VR", "regione": "20", "cap": "37100", "lat": 45.4429, "lon": 10.9981},
    {"codice": "065001", "nome": "Messina", "provincia": "ME", "regione": "15", "cap": "98100", "lat": 38.1938, "lon": 15.5540},
    {"codice": "028001", "nome": "Padova", "provincia": "PD", "regione": "20", "cap": "35100", "lat": 45.4068, "lon": 11.8765},
    {"codice": "029001", "nome": "Trieste", "provincia": "TS", "regione": "06", "cap": "34100", "lat": 45.6495, "lon": 13.7768},
    {"codice": "017001", "nome": "Brescia", "provincia": "BS", "regione": "09", "cap": "25100", "lat": 45.5416, "lon": 10.2118},
    {"codice": "073001", "nome": "Taranto", "provincia": "TA", "regione": "13", "cap": "74100", "lat": 40.4643, "lon": 17.2471},
    {"codice": "100005", "nome": "Prato", "provincia": "PO", "regione": "16", "cap": "59100", "lat": 43.8777, "lon": 11.1022},
    {"codice": "080001", "nome": "Reggio Calabria", "provincia": "RC", "regione": "03", "cap": "89100", "lat": 38.1036, "lon": 15.6462},
    {"codice": "036001", "nome": "Modena", "provincia": "MO", "regione": "05", "cap": "41100", "lat": 44.6471, "lon": 10.9254},
    {"codice": "034001", "nome": "Parma", "provincia": "PR", "regione": "05", "cap": "43100", "lat": 44.8015, "lon": 10.3279},
    {"codice": "035001", "nome": "Reggio Emilia", "provincia": "RE", "regione": "05", "cap": "42100", "lat": 44.6989, "lon": 10.6314},
    {"codice": "047001", "nome": "Perugia", "provincia": "PG", "regione": "18", "cap": "06100", "lat": 43.1107, "lon": 12.3908},
    {"codice": "059001", "nome": "Ravenna", "provincia": "RA", "regione": "05", "cap": "48100", "lat": 44.4184, "lon": 12.2037},
    {"codice": "099001", "nome": "Ferrara", "provincia": "FE", "regione": "05", "cap": "44100", "lat": 44.8370, "lon": 11.6188},
    {"codice": "061001", "nome": "Rimini", "provincia": "RN", "regione": "05", "cap": "47900", "lat": 44.0593, "lon": 12.5686},
    {"codice": "071001", "nome": "Sassari", "provincia": "SS", "regione": "14", "cap": "07100", "lat": 40.7279, "lon": 8.3233},
    {"codice": "092001", "nome": "Cagliari", "provincia": "CA", "regione": "14", "cap": "09100", "lat": 39.2074, "lon": 9.1456},
    {"codice": "078001", "nome": "Lecce", "provincia": "LE", "regione": "13", "cap": "73100", "lat": 40.3510, "lon": 18.1717},
    {"codice": "101001", "nome": "Bolzano", "provincia": "BZ", "regione": "17", "cap": "39100", "lat": 46.4983, "lon": 11.3548},
    {"codice": "121001", "nome": "Trento", "provincia": "TN", "regione": "17", "cap": "38100", "lat": 46.0748, "lon": 11.1211},
    # Puglia - comuni principali
    {"codice": "075001", "nome": "Galatina", "provincia": "LE", "regione": "13", "cap": "73013", "lat": 40.1752, "lon": 18.1703},
    {"codice": "075002", "nome": "Gallipoli", "provincia": "LE", "regione": "13", "cap": "73014", "lat": 40.0547, "lon": 17.9936},
    {"codice": "075003", "nome": "Nardò", "provincia": "LE", "regione": "13", "cap": "73048", "lat": 40.1714, "lon": 18.0314},
    {"codice": "075004", "nome": "Otranto", "provincia": "LE", "regione": "13", "cap": "73028", "lat": 40.1474, "lon": 18.4864},
    {"codice": "072002", "nome": "Barletta", "provincia": "BT", "regione": "13", "cap": "76121", "lat": 41.3144, "lon": 16.2817},
    {"codice": "072003", "nome": "Andria", "provincia": "BT", "regione": "13", "cap": "76123", "lat": 41.2276, "lon": 16.2903},
    {"codice": "071002", "nome": "Manfredonia", "provincia": "FG", "regione": "13", "cap": "71043", "lat": 41.6275, "lon": 15.9104},
    {"codice": "071003", "nome": "San Severo", "provincia": "FG", "regione": "13", "cap": "71016", "lat": 41.6868, "lon": 15.3817},
    # Lazio
    {"codice": "058002", "nome": "Latina", "provincia": "LT", "regione": "07", "cap": "04100", "lat": 41.5316, "lon": 12.8981},
    {"codice": "056001", "nome": "Frosinone", "provincia": "FR", "regione": "07", "cap": "03100", "lat": 41.6340, "lon": 13.2513},
    {"codice": "057002", "nome": "Viterbo", "provincia": "VT", "regione": "07", "cap": "01100", "lat": 42.4315, "lon": 12.1276},
    {"codice": "052001", "nome": "Rieti", "provincia": "RI", "regione": "07", "cap": "02100", "lat": 42.4184, "lon": 12.8551},
    {"codice": "058003", "nome": "Velletri", "provincia": "RM", "regione": "07", "cap": "00049", "lat": 41.6867, "lon": 12.7761},
    {"codice": "058004", "nome": "Aprilia", "provincia": "LT", "regione": "07", "cap": "04011", "lat": 41.5951, "lon": 12.6556},
    {"codice": "058005", "nome": "Pomezia", "provincia": "RM", "regione": "07", "cap": "00040", "lat": 41.6687, "lon": 12.5012},
    {"codice": "058006", "nome": "Tivoli", "provincia": "RM", "regione": "07", "cap": "00019", "lat": 41.9594, "lon": 12.7966},
    # Lombardia
    {"codice": "016001", "nome": "Bergamo", "provincia": "BG", "regione": "09", "cap": "24100", "lat": 45.6983, "lon": 9.6772},
    {"codice": "108001", "nome": "Monza", "provincia": "MB", "regione": "09", "cap": "20900", "lat": 45.5801, "lon": 9.2724},
    {"codice": "012001", "nome": "Varese", "provincia": "VA", "regione": "09", "cap": "21100", "lat": 45.8206, "lon": 8.8252},
    {"codice": "013001", "nome": "Como", "provincia": "CO", "regione": "09", "cap": "22100", "lat": 45.8080, "lon": 9.0852},
    {"codice": "019001", "nome": "Mantova", "provincia": "MN", "regione": "09", "cap": "46100", "lat": 45.1564, "lon": 10.7914},
    {"codice": "019002", "nome": "Cremona", "provincia": "CR", "regione": "09", "cap": "26100", "lat": 45.1333, "lon": 10.0333},
    {"codice": "097001", "nome": "Lecco", "provincia": "LC", "regione": "09", "cap": "23900", "lat": 45.8566, "lon": 9.3972},
    # Campania
    {"codice": "063002", "nome": "Salerno", "provincia": "SA", "regione": "04", "cap": "84100", "lat": 40.6825, "lon": 14.7576},
    {"codice": "064001", "nome": "Avellino", "provincia": "AV", "regione": "04", "cap": "83100", "lat": 40.9141, "lon": 14.7968},
    {"codice": "062001", "nome": "Benevento", "provincia": "BN", "regione": "04", "cap": "82100", "lat": 41.1335, "lon": 14.7811},
    {"codice": "061001", "nome": "Caserta", "provincia": "CE", "regione": "04", "cap": "81100", "lat": 41.0746, "lon": 14.3325},
    # Emilia-Romagna
    {"codice": "037001", "nome": "Piacenza", "provincia": "PC", "regione": "05", "cap": "29100", "lat": 45.0146, "lon": 9.6434},
    {"codice": "038001", "nome": "Rimini", "provincia": "RN", "regione": "05", "cap": "47900", "lat": 44.0593, "lon": 12.5686},
    {"codice": "039001", "nome": "Forlì", "provincia": "FO", "regione": "05", "cap": "47100", "lat": 44.2228, "lon": 12.0408},
    {"codice": "040001", "nome": "Cesena", "provincia": "FO", "regione": "05", "cap": "47521", "lat": 44.1391, "lon": 12.2431},
    # Toscana
    {"codice": "046001", "nome": "Pisa", "provincia": "PI", "regione": "16", "cap": "56100", "lat": 43.7228, "lon": 10.4017},
    {"codice": "047002", "nome": "Livorno", "provincia": "LI", "regione": "16", "cap": "57100", "lat": 43.5485, "lon": 10.3106},
    {"codice": "048002", "nome": "Arezzo", "provincia": "AR", "regione": "16", "cap": "52100", "lat": 43.4631, "lon": 11.8793},
    {"codice": "052002", "nome": "Siena", "provincia": "SI", "regione": "16", "cap": "53100", "lat": 43.3188, "lon": 11.3308},
    {"codice": "053001", "nome": "Lucca", "provincia": "LU", "regione": "16", "cap": "55100", "lat": 43.8427, "lon": 10.5028},
    {"codice": "045001", "nome": "Pistoia", "provincia": "PT", "regione": "16", "cap": "51100", "lat": 43.9148, "lon": 10.9046},
    {"codice": "050001", "nome": "Massa", "provincia": "MS", "regione": "16", "cap": "54100", "lat": 44.0862, "lon": 10.1614},
    # Sicilia
    {"codice": "054001", "nome": "Messina", "provincia": "ME", "regione": "15", "cap": "98100", "lat": 38.1938, "lon": 15.5540},
    {"codice": "055001", "nome": "Catania", "provincia": "CT", "regione": "15", "cap": "95100", "lat": 37.5079, "lon": 15.0833},
    {"codice": "056002", "nome": "Siracusa", "provincia": "SR", "regione": "15", "cap": "96100", "lat": 37.0576, "lon": 15.2935},
    {"codice": "084001", "nome": "Ragusa", "provincia": "RG", "regione": "15", "cap": "97100", "lat": 36.9259, "lon": 14.7411},
    {"codice": "081001", "nome": "Trapani", "provincia": "TP", "regione": "15", "cap": "91100", "lat": 38.0184, "lon": 12.3358},
    {"codice": "085001", "nome": "Caltanissetta", "provincia": "CL", "regione": "15", "cap": "93100", "lat": 37.4899, "lon": 14.0630},
    {"codice": "086001", "nome": "Agrigento", "provincia": "AG", "regione": "15", "cap": "92100", "lat": 37.3104, "lon": 13.5766},
    {"codice": "083001", "nome": "Enna", "provincia": "EN", "regione": "15", "cap": "94100", "lat": 37.5961, "lon": 14.2790},
]


def seed_comuni():
    """Eseede i dati base dei comuni."""
    app = create_app()
    with app.app_context():
        # Crea tabelle
        db.create_all()
        
        # Seed regioni
        for r in REGIONI:
            if not Regione.query.filter_by(codice=r["codice"]).first():
                db.session.add(Regione(**r))
        db.session.commit()
        print(f"✅ Inserite {len(REGIONI)} regioni")
        
        # Seed province
        for p in PROVINCE:
            if not Provincia.query.filter_by(codice=p["codice"]).first():
                db.session.add(Provincia(
                    codice=p["codice"],
                    nome=p["nome"],
                    codice_regione=p["regione"]
                ))
        db.session.commit()
        print(f"✅ Inserite {len(PROVINCE)} province")
        
        # Seed comuni
        count = 0
        for c in COMUNI:
            if not Comune.query.filter_by(codice_istat=c["codice"]).first():
                db.session.add(Comune(
                    codice_istat=c["codice"],
                    nome=c["nome"],
                    codice_provincia=c["provincia"],
                    codice_regione=c["regione"],
                    cap=c["cap"],
                    latitudine=c["lat"],
                    longitudine=c["lon"],
                    source='ISTAT',
                    is_manuale=False
                ))
                count += 1
        db.session.commit()
        print(f"✅ Inseriti {count} comuni")
        
        print(f"\n📊 Totale regioni: {Regione.query.count()}")
        print(f"📊 Totale province: {Provincia.query.count()}")
        print(f"📊 Totale comuni: {Comune.query.count()}")
        print("\n🚀 Per sincronizzare tutti i comuni ISTAT:")
        print("   curl -X POST http://localhost:5002/api/v1/comuni/sync -H 'Authorization: Bearer <token>'")


if __name__ == '__main__':
    seed_comuni()
