# Integrazioni - API, Webhooks e Plugin

## Panoramica

FlaskERP è progettato per integrarsi con il mondo esterno. Attraverso le API REST, i webhooks e il sistema plugin, puoi connettere FlaskERP con altri sistemi, automatizzare flussi di lavoro e estendere le funzionalità.

---

## API REST

### Introduzione alle API

Tutte le funzionalità di FlaskERP sono accessibili via API. Questo significa che puoi:

- Integrare con siti web
- Creare APP mobile
- Automatizzare operazioni
- Sincronizzare dati con altri sistemi

### Autenticazione

Le API usano JWT per l'autenticazione. Per ogni chiamata devi includere il token:

```
Authorization: Bearer <token>
```

Per ottenere un token, effettua il login:

```
POST /api/v1/auth/login
{
  "email": "utente@esempio.it",
  "password": "lapassword"
}
```

La risposta contiene:
- `access_token`: Da usare nelle chiamate API
- `refresh_token`: Per rinnovare il token quando scade

### Endpoint Principali

| Risorsa | Metodo | Endpoint |
|---------|--------|----------|
| Progetti | GET | /api/projects |
| Modelli | GET | /api/projects/{id}/models |
| Dati | GET | /api/projects/{id}/data/{model} |
| Utenti | GET/POST | /api/v1/users |

### Esempio: Leggere Dati

Per leggere i clienti dal tuo progetto:

```bash
curl -X GET "http://localhost:5000/api/projects/1/data/clienti" \
  -H "Authorization: Bearer <token>"
```

### Esempio: Creare un Record

```bash
curl -X POST "http://localhost:5000/api/projects/1/data/clienti" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"nome": "Mario Rossi", "email": "mario@esempio.it"}'
```

---

## Webhooks

I webhooks permettono a FlaskERP di notificare altri sistemi quando accadono eventi.

### Configurare un Webhook

1. Vai su **Amministrazione → Webhooks**
2. Clicca **Nuovo Webhook**
3. Definisci:
   - **URL**: Dove inviare la notifica
   - **Eventi**: Quali eventi attivano il webhook
   - **Secret**: Chiave per verificare l'autenticità

### Eventi Disponibili

**Utenti:**
- user.created
- user.updated
- user.deleted

**Progetti:**
- project.created
- project.updated

**Dati:**
- record.created
- record.updated
- record.deleted

**Moduli:**
- order.created
- order.confirmed
- invoice.created
- invoice.paid

### Payload del Webhook

Quando si attiva un webhook, FlaskERP invia un POST con:

```json
{
  "event": "record.created",
  "timestamp": "2026-02-26T10:00:00Z",
  "data": {
    "id": 123,
    "model": "clienti",
    "values": {...}
  }
}
```

### Sicurezza

Ogni webhook include un header `X-Webhook-Signature` che puoi verificare per assicurarti che la richiesta arrivi da FlaskERP.

---

## Sistema Plugin

I plugin permettono di estendere FlaskERP con funzionalità custom.

### Struttura di un Plugin

Un plugin è una directory con una struttura specifica:

```
mio_plugin/
├── __init__.py
├── plugin.py
├── models.py
├── api.py
└── static/
    └── frontend.js
```

### Creare un Plugin

1. Crea la directory in `backend/plugins/`
2. Definisci la classe del plugin
3. Registrala nel sistema

### Esempio Semplice

```python
from backend.plugins import BasePlugin

class MioPlugin(BasePlugin):
    name = "mio_plugin"
    version = "1.0.0"
    description = "Un plugin di esempio"
    
    def install(self):
        # Logica di installazione
        pass
    
    def uninstall(self):
        # Logica di disinstallazione
        pass
```

---

## Integrazioni Comuni

### E-commerce

Collega FlaskERP al tuo sito e-commerce:

- Sincronizzazione prodotti
- Import ordini automatico
- Aggiornamento giacenze

### Contabilità Esterna

Esporta dati per il tuo commercialista:

- Esportazione movimenti
- Generazione XML per fatturazione
- Integrazione con programmi contabili

### Marketing

Connetti con strumenti marketing:

- Sincronizzazione contatti
- Automazione inviti
- Tracking comportamenti

---

## Best Practices

### API

- Usa sempre HTTPS in produzione
- Gestisci correttamente i token
- Implementa retry per fallimenti temporanei
- Cache le risposte quando possibile

### Webhooks

- Verifica sempre la signature
- Implementa idempotenza
- Gestisci i retry del sender
- Logga gli invii per troubleshooting

### Plugin

- Testa in ambiente di sviluppo
- Segui le convenzioni del sistema
- Documenta il tuo plugin
- Gestisci le dipendenze

---

*Documento aggiornato: Febbraio 2026*
