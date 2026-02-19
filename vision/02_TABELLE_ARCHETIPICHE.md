# ERPE: Tabelle Archetipiche (Mattoncini Base)

## Introduzione

Le tabelle archetipiche sono i **mattoncini LEGO** fondamentali del sistema. Ogni tabella è un componente atomico con:
- **Identità chiara** (cosa rappresenta)
- **Responsabilità singola** (fa una cosa sola)
- **Interfaccia standard** (CRUD comune)
- **Punti di aggancio** (relazioni predefinite)

---

## Livello 1: Entità Core (Fondamenta)

### 1.1 Soggetto (Party/Subject)

L'entità più importante: rappresenta qualsiasi persona o organizzazione con cui l'azienda interagisce.

```python
class Soggetto(BaseModel):
    """Entità base per qualsiasi soggetto nel sistema.
    
    Un Soggetto può essere:
    - Persona fisica
    - Persona giuridica
    - Ente
    
    Rappresenta l'identità anagrafica, indipendente dai ruoli.
    """
    __tablename__ = 'soggetti'
    
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
    # Identificazione
    codice = db.Column(db.String(50), unique=True, index=True)  # Codice interno
    tipo_soggetto = db.Column(db.String(20), default='persona_fisica')  # persona_fisica, persona_giuridica, ente
    
    # Anagrafica base
    nome = db.Column(db.String(150), nullable=False)
    cognome = db.Column(db.String(100))  # Per persone fisiche
    ragione_sociale = db.Column(db.String(200))  # Per persone giuridiche
    partita_iva = db.Column(db.String(50), index=True)
    codice_fiscale = db.Column(db.String(50), index=True)
    
    # Contatti (riferimento a oggetti separati)
    email_principale = db.Column(db.String(120))
    telefono_principale = db.Column(db.String(50))
    website = db.Column(db.String(255))
    
    # Status
    stato = db.Column(db.String(20), default='attivo')  # attivo, sospeso, cessato
    note = db.Column(db.Text)
    
    # Metadata
    tags = db.Column(db.String(500))  # Tags separati da virgola
    
    # Relazioni
    tenant = db.relationship('Tenant', backref='soggetti')
    ruoli = db.relationship('SoggettoRuolo', back_populates='soggetto', cascade='all, delete-orphan')
    indirizzi = db.relationship('SoggettoIndirizzo', back_populates='soggetto', cascade='all, delete-orphan')
    contatti = db.relationship('SoggettoContatto', back_populates='soggetto', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Soggetto {self.codice}: {self.nome}>'
    
    @property
    def denominazione(self):
        """Ritorna il nome completo per visualizzazione"""
        if self.tipo_soggetto == 'persona_giuridica':
            return self.ragione_sociale or self.nome
        return f"{self.cognome or ''} {self.nome}".strip()
```

### 1.2 Ruolo (Role)

Un soggetto può avere **molteplici ruoli** contemporaneamente. Un cliente può anche essere fornitore, un dipendente può essere autista.

```python
class Ruolo(BaseModel):
    """Definizione di un ruolo nel sistema.
    
    Esempi: Cliente, Fornitore, Dipendente, Autista, 
            Consulente, Spedizioniere, Agente, etc.
    """
    __tablename__ = 'ruoli'
    
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
    codice = db.Column(db.String(30), unique=True, nullable=False)  # CLIENTE, FORNITORE, DIPENDENTE
    nome = db.Column(db.String(100), nullable=False)
    descrizione = db.Column(db.Text)
    categoria = db.Column(db.String(50))  # commercial, operativo, interno
    
    # Comportamento del ruolo
    richiede_credito = db.Column(db.Boolean, default=False)  # Richiede limiti credito
    richiede_contratto = db.Column(db.Boolean, default=False)
    soggetto_a_fatturazione = db.Column(db.Boolean, default=False)
    
    # Gestione stato
    is_active = db.Column(db.Boolean, default=True)
    
    tenant = db.relationship('Tenant', backref='ruoli')
    soggetti = db.relationship('SoggettoRuolo', back_populates='ruolo')
    
    def __repr__(self):
        return f'<Ruolo {self.codice}>'


class SoggettoRuolo(BaseModel):
    """Associazione N:N tra Soggetto e Ruolo.
    
    Un soggetto può avere molti ruoli.
    Un ruolo può essere assegnato a molti soggetti.
    """
    __tablename__ = 'soggetti_ruoli'
    
    soggetto_id = db.Column(db.Integer, db.ForeignKey('soggetti.id'), nullable=False)
    ruolo_id = db.Column(db.Integer, db.ForeignKey('ruoli.id'), nullable=False)
    
    # Dati specifici dell'associazione
    data_inizio = db.Column(db.Date)
    data_fine = db.Column(db.Date)
    stato = db.Column(db.String(20), default='attivo')  # attivo, sospeso, terminato
    
    # Campi specifici per il ruolo (JSON)
    parametri = db.Column(db.Text)  # JSON con parametri specifici
    
    soggetto = db.relationship('Soggetto', back_populates='ruoli')
    ruolo = db.relationship('Ruolo', back_populates='soggetti')
    
    __table_args__ = (
        db.UniqueConstraint('soggetto_id', 'ruolo_id', name='uq_soggetto_ruolo'),
    )
    
    def __repr__(self):
        return f'<SoggettoRuolo soggetto={self.soggetto_id} ruolo={self.ruolo_id}>'
```

