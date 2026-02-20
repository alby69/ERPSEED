# FlaskERP - Introduzione e Fondamenti

## Cos'è FlaskERP

FlaskERP è un sistema ERP modulare e flessibile, costruito come un "Low-Code Engine" che permette di creare, estendere e gestire sistemi ERP complessi attraverso:

- **Architettura modulare**: Ogni funzionalità (Contabilità, Vendite, Magazzino) è un modulo separato
- **Builder integrato**: Creazione di nuove entità direttamente dall'interfaccia web
- **Multi-tenant**: Isolamento completo dei dati per ogni cliente
- **Codice adattivo**: Il sistema può generare codice automaticamente da configurazioni

---

## I Quattro Pilastri Teorici

### 1. Domain-Driven Design (DDD)

Il dominio come collante - ogni modulo ha un contesto delimitato con linguaggio condiviso:

```
Esempio nel nostro ERP:
┌─────────────────┐     ┌─────────────────┐
│     Soggetto    │────<│      Ruolo      │
└─────────────────┘     └─────────────────┘
        │
        ▼
┌─────────────────┐     ┌─────────────────┐
│    Indirizzo    │     │    Contatto    │
└─────────────────┘     └─────────────────┘
```

### 2. Plugin Architecture

Moduli che si agganciano - estensioni senza modificare il core:

```
┌─────────────────────────────────────────┐
│              CORE SYSTEM                  │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐  │
│  │Plugin   │ │Plugin   │ │Plugin   │  │
│  │Accounting│ │   HR    │ │Inventory│  │
│  └─────────┘ └─────────┘ └─────────┘  │
│         └───────────┼───────────┘      │
│                     ▼                  │
│            ┌──────────────┐            │
│            │Plugin Registry│            │
│            └──────────────┘            │
└─────────────────────────────────────────┘
```

### 3. Metaprogramming

Codice che genera codice - il Builder crea automaticamente classi, API, schemi:

```python
# Esempio: creazione dinamica di entità
def create_entity_class(config):
    return type(config['name'], (Base,), {...})
```

### 4. Self-Modifying Code

Codice adattivo - modifiche a runtime senza riavvio:

- Hot Reload: ricarica moduli senza restart
- Expression Engine: valutazione formule dinamiche
- Hook System: estensione comportamento

---

## Entità Core (Mattoncini Base)

Le tabelle archetipiche sono i mattoncini fondamentali del sistema.

### Soggetto (Party)

Entità centrale: rappresenta qualsiasi persona o organizzazione.

```python
class Soggetto(BaseModel):
    __tablename__ = 'soggetti'
    
    codice = db.Column(db.String(50), unique=True)
    nome = db.Column(db.String(150), nullable=False)
    cognome = db.Column(db.String(100))
    ragione_sociale = db.Column(db.String(200))
    partita_iva = db.Column(db.String(50))
    codice_fiscale = db.Column(db.String(50))
    
    # Relazioni
    ruoli = db.relationship('SoggettoRuolo', back_populates='soggetto')
    indirizzi = db.relationship('SoggettoIndirizzo', back_populates='soggetto')
    contatti = db.relationship('SoggettoContatto', back_populates='soggetto')
```

### Ruolo

Un Soggetto può avere **molteplici ruoli**: Cliente, Fornitore, Dipendente, etc.

```python
class Ruolo(BaseModel):
    __tablename__ = 'ruoli'
    
    codice = db.Column(db.String(30), unique=True)  # CLIENTE, FORNITORE
    nome = db.Column(db.String(100))
    categoria = db.Column(db.String(50))  # commercial, operativo
```

### Indirizzo

Value Object per localizzazioni geografiche.

```python
class Indirizzo(BaseModel):
    __tablename__ = 'indirizzi'
    
    denominazione = db.Column(db.String(200))
    città = db.Column(db.String(100))
    provincia = db.Column(db.String(50))
    nazione = db.Column(db.String(2), default='IT')
    latitudine = db.Column(db.Float)
    longitudine = db.Column(db.Float)
```

### Contatto

Canali di contatto: email, telefono, fax, cellulare.

```python
class Contatto(BaseModel):
    __tablename__ = 'contatti'
    
    canale = db.Column(db.String(30))  # email, telefono, fax
    valore = db.Column(db.String(255))
    is_verified = db.Column(db.Boolean, default=False)
```

---

## Pattern Documentali

### Testata e Riga

Archetipi per documenti (Ordini, Fatture, DDT).

```python
class Testata(BaseModel):
    """Header del documento"""
    tipo_documento = db.Column(db.String(50))  # ORDINE_VENDITA, FATTURA
    codice = db.Column(db.String(50))
    data_documento = db.Column(db.Date)
    totale_documento = db.Column(db.Float)
    stato = db.Column(db.String(30), default='bozza')
    
    righe = db.relationship('Riga', back_populates='testata')


class Riga(BaseModel):
    """Dettaglio del documento"""
    testata_id = db.Column(db.Integer, db.ForeignKey('testate.id'))
    numero_riga = db.Column(db.Integer)
    descrizione = db.Column(db.String(500))
    quantita = db.Column(db.Float, default=1)
    prezzo_unitario = db.Column(db.Float)
    totale = db.Column(db.Float)
```

---

## Relazioni tra Entità

```
Soggetto (1) ──────< N > SoggettoRuolo >──N<── Ruolo
    │
    ├──< N > SoggettoIndirizzo >──N<── Indirizzo
    │
    └──< N > SoggettoContatto >──N<── Contatto

Testata (1) ──────< N > Riga
```

---

## Moduli Implementati

| Modulo | Stato | Descrizione |
|--------|-------|-------------|
| **Core Multi-Tenant** | ✅ | Tenant, User, Auth |
| **Parties** | ✅ | Soggetti, Ruoli |
| **Products** | ✅ | Prodotti, Categorie |
| **Sales** | ✅ | Ordini, Preventivi |
| **Inventory** | ✅ | Magazzino, Movimenti |
| **Purchases** | ✅ | Ordini fornitore |
| **Accounting** | 🟡 | Contabilità (70%) |
| **HR** | 🟡 | Dipendenti (50%) |
| **Dashboard** | 🟡 | KPI base |

---

## Quick Start

Per iniziare:

1. **Comprendere** i pilastri teorici (sezione sopra)
2. **Esplorare** i moduli disponibili
3. **Configurare** il primo modulo per il tuo tenant

Per sviluppare, consulta `08_GUIDE.md` per il manuale del Builder.

---

*Documento aggiornato: Febbraio 2026*
