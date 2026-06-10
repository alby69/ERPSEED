# Indirizzi

Il modulo **Indirizzi** gestisce gli indirizzi associati a soggetti
(clienti, fornitori, dipendenti, etc.).

## Struttura

Ogni indirizzo contiene:

- **Città/Comune** — selezionato dal database comuni (autocomplete)
- **Via/Piazza** — autocomplete su cache locale `Via` + Nominatim fallback
- **Numero civico**
- **Tipo** — residenza, sede legale, magazzino, fatturazione, consegna

I seguenti campi vengono **auto-compilati** dal modello **Comune** alla
selezione della città (non editabili nel form):

- **CAP**, **Provincia**, **Regione**, **Nazione** (default IT)
- **Latitudine**, **Longitudine**

## Modello Via

Il modello `Via` funge da **cache locale** per le strade, popolata
automaticamente da Nominatim (OpenStreetMap) sotto richiesta.
Ogni via è associata a un comune tramite `comune_id`.

## Come usare

### Creare un indirizzo

1. Seleziona il **soggetto** a cui associare l'indirizzo
2. Scegli il **tipo** di indirizzo
3. **Seleziona la Città** (autocomplete sul database comuni):
   - CAP, provincia, regione, nazione e coordinate si compileranno automaticamente
4. **Digita la Via** (autocomplete, attivo solo dopo aver selezionato la città):
   - Cerca nella cache locale `Via` + Nominatim fallback
   - Se la via non è in cache, Nominatim la cerca e la salva automaticamente
5. **Inserisci il Numero Civico**

### Modifica

Clicca sul record per modificare i campi.

### Tipi di indirizzo

| Tipo | Descrizione |
|---|---|
| Residenza | Indirizzo di residenza |
| Sede Legale | Indirizzo legale/amministrativo |
| Magazzino | Sede operativa / magazzino |
| Fatturazione | Indirizzo per fatture |
| Consegna | Indirizzo per spedizioni |

## Colonne tabella

| Colonna | Descrizione |
|---|---|
| Cod. Soggetto | Codice identificativo del soggetto associato |
| Soggetto | Nome/ragione sociale del soggetto |
| Tipo | Tipologia indirizzo |
| Città | Comune (dal database comuni) |
| Regione | Regione (auto-compilata dal comune) |
| Provincia | Sigla provincia (auto-compilata dal comune) |
| Nazione | Codice nazione ISO (auto-compilato, default IT) |

## API

```
# Indirizzi
GET    /api/v1/indirizzi              — Lista (JWT)
POST   /api/v1/indirizzi              — Crea (JWT)
GET    /api/v1/indirizzi/{id}         — Dettaglio (JWT)
PUT    /api/v1/indirizzi/{id}         — Modifica (JWT)
DELETE /api/v1/indirizzi/{id}         — Elimina (JWT)

# Vie (cache locale + Nominatim)
GET    /api/v1/vie/?comune_id=X&q=nome  — Cerca strade per comune
POST   /api/v1/vie/bulk?comune_id=X     — Pre-carica strade da Nominatim
```