### 1.3 Indirizzo (Address)

Value Object riutilizzabile che rappresenta una localizzazione geografica.

```python
class Indirizzo(BaseModel):
    """Indirizzo geografico riutilizzabile.
    
    Value Object: non ha identità propria, conta solo il valore.
    Può essere associato a più soggetti (sede legale, magazzino, etc.)
    """
    __tablename__ = 'indirizzi'
    
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
    # Indirizzo strutturato
    denominazione = db.Column(db.String(200))  # Via, Piazza, etc.
    numero_civico = db.Column(db.String(20))
    CAP = db.Column(db.String(10))
    città = db.Column(db.String(100), nullable=False)
    provincia = db.Column(db.String(50))
    regione = db.Column(db.String(50))
    nazione = db.Column(db.String(2), default='IT')  # Codice ISO 3166-1 alpha-2
    
    # Coordinate geografiche
    latitudine = db.Column(db.Float)
    longitudine = db.Column(db.Float)
    
    # Indirizzo formattato
    indirizzo_completo = db.Column(db.String(500))  # Indirizzo come stringa unica
    
    # Tipo indirizzo
    tipo = db.Column(db.String(30))  # residenza, sede_legale, magazzino, lavoro
    
    # Geocoding
    geocoded = db.Column(db.Boolean, default=False)  # Se è stato geocodificato
    geocoding_data = db.Column(db.Text)  # JSON con dati completi geocoding
    
    tenant = db.relationship('Tenant', backref='indirizzi')
    soggetti = db.relationship('SoggettoIndirizzo', back_populates='indirizzo')
    
    def __repr__(self):
        return f'<Indirizzo {self.denominazione}, {self.città}>'
    
    def to_formatted(self):
        """Ritorna indirizzo formattato"""
        parts = [self.denominazione, self.numero_civico, self.CAP, self.città]
        return ', '.join([p for p in parts if p])


class SoggettoIndirizzo(BaseModel):
    """Associazione tra Soggetto e Indirizzo.
    
    Permette a un soggetto di avere più indirizzi,
    e a un indirizzo di essere associato a più soggetti.
    """
    __tablename__ = 'soggetti_indirizzi'
    
    soggetto_id = db.Column(db.Integer, db.ForeignKey('soggetti.id'), nullable=False)
    indirizzo_id = db.Column(db.Integer, db.ForeignKey('indirizzi.id'), nullable=False)
    
    # Tipo associazione
    tipo_riferimento = db.Column(db.String(30))  # sede_legale, sede_operativa, magazzino, fatturazione
    is_preferred = db.Column(db.Boolean, default=False)  # Indirizzo preferito per questo tipo
    
    # Validità
    data_inizio = db.Column(db.Date)
    data_fine = db.Column(db.Date)
    
    soggetto = db.relationship('Soggetto', back_populates='indirizzi')
    indirizzo = db.relationship('Indirizzo', back_populates='soggetti')
    
    def __repr__(self):
        return f'<SoggettoIndirizzo soggetto={self.soggetto_id} indirizzo={self.indirizzo_id}>'
```

### 1.4 Contatto (Contact)

Informazioni di contatto strutturate (email, telefono, social, etc.)

