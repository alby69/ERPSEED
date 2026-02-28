# AI Assistant - Guida all'Agente AI

## Introduzione

L'AI Assistant è un assistente che ti aiuta a costruire il tuo ERP usando il linguaggio naturale. Invece di dover navigare interfacce e configurare manualmente, puoi semplicemente descrivere quello che ti serve e l'AI si occupa del resto.

Questa funzionalità sfrutta il quarto pilastro di FlaskERP: il Self-Modifying Code. L'AI genera configurazioni che il sistema applica automaticamente.

---

## Come Funziona

### Flusso di Lavoro

```
Tu descrivi → AI comprende → AI genera config → Sistema applica → Risultato
```

1. **Descrivi** la tua esigenza in italiano o inglese
2. **L'AI analizza** e estrae entità, campi, relazioni
3. **L'AI genera** la configurazione per il Builder
4. **Il sistema applica** la configurazione automaticamente
5. **Il risultato** è pronto per l'uso

### Esempi Pratici

**Esempio 1: Modello Semplice**

> "Voglio un modulo per gestire i miei fornitori con nome, indirizzo, telefono e email."

L'AI genera:
- Modello "Fornitore"
- Campi: nome, indirizzo, telefono, email
- API e interfaccia

**Esempio 2: Con Relazioni**

> "Creo un modulo ordini collegato ai clienti. Ogni ordine ha data, totale e stato."

L'AI genera:
- Modello "Ordine" 
- Relazione al modulo Clienti
- Campi: data, totale, stato
- Ordine "cliente" di tipo relation

**Esempio 3: Complesso**

> "Serve un sistema per tracciare i macchinari con: nome, marca, modello, data acquisto, data prossima manutenzione, stato (attivo/fermo/rotto), e collegato al fornitore di ricambi."

L'AI genera:
- Modello "Macchinario"
- Relazione a Fornitore
- Campi con tipi appropriati
- Select per stato

---

## Stato di Implementazione

| Componente | Stato | Note |
|------------|-------|------|
| Architettura base | ✅ Completo | Service + API |
| Integrazione LLM (OpenRouter) | ✅ Completo | NVIDIA Nemotron, Qwen3 |
| Generazione modelli da linguaggio naturale | ✅ Completo | Genera JSON config |
| Interfaccia chat frontend | ✅ Completo | Modal con chat |
| Preview JSON modificabile | ✅ Completo | Modale con TextArea |
| Applicazione configurazione al DB | ✅ Completo | Crea modelli, campi, tabelle |
| Autenticazione JWT | ⚠️ Disabilitata | Disabilitata per testing |

---

## Utilizzo

1. Vai su **Administration → AI Assistant** nel menu
2. Descrivi il modulo che vuoi creare
3. Visualizza l'anteprima JSON
4. Modifica se necessario
5. Clicca "Applica al Progetto"

### Accesso

L'AI Assistant è accessibile dall'interfaccia principale attraverso:

- Menu **Administration → AI Assistant** (path: `/ai-assistant`)
- Un endpoint API per integrazioni

### Come Comunicare

**Sii specifico**: Più dettagli fornisci, migliore è il risultato.

**Includi**:
- Nome delle entità
- Campi necessari
- Eventuali relazioni
- Comportamenti speciali

**Esempio dettagliato**:

> "Crea un modulo 'Progetti' con: nome progetto (testo), cliente (collegato a Clienti), data inizio, data fine prevista, budget, stato (bozza, attivo, completato, sospeso), responsabile (collegato a Utenti)."

---

## Implementazione

### Architettura

L'AI Assistant è composto da:

- **Backend Service**: `backend/ai/service.py`
- **Backend API**: `backend/ai/api.py`
- **Frontend**: `frontend/src/components/ui/AIAssistant.jsx`

### Stack Tecnologico

- **LLM**: OpenRouter con modelli `nvidia/nemotron-nano-9b-v2:free` e `qwen/qwen3-coder:free`
- **Frontend**: React con Ant Design (Modal, List, Input)
- **API**: Flask REST endpoints con Flask-Smorest

### Endpoint API

| Endpoint | Metodo | Autenticazione | Descrizione |
|----------|--------|----------------|-------------|
| `/api/ai/chat` | POST | JWT | Chat generale |
| `/api/ai/generate` | POST | ❌ Disabilitata | Genera config ERP |
| `/api/ai/suggestions` | POST | JWT | Suggerimenti miglioramento |
| `/api/ai/models` | GET | JWT | Lista modelli disponibili |

