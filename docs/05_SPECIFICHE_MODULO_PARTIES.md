# ERPaaS - Specifiche Modulo Parties (Anagrafiche)

## Documento #05 - Modulo Anagrafiche

---

## 1. Panoramica Modulo

### 1.1 Descrizione

Il modulo **Parties** gestisce le anagrafiche di base del sistema:
- Clienti
- Fornitori
- Contatti
- Lead (potenziali clienti)

### 1.2 Entità

| Entità | Descrizione |
|--------|-------------|
| **Party** | Anagrafica principale (azienda/persona) |
| **PartyType** | Tipologia (cliente, fornitore, lead) |
| **PartyAddress** | Indirizzi multipli per party |
| **PartyContact** | Contatti email, telefono |
| **PartyGroup** | Gruppi/segmenti clienti |

---

## 2. Modelli Database

### 2.1 Party

```python
class Party(BaseModel):
    """Anagrafica principale."""
    __tablename__ = 'parties'
    
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
    # Identificazione
    name = db.Column(db.String(150), nullable=False, index=True)
    code = db.Column(db.String(50), unique=True, index=True)  # Codice cliente
    party_type = db.Column(db.String(20), nullable=False)  # customer, supplier, lead
    
    # Persona fisica / Giuridica
    is_company = db.Column(db.Boolean, default=True)
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    fiscal_code = db.Column(db.String(16), index=True)  # Codice fiscale
    vat_number = db.Column(db.String(50), index=True)  # Partita IVA
    
    # Contatto
    email = db.Column(db.String(120), index=True)
    phone = db.Column(db.String(50))
    website = db.Column(db.String(255))
    
    # Indirizzo principale
    address = db.Column(db.String(255))
    city = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(2), default='IT')
    
    # Stato
    status = db.Column(db.String(20), default='active')  # active, inactive, blocked
    notes = db.Column(db.Text)
    
    # Marketing
    source = db.Column(db.String(50))  # lead_source: web, fair, referral
    tags = db.Column(db.Text)  # JSON array
    
    # Relazioni
    addresses = db.relationship('PartyAddress', back_populates='party', cascade='all, delete-orphan')
    contacts = db.relationship('PartyContact', back_populates='party', cascade='all, delete-orphan')
    group_id = db.Column(db.Integer, db.ForeignKey('party_groups.id'))
    group = db.relationship('PartyGroup')
    
    __table_args__ = (
        db.Index('ix_party_tenant_type', 'tenant_id', 'party_type'),
    )
```

### 2.2 PartyAddress

```python
class PartyAddress(BaseModel):
    """Indirizzi multipli per party."""
    __tablename__ = 'party_addresses'
    
    party_id = db.Column(db.Integer, db.ForeignKey('parties.id'), nullable=False)
    address_type = db.Column(db.String(20), default='billing')  # billing, shipping, headquarter
    
    street = db.Column(db.String(255))
    street2 = db.Column(db.String(255))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(2), default='IT')
    is_default = db.Column(db.Boolean, default=False)
    
    party = db.relationship('Party', back_populates='addresses')
```

### 2.3 PartyContact

```python
class PartyContact(BaseModel):
    """Contatti multipli per party."""
    __tablename__ = 'party_contacts'
    
    party_id = db.Column(db.Integer, db.ForeignKey('parties.id'), nullable=False)
    contact_type = db.Column(db.String(20))  # email, phone, mobile, fax
    
    value = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100))  # Nome contatto (es. "Ufficio vendite")
    is_default = db.Column(db.Boolean, default=False)
    is_primary = db.Column(db.Boolean, default=False)  # Contatto principale
    
    party = db.relationship('Party', back_populates='contacts')
```

### 2.4 PartyGroup

```python
class PartyGroup(BaseModel):
    """Gruppi/Segmenti per categorizzare le anagrafiche."""
    __tablename__ = 'party_groups'
    
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    color = db.Column(db.String(7))  # Colore per UI
    
    tenant = db.relationship('Tenant')
    parties = db.relationship('Party', back_populates='group')
    
    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'name', name='uix_tenant_group_name'),
    )
```

---

## 3. API Endpoints

### 3.1 Party CRUD

| Method | Endpoint | Descrizione |
|--------|----------|-------------|
| GET | `/api/v1/parties` | Lista party con filtri |
| POST | `/api/v1/parties` | Crea party |
| GET | `/api/v1/parties/{id}` | Dettaglio party |
| PUT | `/api/v1/parties/{id}` | Aggiorna party |
| DELETE | `/api/v1/parties/{id}` | Elimina party |
| POST | `/api/v1/parties/{id}/addresses` | Aggiungi indirizzo |
| POST | `/api/v1/parties/{id}/contacts` | Aggiungi contatto |

### 3.2 Filtri Supportati

```python
# Query parameters
?party_type=customer        # Filtro per tipo
?status=active               # Filtro per stato
?search=mario                # Ricerca nome/email/codice
?country=IT                  # Filtro per paese
?group_id=5                  # Filtro per gruppo
?tags=VIP,Premium            # Filtro per tag
?created_after=2026-01-01   # Filtro data creazione
?page=1&per_page=20          # Paginação
?sort=name&order=asc         # Ordinamento
```

---

## 4. Funzionalità Business

### 4.1 Validazione

- **Partita IVA**: Validazione formato italiano (11 cifre)
- **Codice Fiscale**: Validazione formato italiano (16 caratteri)
- **Email**: Validazione formato standard
- **Codice Univoco**: Verifica duplicati

### 4.2 Import/Export

- Import CSV con mapping campi
- Export CSV/Excel
- Import da file ISTAT (elenchi comuni)

### 4.3 Completamento Automatico

```
Inserendo partita IVA:
→ Query API VIES/SDICOOP
→ Auto-compila: nome, indirizzo, sede
```

---

## 5. Dipendenze

| Modulo | Dipendenza |
|--------|------------|
| Core | Obbligatorio |
| Sales | Richiede Party |
| Purchases | Richiede Party |
| Accounting | Richiede Party |
| CRM | Richiede Party |

---

## 6. Stima Sviluppo

| Componente | Tempo |
|------------|-------|
| Modelli DB | 2h |
| Migration | 1h |
| API CRUD | 4h |
| Validazioni | 2h |
| Import/Export | 3h |
| Testing | 2h |
| **Totale** | **~14h** |

---

*Documento generato il 18 Febbraio 2026*
*Progetto: FlaskERP ERPaaS Platform*
*Documento #05 - Modulo Parties*
