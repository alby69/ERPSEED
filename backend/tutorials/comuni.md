# Comuni Italiani

Il modulo **Comuni** gestisce l'anagrafica dei comuni italiani, utilizzata
come riferimento per indirizzi, soggetti e fatturazione.

## Dati

Il database contiene **~12.000 comuni** italiani popolati automaticamente
da [geocoded.me](https://geocoded.me) (fonte: GeoNames + Wikidata, CC BY 4.0).

Ogni comune include:
- Nome e denominazione ufficiale
- Provincia e Regione di appartenenza
- Coordinate geografiche (latitudine, longitudine)
- CAP (codice postale)
- Popolazione
- Superficie

## Come usare

### Ricerca

Usa la barra di ricerca o i filtri per Regione/Provincia.
La tabella supporta ordinamento per colonna e paginazione.

### Aggiungere un comune manualmente

Clicca **"Aggiungi Comune"** per inserire un comune non presente.
Utile per località estere o frazioni non coperte dal dataset standard.

### Modificare un comune

Clicca l'icona **matita** su un comune per modificare nome, CAP,
denominazione o coordinate.

### Eliminare un comune

Solo i comuni aggiunti manualmente possono essere eliminati.
I comuni importati da geocoded.me sono protetti.

### Sincronizzazione

Per forzare un aggiornamento dei dati:
```
flask seed-comuni
```

## API

Tutte le operazioni CRUD sono disponibili tramite API REST:

```
GET    /api/v1/comuni              — Lista paginata con filtri
POST   /api/v1/comuni              — Crea comune (JWT)
GET    /api/v1/comuni/{id}         — Dettaglio
PUT    /api/v1/comuni/{id}         — Modifica (JWT)
DELETE /api/v1/comuni/{id}         — Elimina solo manuali (JWT)
GET    /api/v1/comuni/stats        — Statistiche
GET    /api/v1/comuni/regioni      — Elenco regioni
GET    /api/v1/comuni/province     — Elenco province
```
