# Indirizzi

Il modulo **Indirizzi** gestisce gli indirizzi associati a soggetti
(clienti, fornitori, dipendenti, etc.).

## Struttura

Ogni indirizzo contiene:
- **Denominazione** — via, piazza, viale, etc.
- **Numero civico**
- **CAP** e **Città** (autocompletati dal database comuni)
- **Provincia** e **Regione**
- **Nazione** (ISO 3166-1 alpha-2, default IT)
- **Coordinate** (latitudine, longitudine)
- **Tipo** — residenza, sede legale, magazzino, fatturazione, consegna

## Come usare

### Creare un indirizzo

1. Seleziona il **soggetto** a cui associare l'indirizzo
2. Scegli il **tipo** di indirizzo
3. Inserisci via e numero civico
4. Seleziona **Regione → Provincia → Comune**:
   - La città, il CAP, la provincia e regione si compileranno automaticamente
   - Le coordinate geografiche verranno recuperate dal database
5. (Opzionale) Clicca **"Geocodifica"** per ottenere coordinate precise
   da Nominatim (OpenStreetMap)

### Modifica

Clicca sul record per modificare i campi.
La geocodifica è sempre disponibile per aggiornare le coordinate.

### Tipi di indirizzo

| Tipo | Descrizione |
|---|---|
| Residenza | Indirizzo di residenza |
| Sede Legale | Indirizzo legale/amministrativo |
| Magazzino | Sede operativa / magazzino |
| Fatturazione | Indirizzo per fatture |
| Consegna | Indirizzo per spedizioni |

## Geocodifica

### Forward Geocoding (indirizzo → coordinate)

Inserisci un indirizzo testuale, il sistema cerca le coordinate in questo ordine:
1. **Nominatim (OSM)** — per indirizzi con via/viale/piazza
2. **Database comuni** — lookup per nome del comune
3. **Nominatim (fallback)** — ricerca libera

### Reverse Geocoding (coordinate → indirizzo)

Inserisci latitudine e longitudine per ottenere l'indirizzo corrispondente.

## API

```
GET    /api/v1/indirizzi              — Lista (JWT)
POST   /api/v1/indirizzi              — Crea (JWT)
GET    /api/v1/indirizzi/{id}         — Dettaglio (JWT)
PUT    /api/v1/indirizzi/{id}         — Modifica (JWT)
DELETE /api/v1/indirizzi/{id}         — Elimina (JWT)
GET    /api/v1/indirizzi/geocodifica  — Forward geocoding
GET    /api/v1/indirizzi/geocodifica-inversa — Reverse geocoding
```
