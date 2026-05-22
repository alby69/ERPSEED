# Strategia dei Branch ERPSeed

Questo documento spiega la struttura dei branch del progetto e come utilizzarli correttamente per lo sviluppo.

## Branch Principali

### 1. `main`
Il branch `main` è il punto di integrazione stabile. Contiene sia il `backend/` che il `frontend/` in uno stato coerente.
- **Utilizzo**: Per test di integrazione e deploy di produzione.
- **Note**: Tutti i nuovi moduli testati e le feature completate vengono uniti qui.

### 2. `erpseed/backend`
Questo branch è focalizzato sul rifacimento modulare del backend seguendo il pattern **CQRS** (Command Query Responsibility Segregation).
- **Utilizzo**: Sviluppo di core logic, nuovi moduli backend, refactoring dell'architettura.
- **Caratteristiche**: Struttura a cartelle sotto `backend/modules/` più profonda (application, domain, infrastructure).

### 3. `erpseed/frontend`
Focalizzato sullo sviluppo dell'interfaccia utente React e del Visual Builder.
- **Utilizzo**: Modifiche ai componenti UI, miglioramenti del builder visuale, integrazione API lato client.
- **Caratteristiche**: Spesso contiene aggiornamenti alle API proxy e agli schema di validazione lato frontend.

## Flusso di Lavoro Consigliato

1. **Nuova Feature Backend**: Lavora su un branch derivato da `erpseed/backend`.
2. **Nuova Feature Frontend**: Lavora su un branch derivato da `erpseed/frontend`.
3. **Bugfix/Integrazione**: Lavora su `main` o un branch dedicato se richiede modifiche coordinate ad entrambi i lati.

## Sincronizzazione

A causa della natura divergente ma parallela dello sviluppo, i branch vengono periodicamente sincronizzati verso `main`.
Quando si effettua il merge tra questi branch, potrebbe essere necessario usare il flag `--allow-unrelated-histories` se i branch hanno divergenze strutturali significative nella storia dei commit.

## Testing su più Branch

Ogni branch mantiene la propria suite di test specifica:
- I test nel branch `backend` si concentrano sulla logica di business e i comandi CQRS.
- I test nel branch `frontend` si concentrano sulla resa dei componenti e la validazione degli stati.
- Il branch `main` esegue la suite completa di integrazione.
