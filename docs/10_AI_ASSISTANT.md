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

**Esempio 3: Complesso - Gestione Parco Mezzi**

> "Crea un sistema per gestione parco mezzi con veicoli, conducenti e manutenzione"

L'AI genera:
- Modello "Veicolo" (targa, marca, modello, anno, stato)
- Modello "Conducente" (nome, cognome, numero patente)
- Modello "Manutenzione" (veicolo, tipo, date, costo)
- Modello "Assegnazione" (veicolo-conducente)

---

## Stato di Implementazione

| Componente | Stato | Note |
|------------|-------|------|
| Architettura base | ✅ Completo | Service + API |
| Integrazione LLM (OpenRouter) | ✅ Completo | DeepSeek V3 |
| RAG Context Injection | ✅ Completo | Context from project schema |
| Tool Calling | ✅ Completo | generate_json, apply_config |
| Generazione modelli da linguaggio naturale | ✅ Completo | Genera JSON config |
| Interfaccia chat frontend | ✅ Completo | Modal con chat |
| Preview JSON modificabile | ✅ Completo | Modale con TextArea |
| Applicazione configurazione al DB | ✅ Completo | Crea modelli, campi, tabelle |
| Feedback Loop (Learning) | ✅ Completo | Salva conversazioni in DB |
| Cronologia conversazioni | ✅ Completo | UI con history panel |
| Autenticazione JWT | ✅ Abilitata | Protegge tutti gli endpoint |

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
- **Context Builder (RAG)**: `backend/ai/context.py`
- **Backend API**: `backend/ai/api.py`
- **Frontend**: `frontend/src/components/ui/AIAssistant.jsx`

### Stack Tecnologico

- **LLM**: OpenRouter con modello `deepseek/deepseek-chat-v3-0324`
- **RAG**: Context Injection dal schema del progetto
- **Tool Calling**: generate_json, apply_config, create_workflow
- **Database**: AIConversation per feedback loop
- **Frontend**: React con Ant Design (Modal, List, Input)

### Context Injection (RAG)

Il sistema costruisce automaticamente il contesto includendo:

- **Info Progetto**: nome, descrizione, titoli
- **Modelli Esistenti**: nomi, campi, tipi, relazioni
- **Blocchi UI**: blocchi personalizzati creati
- **Workflow**: workflow esistenti nel progetto
- **Conversazioni Precedenti**: per apprendimento incrementale

```python
# backend/ai/context.py
class AIContextBuilder:
    def build_context(self) -> str:
        # 1. Info progetto
        # 2. Modelli esistenti con campi
        # 3. Blocchi disponibili
        # 4. Workflow esistenti
        # 5. Cronologia conversazioni (per learning)
```

### Tool Calling

L'AI utilizza tool calling per azioni specifiche:

| Tool | Descrizione |
|------|-------------|
| `generate_json` | Genera config JSON senza applicare |
| `apply_config` | Applica la configurazione al DB |
| `create_workflow` | Crea un workflow automatico |

---

## Endpoint API

| Endpoint | Metodo | Autenticazione | Descrizione |
|----------|--------|----------------|-------------|
| `/api/ai/generate` | POST | JWT | Genera config ERP |
| `/api/ai/apply` | POST | JWT | Applica config al DB |
| `/api/ai/suggestions` | POST | JWT | Suggerimenti miglioramento |
| `/api/ai/models` | GET | JWT | Lista modelli disponibili |
| `/api/ai/conversations` | GET | JWT | Lista conversazioni |
| `/api/ai/feedback` | POST | JWT | Salva feedback per learning |

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

### Feedback Loop (Apprendimento)

Il sistema salva le conversazioni per apprendimento incrementale:

1. Ogni conversazione viene salvata nel DB
2. L'utente può dare feedback (thumbs up/down)
3. Le conversazioni di successo vengono usate come contesto per richieste future

```python
# backend/models.py
class AIConversation(BaseModel):
    project_id = db.Column(db.Integer, ...)
    user_message = db.Column(db.Text, ...)
    ai_response = db.Column(db.Text, ...)
    was_successful = db.Column(db.Boolean, ...)
    user_correction = db.Column(db.Text, ...)
    context_snapshot = db.Column(db.Text, ...)
```

---

## Integrazione API

### Generazione Configurazione

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

### Applicazione Configurazione

```
POST /api/ai/apply
{
  "config": { ... },
  "project_id": 1
}
```

### Salvataggio Feedback

```
POST /api/ai/feedback
{
  "conversation_id": 1,
  "was_successful": true,
  "rating": 5,
  "user_correction": null
}
```

---

## Best Practices

### Per ottenere risultati migliori

1. **Inizia semplice**: Prima richieste basiche, poi complesse
2. **Sii iterativo**: Raffina il risultato passo dopo passo
3. **Verifica sempre**: Controlla ciò che l'AI ha generato
4. **Correggi**: Se qualcosa non è giusto, spiega all'AI come correggerlo
5. **Dai feedback**: Usa i pulsanti thumbs up/down per migliorare il sistema

### Esempio Conversazione

```
Tu: Crea modulo clienti
AI: Ho creato il modulo Clienti con i campi base.

Tu: Aggiungi anche partita iva e codice fiscale
AI: Ho aggiunto i campi partita_iva e codice_fiscale al modulo Clienti.

Tu: Collegalo al modulo ordini
AI: Ho creato la relazione tra Clienti e Ordini. Ora ogni cliente può avere molti ordini.

[Tu: Thumbs Up]
→ Feedback salvato per apprendimento futuro
```

---

## Test - Gestione Parco Mezzi

Esempio di test eseguito con successo:

**Richiesta**: "Crea un sistema per gestione parco mezzi con veicoli, conducenti e manutenzione"

**Risultato**: L'AI ha generato 4 modelli:
- `Veicolo` (targa, marca, modello, anno, km, stato)
- `Conducente` (nome, cognome, patente)
- `Manutenzione` (veicolo, tipo, date, costo)
- `Assegnazione` (veicolo, conducente, date)

**Workflow**:
1. Generazione → 2. Preview JSON → 3. Applica → 4. Modelli creati nel DB

---

## Roadmap

L'AI Assistant è in fase di sviluppo. Prossime funzionalità:

- [x] Generazione modelli da linguaggio naturale
- [x] Interfaccia chat
- [x] Preview JSON modificabile
- [x] Applicazione configurazione al database
- [x] RAG Context Injection
- [x] Tool Calling
- [x] Feedback Loop per apprendimento
- [ ] Generazione automatica test
- [ ] Creazione workflow (integrazione con Workflow Builder)
- [ ] Suggerimenti intelligenti
- [ ] Integrazione Marketplace

---

## Conclusione

L'AI Assistant rende FlaskERP ancora più accessibile. Anche senza conoscenze tecniche, puoi costruire il tuo sistema gestionale semplicemente descrivendo ciò che ti serve.

Il sistema impara dalle conversazioni: più lo usi, migliore sarà il risultato grazie al feedback loop.

Prova e vedrai: descrivere in linguaggio naturale quello che vuoi è spesso più veloce che cliccare tra mille opzioni.

---

## File di Riferimento

- Service: `backend/ai/service.py`
- Context Builder: `backend/ai/context.py`
- API: `backend/ai/api.py`
- Modello: `backend/models.py` (AIConversation)
- Frontend: `frontend/src/components/ui/AIAssistant.jsx`

*Documento aggiornato: Marzo 2026*
