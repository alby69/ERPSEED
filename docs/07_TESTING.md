# Testing - Guida al Test Runner

## Introduzione

Il Test Runner è uno strumento integrato in FlaskERP per verificare automaticamente la correttezza dei moduli. È pensato per garantire che tutto funzioni come previsto, sia per gli amministratori che per gli sviluppatori.

---

## Accedere al Test Runner

Vai su **Test Runner** dal menu di amministrazione o direttamente all'indirizzo `/test-runner`.

L'accesso è riservato agli amministratori.

---

## Concetti Fondamentali

### Test Suite

Una test suite è un contenitore che raggruppa test correlati. Ad esempio, una suite per il modulo "Clienti" contiene tutti i test specifici per quella parte.

### Test Case

Un test case è un singolo test che verifica un comportamento specifico. Ogni test ha:

- **Nome**: Identificativo del test
- **Tipo**: create, read, update, delete, validation
- **Metodo**: HTTP method (GET, POST, PUT, DELETE)
- **Endpoint**: URL dell'API da testare
- **Payload**: Dati per le chiamate POST/PUT
- **Status atteso**: Codice HTTP atteso

### Stati dei Moduli

Ogni modulo in FlaskERP ha uno stato:

| Stato | Significato |
|-------|-------------|
| Bozza | Mai testato |
| In Test | Test in corso |
| Testato | Test passati |
| Pubblicato | In produzione |
| Obsoleto | Non più usato |

---

## Creare Test Suite

### Metodo 1: Creazione Manuale

1. Clicca **Nuova Suite**
2. Compila:
   - **Nome**: Identificativo della suite
   - **Descrizione**: Cosa testa
   - **Modulo Target**: Quale modulo riguarda
   - **Tipo Test**: CRUD, validation, ecc.

### Metodo 2: Generazione Automatica

Il sistema può generare test base automaticamente:

1. Clicca **Genera Suite**
2. Indica:
   - **Modulo**: es. clienti, prodotti
   - **Endpoint Base**: es. /clienti
   - **Tipo**: CRUD o validazione

Il sistema crea automaticamente test per:
- List (GET)
- Create (POST)
- Read (GET singolo)
- Update (PUT)
- Delete (DELETE)

---

## Aggiungere Test Cases

Puoi aggiungere test specifici oltre a quelli generati:

1. Clicca **+ Test** sulla suite
2. Definisci:
   - **Nome**: Descrizione del test
   - **Tipo**: create/read/update/delete/validation
   - **Metodo**: GET/POST/PUT/DELETE
   - **Endpoint**: URL completa
   - **Payload**: JSON per POST/PUT
   - **Status atteso**: 200, 201, 204, ecc.

---

## Eseguire i Test

### Singola Suite

1. Clicca **Esegui** sulla suite
2. Attendi il completamento
3. Visualizza i risultati:
   - Test passati (verde)
   - Test falliti (rosso)
   - Errori (giallo)

### Suite Multiple

Puoi eseguire più suite contemporaneamente.

### Interpretare i Risultati

Dopo l'esecuzione vedrai:

- **Totale**: Numero di test eseguiti
- **Passati**: Test con successo
- **Falliti**: Test falliti
- **Errori**: Errori di esecuzione
- **Durata**: Tempo impiegato

---

## Gestire gli Stati

Dopo test completati con successo, puoi cambiare lo stato del modulo:

1. Seleziona il nuovo stato
2. Il sistema valida la transizione
3. Se i test passano, puoi passare a "Testato"

**Regola**: Solo con tutti i test passati puoi arrivare a "Testato" e poi "Pubblicato".

---

## Esempi Pratici

### Esempio 1: Testare un Nuovo Modulo

Hai creato un modulo "Preventivi" e vuoi verificare:

1. Crea suite "Preventivi - CRUD"
2. Usa generazione automatica
3. Esegui i test
4. Se passano, cambia stato in Testato

### Esempio 2: Test Dopo Modifica

Hai aggiunto un campo obbligatorio:

1. Apri la suite esistente
2. Aggiungi test che invia dati senza il nuovo campo
3. Verifica che il sistema rifiuti (status 400)

### Esempio 3: Verifica Permessi

Vuoi verificare che gli utenti Viewer non possano modificare:

1. Crea test con token di un utente Viewer
2. Prova a fare POST/PUT/DELETE
3. Verifica che risponda con 403

---

## Best Practices

### Frequenza

- Esegui test dopo ogni modifica significativa
- Non pubblicare mai senza test passati

### Copertura

- Copri i casi base (CRUD)
- Aggiungi test per casi edge
- Testa le validazioni

### Manutenzione

- Aggiorna i test quando cambi i moduli
- Rimuovi test obsoleti
- Documenta test complessi

---

## Problemi Comuni

### Test che Falliscono

- Verifica endpoint e payload
- Controlla che il modulo esista
- Consulta i dettagli dell'errore

### Transizioni Non Consentite

Ricorda le regole:
- Bozza → In Test
- In Test → Bozza o Testato (se passano)
- Testato → Pubblicato
- Pubblicato → Obsoleto

---

*Documento aggiornato: Febbraio 2026*