```python
class Contatto(BaseModel):
    """Canale di contatto riutilizzabile."""
    __tablename__ = 'contatti'
    
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
    # Tipo canale
    canale = db.Column(db.String(30), nullable=False)  # email, telefono, fax, cellulare, web, social
    valore = db.Column(db.String(255), nullable=False)  # il valore effettivo
    tipo_utilizzo = db.Column(db.String(30))  # personale, lavoro, principale
    
    # Validazione
    is_verified = db.Column(db.Boolean, default=False)
    verifica_data = db.Column(db.DateTime)
    
    # Preferenza
    is_preferred = db.Column(db.Boolean, default=False)
    
    tenant = db.relationship('Tenant', backref='contatti')
    soggetti = db.relationship('SoggettoContatto', back_populates='contatto')
    
    def __repr__(self):
        return f'<Contatto {self.canale}: {self.valore}>'


class SoggettoContatto(BaseModel):
    """Associazione Soggetto - Contatto"""
    __tablename__ = 'soggetti_contatti'
    
    soggetto_id = db.Column(db.Integer, db.ForeignKey('soggetti.id'), nullable=False)
    contatto_id = db.Column(db.Integer, db.ForeignKey('contatti.id'), nullable=False)
    
    tipo_riferimento = db.Column(db.String(30))  # principale, alternativo, lavoro
    is_primary = db.Column(db.Boolean, default=False)
    
    soggetto = db.relationship('Soggetto', back_populates='contatti')
    contatto = db.relationship('Contatto', back_populates='soggetti')
```

---

## Livello 2: Pattern Documentali

### 2.1 Testata (Header) - Archetipo per Documenti

```python
class Testata(BaseModel):
    """Archetipo base per qualsiasi documento.
    
    Gestisce i dati comuni a tutti i documenti:
    - Ordini (acquisto, vendita)
    - Fatture (attive, passive)
    - DDT (documento trasporto)
    - Contratti
    - Preventivi
    
    La specializzazione avviene tramite 'tipo_documento'.
    """
    __tablename__ = 'testate'
    
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
    # Identificazione documento
    tipo_documento = db.Column(db.String(50), nullable=False)  # ORDINE_VENDITA, FATTURA, DDT
    codice = db.Column(db.String(50), nullable=False)  # Numero documento
    anno = db.Column(db.Integer)  # Anno per numerazione
    progressivo = db.Column(db.Integer)  # Numero progressivo
    
    # Data
    data_documento = db.Column(db.Date, nullable=False)
    data_validita = db.Column(db.Date)  # Data inizio validità
    data_scadenza = db.Column(db.Date)  # Data scadenza
    
    # Soggetti coinvolti
    soggetto_id = db.Column(db.Integer, db.ForeignKey('soggetti.id'))  # Cliente/Fornitore
    
    # Totali
    totale_imponibile = db.Column(db.Float, default=0)
    totale_imposta = db.Column(db.Float, default=0)
    totale_documento = db.Column(db.Float, default=0)
    valuta = db.Column(db.String(3), default='EUR')
    
    # Stato
    stato = db.Column(db.String(30), default='bozza')  # bozza, confermato, evaso, annullato
    note = db.Column(db.Text)
    
    # Integrazione
    documento_esterno_id = db.Column(db.String(100))  # ID documento sistema esterno
    
    # Relazioni
    tenant = db.relationship('Tenant', backref='testate')
    soggetto = db.relationship('Soggetto')
    righe = db.relationship('Riga', back_populates='testata', cascade='all, delete-orphan')
    allegati = db.relationship('Allegato', back_populates='testata', cascade='all, delete-orphan')
    
    __table_args__ = (
        db.Index('ix_testata_tenant_tipo', 'tenant_id', 'tipo_documento'),
        db.UniqueConstraint('tenant_id', 'tipo_documento', 'codice', name='uq_testata_codice'),
    )
    
    def __repr__(self):
        return f'<Testata {self.tipo_documento} {self.codice}>'
    
    def ricalcola_totali(self):
        """Ricalcola i totali sommando le righe"""
        self.totale_imponibile = sum(r.totale for r in self.righe)
        # In un sistema reale, calcoleresti anche le imposte
        self.totale_documento = self.totale_imponibile + self.totale_imposta
```

### 2.2 Riga (Line) - Archetipo per Dettagli Documento

