# ERPaaS - ERP as a Service Platform

## Proposta Tecnica e Funzionale

---

## 1. Panoramica del Progetto

**Nome:** ERPaaS (ERP as a Service)  
**Concept:** Piattaforma SaaS che consente la creazione on-demand di sistemi ERP personalizzati  
**Target:** 
- Utenti non tecnici che desiderano un ERP senza competenze specifiche
- Consulenti IT che creano ERP per i loro clienti

### Flusso Base

```
Utente → Registrazione → Configurazione Wizard → Acquisto → ERP Provisioned
```

---

## 2. Architettura

### 2.1 Multi-Repo Structure

```
┌─────────────────────────────────────────────────────────────┐
│                     PLATTAFORMA CENTRALE                      │
├─────────────────────────────────────────────────────────────┤
│  • Portale Pubblico (vetrina, registrazione, acquisto)     │
│  • Pannello Admin (gestione clienti, abbonamenti)           │
│  • Builder Studio (configurazione ERP)                      │
│  • Marketplace Template                                     │
│  • Marketplace Moduli                                      │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   ERP #1     │   │   ERP #2     │   │   ERP #N     │
│  (Docker)    │   │  (Docker)    │   │  (Docker)    │
│  Tenant A    │   │  Tenant B    │   │  Tenant Z    │
└──────────────┘   └──────────────┘   └──────────────┘
```

### 2.2 Componenti

| Componente | Descrizione |
|------------|-------------|
| **Platform Core** | Backend condiviso per auth, billing, gestione tenant |
| **Template Catalog** | Catalogo template preconfigurati |
| **Module Registry** | Registro moduli disponibili |
| **Provisioning Engine** | Servizio che crea/deploya nuove istanze ERP |
| **Builder Studio** | Interfaccia avanzata per configuazione |
| **Marketplace** | Store per template e moduli |

---

## 3. Customer Journey

### Step 1: Scoperta
- Visitare vetrina template
- Visualizzare feature e prezzi
- Leggere documentazione

### Step 2: Configurazione (Wizard Guidato)
L'utente descrive cosa vuole:
> "Voglio un ERP per un negozio di abbigliamento"

Il sistema:
- Analizza la richiesta testuale
- Suggerisce template base
- Consiglia moduli rilevanti

### Step 3: Acquisto
- Scelta piano mensile/annuale
- Pagamento Stripe
- Provisioning automatico

### Step 4: Utilizzo
- URL personale: `azienda.erpplatform.com`
- Accesso immediato all'ERP configurato

---

## 4. Template Predefiniti

Un **Template** = insieme preconfigurato di:
- Moduli applicativi
- Workflow predefiniti
- Dashboard default
- Report template
- Dati di esempio

### Template Disponibili

| Template | Moduli Inclusi | Target | Prezzo Starter |
|---------|---------------|--------|----------------|
| **Startup** | Anagrafiche, Tasks, Note, Dashboard | Piccole attività | €29/mese |
| **Negozio** | Magazzino, Vendite, Clienti, Fatturazione | Retail | €49/mese |
| **Professionista** | Fatturazione, Scadenze, Clienti, Anagrafiche | Commercialisti | €39/mese |
| **Manufacturing** | Produzione, Ordini, Fornitori, Magazzino | Fabbriche | €79/mese |
| **Services** | Progetti, Timesheet, Fatturazione, Clienti | Consulenti | €59/mese |
| **Enterprise** | Tutti i moduli + custom | Grandi aziende | €299/mese |

---

## 5. Moduli Applicativi

Un **Modulo** = blocco funzionale che aggiunge feature all'ERP.

### 5.1 Struttura Modulo

```json
{
  "id": "accounting",
  "name": "Contabilità",
  "description": "Modulo base per la gestione contabile",
  "version": "1.0.0",
  "dependencies": [],
  "entities": ["Account", "Entry", "VatCode"],
  "workflows": ["auto_reconcile"],
  "dashboards": ["accounting_overview"],
  "permissions": ["accounting_admin", "accounting_view"]
}
```

