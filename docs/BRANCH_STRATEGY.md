# Strategia dei Branch ERPSeed

> ⚠️ **Nota di Sincronizzazione:** Come descritto in [AGENTMESH.md](AGENTMESH.md#fase-1-consolidamento-e-bridge-completato), i branch storici `erpseed/backend` ed `erpseed/frontend` sono stati unificati nel ramo principale `main`. Lo sviluppo attivo e l'integrazione avvengono direttamente su `main` tramite feature branch.

---

## Flusso di Lavoro Attuale

### Ramo Principale: `main`
Il branch `main` costituisce l'unica sorgente di verità del repository mono-repo e contiene sia il backend (`backend/`) che il frontend (`frontend/`) in uno stato coerente e testato.

### Sviluppo di Nuove Feature
1. **Creazione Feature Branch**: Crea un branch dedicato a partire da `main` (es. `feature/nome-feature` o `fix/nome-bug`).
2. **Commit Atomici**: Se la feature richiede modifiche sia al backend che al frontend, includi i cambi nello stesso branch/pull request.
3. **Pull Request**: Apri una Pull Request verso `main`. Assicurati che i test passino prima del merge.

---

## Branch Storici (Remote)

Per consultazione storica o refactoring mirati, rimangono presenti sui repository remoti:
- `remotes/origin/erpseed/backend`: storia dello sviluppo iniziale della logica CQRS.
- `remotes/origin/erpseed/frontend`: storia dello sviluppo iniziale del Visual Builder React.

---

*Ultimo aggiornamento: 2026-06-11*
