import csv
import sys

# Read from file
with open('/tmp/comuni_utf8.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f, delimiter=';')
    header = next(reader)
    
    from backend import create_app
    from backend.extensions import db
    from backend.entities.comune import Comune, Regione, Provincia
    
    app = create_app()
    with app.app_context():
        count = 0
        skipped = 0
        
        for row in reader:
            if len(row) < 20:
                continue
            
            cod_regione = row[0].strip()
            cod_istat = row[3].strip()
            denominazione = row[6].strip() if row[6].strip() else row[5].strip()
            nome = denominazione
            prog_provincia = row[14].strip()
            cap = row[19].strip()[:5] if row[19].strip() else ''
            
            if not cod_istat or not nome:
                continue
            
            existing = Comune.query.filter_by(codice_istat=cod_istat).first()
            if existing:
                skipped += 1
                continue
            
            comune = Comune()
            comune.codice_istat = cod_istat
            comune.nome = nome
            comune.codice_regione = cod_regione
            comune.codice_provincia = prog_provincia
            comune.cap = cap
            comune.source = 'ISTAT'
            comune.is_manuale = False
            db.session.add(comune)
            count += 1
            
            if count % 500 == 0:
                db.session.commit()
                print(f'Importati {count} comuni...')
        
        db.session.commit()
        print(f'\n✅ Importati: {count}')
        print(f'Già presenti: {skipped}')
        print(f'Totale comuni: {Comune.query.count()}')
