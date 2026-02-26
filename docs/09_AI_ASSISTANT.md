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

**Esempio 1: Modulo Semplice**

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

## Implementazione

### Architettura

L'AI Assistant è composto da:

- **Backend**: `backend/ai/service.py` e `backend/ai/api.py`
- **Frontend**: `frontend/src/components/ui/AIAssistant.jsx`
- **Integrazione**: Pulsante nella sidebar

### Stack Tecnologico

- **LLM**: OpenRouter con modello `nvidia/nemotron-nano-9b-v2:free`
- **Frontend**: React con компонент chat
- **API**: Flask REST endpoints

### Endpoint API

| Endpoint | Metodo | Descrizione |
|----------|--------|-------------|
| `/api/ai/chat` | POST | Chat generale |
| `/api/ai/generate` | POST | Genera config ERP da linguaggio naturale |
| `/api/ai/suggestions` | POST | Suggerimenti miglioramento |
| `/api/ai/models` | GET | Lista modelli disponibili |

### Utilizzo

1. Clicca il pulsante **AI Assistant** nella sidebar
2. Descrivi il modulo che vuoi creare
3. Visualizza l'anteprima JSON
4. Modifica se necessario
5. Clicca "Applica al Progetto"

### Accesso

L'AI Assistant è accessibile dall'interfaccia principale attraverso:

- Un pulsante di chat
- Un pannello dedicato
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

## Funzionalità Supportate

### Creazione Modelli

L'AI può creare:
- Modelli con tutti i tipi di campo
- Relazioni tra modelli
- Validazioni
- Viste alternative (Kanban)

### Configurazione

L'AI può configurare:
- Permessi
- Menu di navigazione
- Template

### Suggerimenti

L'AI può suggerire:
- Strutture dati basate sul tuo business
- Miglioramenti a modelli esistenti
- Best practices

---

## Limitazioni

L'AI è uno strumento potente ma ha limitazioni:

- Non può creare logica di business complessa
- Non può sostituire la conoscenza domain-specific
- Le configurazioni generate vanno sempre verificate

**Consiglio**: Usa l'AI come punto di partenza, poi raffina con il Builder.

---

## Integrazione API

Puoi usare l'AI Assistant via API per integrazioni:

```
POST /api/v1/ai/assistant
{
  "message": "Crea modulo per gestire fornitori",
  "project_id": 1
}
```

Risposta:
```json
{
  "status": "success",
  "created": ["Fornitore"],
  "message": "Ho creato il modulo Fornitori con i campi richiesti."
}
```

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
- [ ] Applicazione configurazione al database
- [ ] Generazione automatica test
- [ ] Creazione workflow
- [ ] Suggerimenti intelligenti
- [ ] Integrazione Marketplace

---

## Conclusione

L'AI Assistant rende FlaskERP ancora più accessibile. Anche senza conoscenze tecniche, puoi costruire il tuo sistema gestionale semplicemente descrivendo ciò che ti serve.

Prova e vedrai: descrivere in linguaggio naturale quello che vuoi è spesso più veloce che cliccare tra mille opzioni.

---

*Documento aggiornato: Febbraio 2026*