```python
class Riga(BaseModel):
    """Archetipo base per righe documento.
    
    Ogni riga appartiene a una testata e rappresenta
    un elemento del documento.
    """
    __tablename__ = 'righe'
    
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
    # Riferimento alla testata
    testata_id = db.Column(db.Integer, db.ForeignKey('testate.id'), nullable=False)
    
    # Posizione nella testata
    numero_riga = db.Column(db.Integer, nullable=False)
    sub_riga = db.Column(db.Integer, default=0)  # Per righe分解
    
    # Riferimento a oggetti
    articolo_id = db.Column(db.Integer, db.ForeignKey('prodotti.id'))  # Prodotto
    soggetto_id = db.Column(db.Integer, db.ForeignKey('soggetti.id'))  # Soggetto (es. subfornitore)
    
    # Dati riga
    descrizione = db.Column(db.String(500))
    descrizione_estesa = db.Column(db.Text)
    
    # Quantità
    quantita = db.Column(db.Float, default=1)
    unità_misura = db.Column(db.String(20), default='pz')
    quantita_secondary = db.Column(db.Float)  # Per duale unità misura
    
    # Prezzi
    prezzo_unitario = db.Column(db.Float, default=0)
    sconto_percentuale = db.Column(db.Float, default=0)
    prezzo_netto = db.Column(db.Float)  # Prezzo dopo sconto
    
    # Totali riga
    totale = db.Column(db.Float, default=0)
    
    # IVA
    aliquota_iva = db.Column(db.Float, default=22)
    imposta = db.Column(db.Float, default=0)
    
    # Date
    data_consegna_prevista = db.Column(db.Date)
    data_consegna_effettiva = db.Column(db.Date)
    
    # Stato
    stato = db.Column(db.String(30), default='attivo')
    
    # Relazioni
    tenant = db.relationship('Tenant', backref='righe')
    testata = db.relationship('Testata', back_populates='righe')
    articolo = db.relationship('Prodotto')
    
    def __repr__(self):
        return f'<Riga {self.testata_id}/{self.numero_riga}>'
    
    def ricalcola(self):
        """Ricalcola i valori della riga"""
        self.prezzo_netto = self.prezzo_unitario * (1 - self.sconto_percentuale / 100)
        self.totale = self.quantita * self.prezzo_netto
        self.imposta = self.totale * self.aliquota_iva / 100
```

### 2.3 Allegato (Attachment)

```python
class Allegato(BaseModel):
    """File allegato a entità nel sistema."""
    __tablename__ = 'allegati'
    
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
    # Riferimento all'entità proprietaria
    entity_type = db.Column(db.String(50))  # testata, soggetto, prodotto
    entity_id = db.Column(db.Integer)
    
    # File
    nome_file = db.Column(db.String(255), nullable=False)
    nome_originale = db.Column(db.String(255))
    mime_type = db.Column(db.String(100))
    dimensione = db.Column(db.Integer)  # bytes
    
    # Storage
    percorso_storage = db.Column(db.String(500))  # Path nel file system/cloud
    checksum = db.Column(db.String(64))  # SHA256
    
    # Metadati
    categoria = db.Column(db.String(50))  # documento, immagine, fattura
    descrizione = db.Column(db.Text)
    tags = db.Column(db.String(500))
    
    # Relazioni
    tenant = db.relationship('Tenant', backref='allegati')
    testata = db.relationship('Testata', back_populates='allegati')
    
    def __repr__(self):
        return f'<Allegato {self.nome_file}>'
```

---

## Livello 3: Valori di Riferimento

### 3.1 Valuta (Currency)

```python
class Valuta(BaseModel):
    """Valute supportate dal sistema."""
    __tablename__ = 'valute'
    
    codice = db.Column(db.String(3), unique=True, nullable=False)  # EUR, USD
    nome = db.Column(db.String(100), nullable=False)
    simbolo = db.Column(db.String(5))
    
    # Decimali
    decimali = db.Column(db.Integer, default=2)
    
    # Tasso di cambio (base EUR)
    tasso_base = db.Column(db.Float, default=1.0)
    
    # Stato
    is_active = db.Column(db.Boolean, default=True)
    is_base = db.Column(db.Boolean, default=False)  # Valuta base del tenant
    
    def __repr__(self):
        return f'<Valuta {self.codice}>'
```

### 3.2 Unità di Misura (UOM)

