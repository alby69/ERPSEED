# FlaskERP Test Runner - Guida all'Uso

## Panoramica

Il sistema di Test Runner di FlaskERP permette di:
- **Creare test automatici** per tutti i moduli (Anagrafiche, Ruoli, Indirizzi, Contatti, ecc.)
- **Eseguire test CRUD** automaticamente
- **Gestire lo stato dei moduli** (bozza → in_test → testato → pubblicato → obsoleto)
- **Esportare report** dei risultati dei test

## Accesso

Accedi alla pagina Test Runner da: `/test-runner` (solo admin)

## Stati dei Moduli

| Stato | Descrizione | Transizioni |
|-------|-------------|-------------|
| `bozza` | Modulo appena creato, non testato | → `in_test` |
| `in_test` | Test in corso di esecuzione | → `testato`, → `bozza` |
| `testato` | Test completati con successo | → `pubblicato` |
| `pubblicato` | Operativo in produzione | → `obsoleto` |
| `obsoleto` | Non più utilizzabile | (stato finale) |

**Regola importante**: Per passare allo stato `testato`, tutti i test devono passare con successo.

## Guida Step-by-Step

### 1. Creare una Test Suite

Puoi creare una test suite in due modi:

#### Metodo A: Manuale
1. Clicca **"Nuova Suite"**
2. Compila:
   - **Nome**: es. `anagrafiche_crud`
   - **Descrizione**: descrizione del test
   - **Modulo Target**: es. `anagrafiche`, `soggetti`, `ruoli`
   - **Tipo Test**: `CRUD` (default)

#### Metodo B: Generazione Automatica
1. Clicca **"Genera Suite"**
2. Compila:
   - **Nome Modulo**: es. `soggetti`
   - **Endpoint Base**: es. `/soggetti`
   - **Tipo**: `CRUD` o `Validazione`

Il sistema genera automaticamente i test case:
- List records (GET)
- Create record (POST)
- Read single record (GET)
- Update record (PUT)
- Delete record (DELETE)

### 2. Aggiungere Test Cases

1. Clicca **"+ Test"** accanto alla test suite
2. Compila i campi:
   - **Nome**: nome descrittivo del test
   - **Tipo**: create, read, update, delete, validation, api
   - **Metodo**: GET, POST, PUT, DELETE
   - **Endpoint**: percorso API (es. `/api/v1/soggetti`)
   - **Payload**: dati JSON per POST/PUT
   - **Status Atteso**: codice HTTP atteso (es. 200, 201, 204)

### 3. Eseguire i Test

1. Clicca **"Esegui"** sulla test suite
2. Attendi il completamento
3. Visualizza i risultati:
   - ✅ Test passati
   - ❌ Test falliti
   - ⚠️ Errori

### 4. Cambiare Stato del Modulo

Dopo test completati:
1. Seleziona il nuovo stato dal dropdown
2. Il sistema valida la transizione
3. Solo se tutti i test passano → possibile passare a `testato`

### 5. Esportare Report

Nella tab **"Storico Esecuzioni"**:
1. Clicca **"Report"** sull'esecuzione desiderata
2. Scarica un file di testo con:
   - Esito finale
   - Numero test passati/falliti
   - Durata
   - Dettagli errori

## Endpoint API

| Metodo | Endpoint | Descrizione |
|--------|----------|-------------|
| GET | `/api/v1/tests/suites` | Lista test suites |
| POST | `/api/v1/tests/suites` | Crea test suite |
| POST | `/api/v1/tests/suites/<id>/run` | Esegui test suite |
| GET | `/api/v1/tests/executions` | Lista esecuzioni |
| POST | `/api/v1/tests/generate` | Genera suite automatica |
| POST | `/api/v1/tests/module/status` | Cambia stato modulo |

## Test esistenti

Per i moduli standard di FlaskERP, puoi generare queste suite:

| Modulo | Endpoint Base | Comandi Generazione |
|--------|---------------|---------------------|
| Soggetti | `/soggetti` | Generate con tipo CRUD |
| Ruoli | `/ruoli` | Generate con tipo CRUD |
| Indirizzi | `/indirizzi` | Generate con tipo CRUD |
| Contatti | `/contatti` | Generate con tipo CRUD |
| Comuni | `/comuni` | Generate con tipo CRUD |
| Prodotti | `/products` | Generate con tipo CRUD |

## Best Practices

1. **Test frequenti**: Esegui i test dopo ogni modifica al modulo
2. **Report sempre**: Esporta i report dopo ogni esecuzione
3. **Stato corretto**: Non pubblicare mai un modulo senza passare per `testato`
4. **Test mirati**: Aggiungi test specifici per casi edge (validazione campi, duplicati)
5. **Isolamento**: Usa il database di test per non influenzare la produzione

## Database di Test

Per un ambiente di test isolato:

1. Crea un database separato: `flaskerp_test`
2. Esegui le migrazioni sul database di test
3. Configura l'env `TESTING=true` o usa il parametro `environment='test'` nelle chiamate API

## Risoluzione Problemi

### Test falliti
- Verifica che l'endpoint sia corretto
- Controlla il payload JSON
- Assicurati che il modulo esista e sia abilitato

### Transizioni stato non consentite
- `bozza` → solo `in_test`
- `in_test` → `testato` (se test passano) o `bozza`
- `testato` → solo `pubblicato`
- `pubblicato` → solo `obsoleto`
