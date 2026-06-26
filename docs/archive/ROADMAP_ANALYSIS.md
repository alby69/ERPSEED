# Analisi Roadmap e Piano di Implementazione ERPSEED

## 1. Analisi dello Stato Attuale

In data 2026-03-24, è stata effettuata una revisione della `ROADMAP.md` rispetto al codebase attuale.

### Fase 0: Stabilizzazione Critica
*   **0.1 Requirements**: Completato.
*   **0.2 Fix BaseModel duplicati**: In corso. Identificate duplicazioni tra `backend/models/base.py` e `backend/core/models/base.py`. Unificazione completata verso il core.
*   **0.3 Test base**: Da potenziare.
*   **0.4 Documentazione API**: Completato.

### Fase 1: Refactoring DRY
*   **1.1 Centralizzare paginate()**: Implementato in `backend/core/utils/utils.py`.
*   **1.2 Centralizzare check_unique()**: Implementato in `backend/core/utils/utils.py`.
*   **1.3 Utility safe_json_parse()**: Implementato in `backend/core/utils/utils.py`.
*   **1.4 BaseService**: Creato in `backend/core/services/base.py` per fornire operazioni CRUD standard.

### Fase 2: Refactoring KISS
*   **2.1 Split DynamicApiService**: Completato. Il servizio è stato suddiviso in:
    *   `FieldValidator`: Validazione e conversione tipi.
    *   `QueryBuilder`: Costruzione query relazionali complesse.
    *   `ResultProcessor`: Elaborazione risultati e calcolo formule.
*   **2.3 Standardizzare pattern Service**: In corso con l'adozione di `BaseService`.

---

## 2. Piano di Implementazione Dettagliato

Il seguente piano descrive i passi necessari per completare la roadmap mantenendo i principi DRY, KISS e il disaccoppiamento.

### Passo 1: Consolidamento Infrastruttura (Settimana 1)
*   **Azione**: Migrazione completa di tutti i modelli esistenti al nuovo `BaseModel` unificato.
*   **Motivazione**: Garantire che il Soft Delete e i metodi utility (`to_dict`) siano disponibili ovunque.
*   **DRY**: Unica sorgente di verità per la struttura base dei dati.

### Passo 2: Rafforzamento della Logica di Business (Settimana 2)
*   **Azione**: Refactoring dei servizi `UserService` e `ProjectService` per ereditare da `BaseService`.
*   **Motivazione**: Ridurre il codice boilerplate per le operazioni CRUD standard.
*   **KISS**: Servizi focalizzati solo sulla logica specifica, non sulla gestione del DB.

### Passo 3: Espansione Funzionalità Dinamiche (Settimana 3-4)
*   **Azione**: Implementazione del modulo "Batch Import/Export UI" (Fase 3.1).
*   **Azione**: Sostituzione di `eval()` con un parser sicuro (es. `simpleeval`) nel `ResultProcessor`.
*   **Sicurezza**: Mitigazione dei rischi di RCE nelle formule dinamiche.

### Passo 4: Ottimizzazione e Sicurezza (Settimana 5+)
*   **Azione**: Implementazione di Rate Limiting e Caching (Fase 4).
*   **Performance**: Utilizzo di Redis per velocizzare le letture dei modelli dinamici più frequenti.

---

## 3. Guida al Refactoring per Sviluppatori

Quando si modifica un modulo esistente:
1.  **Verificare il BaseModel**: Assicurarsi di importare da `backend.core.models.base`.
2.  **Usare BaseService**: Se il servizio fa CRUD semplice, non riscrivere i metodi, usa quelli ereditati.
3.  **Disaccoppiamento**: Non importare servizi direttamente se possibile; usare il pattern `ServiceProxy` o l'iniezione tramite container.