```python
class UnitaMisura(BaseModel):
    """Unità di misura per i prodotti."""
    __tablename__ = 'unita_misure'
    
    codice = db.Column(db.String(10), unique=True, nullable=False)  # pz, kg, lt, mt
    nome = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(50))  # quantità, peso, volume, lunghezza
    
    # Conversioni
    fattore_conversione = db.Column(db.Float, default=1.0)  # Rispetto all'unità base
    um_base_id = db.Column(db.Integer, db.ForeignKey('unita_misure.id'))
    
    decimali_default = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<UM {self.codice}>'
```

---

## Livello 4: Sistema

### 4.1 Modulo (Module)

```python
class Modulo(BaseModel):
    """Modulo funzionale del sistema.
    
    Un modulo è un container che raggruppa:
    - Entità
    - Viste
    - Processi
    - Report
    """
    __tablename__ = 'moduli'
    
    codice = db.Column(db.String(50), unique=True, nullable=False)  # vendite, acquisti, magazzino
    nome = db.Column(db.String(100), nullable=False)
    descrizione = db.Column(db.Text)
    
    # Versione
    versione = db.Column(db.String(20), default='1.0.0')
    
    # Configurazione
    configurazione = db.Column(db.Text)  # JSON
    
    # Stato
    is_active = db.Column(db.Boolean, default=True)
    is_installed = db.Column(db.Boolean, default=False)
    
    # Dipendenze
    depends_on = db.Column(db.String(500))  # JSON array di codici moduli
    
    def __repr__(self):
        return f'<Modulo {self.codice}>'
```

### 4.2 Container (Group)

```python
class Container(BaseModel):
    """Container che aggrega mattoncini.
    
    Un container rappresenta un sottoinsieme funzionale
    all'interno di un modulo.
    """
    __tablename__ = 'containers'
    
    modulo_id = db.Column(db.Integer, db.ForeignKey('moduli.id'), nullable=False)
    
    codice = db.Column(db.String(50), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    descrizione = db.Column(db.Text)
    
    # Configurazione
    configurazione = db.Column(db.Text)  # JSON
    
    # Tipo container
    tipo = db.Column(db.String(30))  # entity, process, report
    
    # API
    api_prefix = db.Column(db.String(100))  # Prefisso per le API
    
    # Relazioni
    modulo = db.relationship('Modulo', backref='containers')
    blocchi = db.relationship('ContainerBlocco', back_populates='container')
    
    def __repr__(self):
        return f'<Container {self.codice}>'


class ContainerBlocco(BaseModel):
    """Associazione Container - Blocchi (mattoncini)"""
    __tablename__ = 'container_blocchi'
    
    container_id = db.Column(db.Integer, db.ForeignKey('containers.id'), nullable=False)
    blocco_type = db.Column(db.String(50), nullable=False)  # tipo blocco (entity, value_object)
    blocco_id = db.Column(db.Integer, nullable=False)  # ID del blocco
    
    ordine = db.Column(db.Integer, default=0)
    configurazione = db.Column(db.Text)  # JSON
    
    container = db.relationship('Container', back_populates='blocchi')
```

---

## Riepilogo Relazioni

```
Soggetto (1) ──────< N > SoggettoRuolo >──N<── Ruolo
    │
    ├──< N > SoggettoIndirizzo >──N<── Indirizzo
    │                                    ├─ latitudine
    │                                    └─ longitudine
    │
    └──< N > SoggettoContatto >──N<── Contatto

Testata (1) ──────< N > Riga
    │
    └──< N > Allegato

Modulo (1) ──────< N > Container
                          │
                          └──< N > ContainerBlocco >── Blocchi (entità)
```

---

## Note sulla Implementazione

1. **Tutte le tabelle** ereditano da `BaseModel` che fornisce:
   - `id` (PK)
   - `created_at`
   - `updated_at`

2. **Multi-tenancy**: ogni tabella ha `tenant_id` per isolamento

3. **API Standard**: ogni entità avrà metodi standard:
   - `create(data)`
   - `read(id)`
   - `update(id, data)`
   - `delete(id)`
   - `list(filters)`

4. **Estensibilità**: i campi JSON (`parametri`, `configurazione`) permettono estensioni senza modificare lo schema

---

## Prossimi Passi

- Implementare i modelli nel progetto
- Creare le migrazioni database
- Definire le API REST standard per ogni entità
- Implementare il sistema di relazioni dinamiche