### 5.2 Catalogo Moduli

| Categoria | Modulo | Descrizione | Obbligatorio |
|-----------|--------|-------------|--------------|
| **Core** | Anagrafiche | Clienti, Fornitori, Contatti | Sì |
| **Core** | Utenti & Permessi | Team, ruoli, ACL | Sì |
| **Contabilità** | Contabilità | Piano conti, prima nota | Opzionale |
| **Contabilità** | Fatturazione | Fatture elettroniche, PDF | Opzionale |
| **Contabilità** | Scadenze | Pagamenti, solleciti | Opzionale |
| **Magazzino** | Inventario | Prodotti, stock, movimenti | Opzionale |
| **Magazzino** | Ordini | Acquisto, Vendita | Opzionale |
| **Vendite** | POS | Punto vendita, scontrini | Opzionale |
| **Vendite** | E-commerce | Integrazione negozio online | Opzionale |
| **CRM** | Leads | Pipeline commerciali | Opzionale |
| **CRM** | Campagne | Email, promozioni | Opzionale |
| **Produzione** | Distinte | BOM, lavorazioni | Opzionale |
| **Produzione** | Ordini Lavorazione | Cadenza produzione | Opzionale |
| **Progetti** | Project Management | Gantt, milestone, task | Opzionale |
| **HR** | Timesheet | Registrazione ore | Opzionale |

### 5.3 Moduli Personalizzati

Gli utenti avanzati o i consulenti possono creare moduli custom:
- Definizione entità
- Creazione campi
- Configurazione relazioni
- Workflow associati

---

## 6. Wizard di Configurazione

Interfaccia semplificata per utenti non tecnici.

### Step 1: Scegli Template
- Visualizzazione card template
- Preview feature
- "Non so quale scegliere" → Quiz guidato

### Step 2: Nome & Branding
| Campo | Descrizione |
|-------|------------|
| Nome Azienda | Testo, richiesto |
| Logo | Upload immagine |
| Colore Primario | Color picker |
| URL | subdomain.erpplatform.com |

### Step 3: Seleziona Moduli
- Lista moduli consigliati (based on template)
- Possibilità aggiungere/rimuovere
- "Perché ti serve?" → Tooltip esplicativo
- Dipendenze automatiche gestite

### Step 4: Dati Iniziali (Opzionale)
- Importa anagrafiche da CSV
- Configura aliquote IVA default
- Imposta anno contabile

### Step 5: Abbonamento
- Piano mensile/annuale
- Metodo pagamento
- Riepilogo costi
- Provisioning automatico

---

## 7. Builder Studio

Interfaccia avanzata per admin della piattaforma e consulenti.

### 7.1 Funzionalità

| Sezione | Descrizione |
|---------|-------------|
| **Entità** | Crea/modifica tabelle, campi, relazioni |
| **Workflow** | Definisci automazioni basate su eventi |
| **Report** | Crea dashboard e stampe custom |
| **API** | Esponi dati verso esterne |
| **Integrazioni** | Webhook, Zapier, API REST |

### 7.2 Regole di Utilizzo

| Ruolo | Accesso |
|-------|---------|
| **Cliente Finale** | Solo moduli approvati, configurazione limitata |
| **Consulente** | Template custom + moduli propri |
| **Admin Platform** | Accesso completo |

---

## 8. Provisioning Engine

### 8.1 Flusso Provisioning

```
1. Ordine confermato
       ↓
2. Crea database PostgreSQL dedicato
       ↓
3. Clona template base (tabelle, dati)
       ↓
4. Applica configurazione utente
       ↓
5. Crea container Docker
       ↓
6. Configura dominio/subdomain
       ↓
7. Invia credenziali email
```

### 8.2 Stack Tecnico

| Componente | Tecnologia |
|------------|------------|
| Orchestrazione | Docker Compose / Kubernetes |
| Database | PostgreSQL (uno per tenant o connection pooling) |
| Storage | S3/MinIO per file e upload |
| DNS | CloudFlare API |
| Monitoring | Prometheus + Grafana |

