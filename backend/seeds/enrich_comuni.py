"""
Arricchisce i comuni con dati ISTAT mancanti (codice_istat, cap, coordinate).
Legge il dump JSON da italian-locations e aggiorna i record esistenti.
"""
import os
import json
from backend import create_app
from backend.extensions import db
from backend.modules.entities.comune import Comune

JSON_PATH = os.path.join(os.path.dirname(__file__), "comuni_istat.json")


def enrich_comuni():
    if not os.path.exists(JSON_PATH):
        print(f"File {JSON_PATH} non trovato. Esegui: docker cp ...")
        return

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        source_list = json.load(f)

    app = create_app()
    with app.app_context():
        source_index = {}
        for s in source_list:
            key = (s["nome"].strip().lower(), s["siglaProvincia"])
            if key not in source_index:
                source_index[key] = s

        total = Comune.query.count()
        matched = 0
        updated_istat = 0
        updated_cap = 0
        updated_coords = 0
        not_found = []
        skipped_dupe = 0

        # Collect all proposed updates first, checking for conflicts
        # (codice_istat is unique, so we must avoid duplicates)
        existing_istat_codes = set(
            row[0] for row in Comune.query.with_entities(Comune.codice_istat)
            if row[0]
        )

        comuni = Comune.query.all()
        for c in comuni:
            key = (c.nome.strip().lower(), c.codice_provincia)
            src = source_index.get(key)
            if not src:
                matches = [s for k, s in source_index.items() if k[0] == key[0]]
                if len(matches) == 1:
                    src = matches[0]
                else:
                    not_found.append(c.nome)
                    continue

            matched += 1
            changed = False

            new_istat = src.get("codiceIstat")
            if not c.codice_istat and new_istat:
                if new_istat in existing_istat_codes:
                    skipped_dupe += 1
                else:
                    c.codice_istat = new_istat
                    existing_istat_codes.add(new_istat)
                    updated_istat += 1
                    changed = True

            if not c.cap and src.get("cap"):
                c.cap = src["cap"]
                updated_cap += 1
                changed = True

            if (not c.latitudine or not c.longitudine) and src.get("coordinate"):
                coord = src["coordinate"]
                if coord.get("lat") and coord.get("lng"):
                    c.latitudine = coord["lat"]
                    c.longitudine = coord["lng"]
                    updated_coords += 1
                    changed = True

            if changed:
                c.source = "ISTAT"

        db.session.commit()

        print(f"\nRiepilogo:")
        print(f"  Totale comuni nel DB:    {total}")
        print(f"  Matchati con ISTAT:      {matched}")
        print(f"  Codice ISTAT aggiunto:   {updated_istat}")
        print(f"  CAP aggiunto:            {updated_cap}")
        print(f"  Coordinate aggiunte:     {updated_coords}")
        print(f"  Saltati (duplicato):     {skipped_dupe}")
        if not_found:
            print(f"  Non trovati in ISTAT:    {len(not_found)} (es: {not_found[:5]})")
        print("✅ Arricchimento completato!")


if __name__ == '__main__':
    enrich_comuni()