---

## Funzionalità Supportate

### Creazione Modelli

L'AI può creare:
- Modelli con tutti i tipi di campo (string, text, integer, decimal, boolean, date, select, relation)
- Relazioni tra modelli
- Validazioni (required, unique)
- Descrizioni

### Configurazione

L'AI può configurare:
- Nomi tabella (automatici dal modello)
- Label dei campi
- Descrizioni

### Suggerimenti

L'AI può suggerire:
- Strutture dati basate sul tuo business
- Miglioramenti a modelli esistenti
- Best practices

---

## Limitazioni

L'AI è uno strumento potente ma ha limitazioni:

- Non può creare logica di business complessa (hook, workflow)
- Non può sostituire la conoscenza domain-specific
- Le configurazioni generate vanno sempre verificate

**Consiglio**: Usa l'AI come punto di partenza, poi raffina con il Builder.

---

## Integrazione API

Puoi usare l'AI Assistant via API per integrazioni:

```
POST /api/ai/generate
{
  "request": "Crea modulo per gestire fornitori",
  "project_id": 1
}
```

Risposta:
```json
{
  "success": true,
  "config": {
    "models": [
      {
        "name": "Fornitore",
        "table": "fornitori",
        "fields": [...]
      }
    ]
  },
  "created_models": ["Fornitore"],
  "message": "Ho creato il modello Fornitori con i campi richiesti."
}
```

---

## TODO - Completamento

Le seguenti funzionalità sono in corso o da completare:

### 1. ✅ Collegare "Applica al Progetto" al backend [COMPLETATO]

**Implementato**:
- Endpoint `POST /api/ai/apply` in `backend/ai/api.py`
- Frontend collegato in `frontend/src/components/ui/AIAssistant.jsx`
- Crea modelli, campi e tabelle nel database

### 2. Ripristinare autenticazione JWT

**Problema**: L'endpoint `/api/ai/generate` ha `@jwt_required()` disabilitato per testing.

**Soluzione**: Ripristinare l'autenticazione prima del rilascio in produzione.

```python
@blp.route("/generate")
class AIGenerate(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()  # <-- Ripristinare
    def post(self):
        ...
```

### 3. Testare flow completo

Testare l'intero flusso:
1. Generazione → edit JSON → applica → modello creato
2. Verificare che i modelli appaiano nel Builder
3. Verificare che le tabelle siano create nel DB

---

## Best Practices

### Per ottenere risultati migliori

1. **Inizia semplice**: Prima richieste basiche, poi complesse
2. **Sii iterativo**: Raffina il risultato passo dopo passo
3. **Verifica sempre**: Controlla ciò che l'AI ha generato
4. **Correggi**: Se qualcosa non è giusto, spiega all'AI come correggerlo

### Esempio Conversazione

```
Tu: Crea modulo clienti
AI: Ho creato il modulo Clienti con i campi base.

Tu: Aggiungi anche partita iva e codice fiscale
AI: Ho aggiunto i campi partita_iva e codice_fiscale al modulo Clienti.

Tu: Collegalo al modulo ordini
AI: Ho creato la relazione tra Clienti e Ordini. Ora ogni cliente può avere molti ordini.
```

---

## Roadmap

L'AI Assistant è in fase di sviluppo. Prossime funzionalità:

- [x] Generazione modelli da linguaggio naturale
- [x] Interfaccia chat
- [x] Preview JSON modificabile
- [x] Applicazione configurazione al database
- [ ] Ripristino autenticazione JWT
- [ ] Generazione automatica test
- [ ] Creazione workflow (integrazione con Workflow Builder)
- [ ] Suggerimenti intelligenti
- [ ] Integrazione Marketplace

---

## Conclusione

L'AI Assistant rende FlaskERP ancora più accessibile. Anche senza conoscenze tecniche, puoi costruire il tuo sistema gestionale semplicemente descrivendo ciò che ti serve.

Prova e vedrai: descrivere in linguaggio naturale quello che vuoi è spesso più veloce che cliccare tra mille opzioni.

---

*Riferimenti*:
- TODO: [10_TODO.md](../10_TODO.md)
- Automazione: [01B_AUTOMAZIONE.md](01B_AUTOMAZIONE.md)

*Documento aggiornato: Febbraio 2026*