---

## 9. Modello di Business

### 9.1 Piano Prezzi

| Piano | Prezzo | ERP | Utenti | Storage | Moduli |
|-------|--------|-----|--------|---------|--------|
| **Starter** | €29/mese | 1 | 3 | 1GB | Base |
| **Business** | €99/mese | 1 | 10 | 10GB | Tutti |
| **Professional** | €249/mese | 3 | 25 | 25GB | Tutti + Custom |
| **Enterprise** | €499/mese | Illimitati | Illimitati | 100GB | Tutti + Custom + SLA |

### 9.2 Ricavi Aggiuntivi

- **Template Custom**: €500-2000 una tantum
- **Moduli Premium**: €10-50/mese
- **Consulenza Setup**: €200-1000 una tantum
- **Formazione**: €100-500/sessione

---

## 10. Roadmap di Sviluppo

### Fase 1: Foundation (Mesi 1-3)
- [ ] Architettura core multi-tenant
- [ ] Sistema auth e gestione utenti
- [ ] Database design per tenant
- [ ] Provisioning engine base
- [ ] Dashboard admin

### Fase 2: Template Core (Mese 4)
- [ ] Template "Startup" pronto
- [ ] Template "Negozio" pronto
- [ ] Template "Professionista" pronto

### Fase 3: Wizard & Checkout (Mese 5)
- [ ] Wizard configurazione guidato
- [ ] Integrazione Stripe
- [ ] Provisioning automatico

### Fase 4: Moduli Base (Mesi 6-7)
- [ ] Modulo Anagrafiche
- [ ] Modulo Magazzino
- [ ] Modulo Fatturazione

### Fase 5: Builder Studio (Mesi 8-10)
- [ ] Creazione entità custom
- [ ] Workflow builder
- [ ] Report builder

### Fase 6: Marketplace (Mesi 11-12)
- [ ] Vetrina template pubblica
- [ ] Store moduli
- [ ] Sistema recensioni

---

## 11. Tech Stack Proposto

### Frontend
| Componente | Tecnologia |
|------------|------------|
| Platform Frontend | React + TypeScript |
| UI Framework | Ant Design / Tailwind |
| State | Zustand / Redux Toolkit |
| i18n | i18next |

### Backend
| Componente | Tecnologia |
|------------|------------|
| API Gateway | FastAPI / Flask |
| ORM | SQLAlchemy + Alembic |
| Auth | OAuth2 + JWT |
| Task Queue | Celery + Redis |
| API Documentation | OpenAPI/Swagger |

### Infrastructure
| Componente | Tecnologia |
|------------|------------|
| Database | PostgreSQL |
| Cache | Redis |
| Storage | S3 / MinIO |
| Container | Docker + Docker Compose |
| Cloud | AWS / DigitalOcean / Hetzner |
| CI/CD | GitHub Actions |

---

## 12. Glossario

| Termine | Definizione |
|---------|-------------|
| **Tenant** | Singola istanza ERP di un cliente |
| **Template** | Configurazione preimpostata di moduli e funzionalità |
| **Modulo** | Blocco funzionale aggiuntivo per l'ERP |
| **Provisioning** | Processo di creazione di una nuova istanza ERP |
| **Wizard** | Interfaccia guidata step-by-step |
| **Builder** | Interfaccia avanzata per configurazione |

---

## 13. Domande Aperte

1. **Database**: Un database per ogni cliente o schema condiviso?
2. **Deploy**: Kubernetes (complesso) o Docker Swarm (semplice)?
3. **Payment**: Solo Stripe o anche PayPal?
4. **AI**: Implementare suggerimenti basati su AI per la configurazione?
5. **White-label**: Permettere branding completamente personalizzato?

---

*Documento generato il 16 Febbraio 2026*
*Progetto: FlaskERP ERPaaS Platform*
