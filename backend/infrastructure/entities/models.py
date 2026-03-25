from datetime import datetime
from backend.extensions import db


class Soggetto(db.Model):
    """Entità base per qualsiasi soggetto nel sistema."""
    __tablename__ = 'soggetti'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)
    codice = db.Column(db.String(50), unique=True, index=True)
    tipo_soggetto = db.Column(db.String(20), default='persona_fisica')
    nome = db.Column(db.String(150), nullable=False)
    cognome = db.Column(db.String(100))
    ragione_sociale = db.Column(db.String(200))
    partita_iva = db.Column(db.String(50), index=True)
    codice_fiscale = db.Column(db.String(50), index=True)
    email_principale = db.Column(db.String(120))
    telefono_principale = db.Column(db.String(50))
    website = db.Column(db.String(255))
    stato = db.Column(db.String(20), default='attivo')
    note = db.Column(db.Text)
    tags = db.Column(db.String(500))

    tenant = db.relationship('Tenant', backref=db.backref('soggetti', lazy='dynamic'))
    ruoli = db.relationship('SoggettoRuolo', back_populates='soggetto', cascade='all, delete-orphan', lazy='dynamic')
    indirizzi = db.relationship('SoggettoIndirizzo', back_populates='soggetto', cascade='all, delete-orphan', lazy='dynamic')
    contatti = db.relationship('SoggettoContatto', back_populates='soggetto', cascade='all, delete-orphan', lazy='dynamic')

    __table_args__ = (db.Index('ix_soggetto_tenant_codice', 'tenant_id', 'codice'),)

    def __repr__(self):
        return f'<Soggetto {self.codice}: {self.denominazione}>'

    @property
    def denominazione(self):
        if self.tipo_soggetto == 'persona_giuridica':
            return self.ragione_sociale or self.nome
        return f"{self.cognome or ''} {self.nome}".strip()

    def to_dict(self):
        return {
            'id': self.id, 'codice': self.codice, 'tipo_soggetto': self.tipo_soggetto,
            'nome': self.nome, 'cognome': self.cognome, 'ragione_sociale': self.ragione_sociale,
            'denominazione': self.denominazione, 'partita_iva': self.partita_iva,
            'codice_fiscale': self.codice_fiscale, 'email_principale': self.email_principale,
            'telefono_principale': self.telefono_principale, 'website': self.website,
            'stato': self.stato, 'tags': self.tags,
            'ruoli': [sr.to_dict() for sr in self.ruoli.all()],
            'indirizzi': [si.to_dict() for si in self.indirizzi.all()],
            'contatti': [sc.to_dict() for sc in self.contatti.all()],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Ruolo(db.Model):
    """Definizione di un ruolo nel sistema."""
    __tablename__ = 'ruoli'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)
    codice = db.Column(db.String(30), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    descrizione = db.Column(db.Text)
    categoria = db.Column(db.String(50))
    richiede_credito = db.Column(db.Boolean, default=False)
    richiede_contratto = db.Column(db.Boolean, default=False)
    soggetto_a_fatturazione = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)

    tenant = db.relationship('Tenant', backref=db.backref('ruoli', lazy='dynamic'))
    soggetti = db.relationship('SoggettoRuolo', back_populates='ruolo', lazy='dynamic')

    __table_args__ = (db.UniqueConstraint('tenant_id', 'codice', name='uq_ruolo_tenant_codice'),)

    def __repr__(self):
        return f'<Ruolo {self.codice}>'

    def to_dict(self):
        return {
            'id': self.id, 'codice': self.codice, 'nome': self.nome,
            'descrizione': self.descrizione, 'categoria': self.categoria,
            'richiede_credito': self.richiede_credito, 'richiede_contratto': self.richiede_contratto,
            'soggetto_a_fatturazione': self.soggetto_a_fatturazione, 'is_active': self.is_active,
        }


class SoggettoRuolo(db.Model):
    """Associazione N:N tra Soggetto e Ruolo."""
    __tablename__ = 'soggetti_ruoli'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    soggetto_id = db.Column(db.Integer, db.ForeignKey('soggetti.id'), nullable=False)
    ruolo_id = db.Column(db.Integer, db.ForeignKey('ruoli.id'), nullable=False)
    data_inizio = db.Column(db.Date)
    data_fine = db.Column(db.Date)
    stato = db.Column(db.String(20), default='attivo')
    parametri = db.Column(db.Text)

    soggetto = db.relationship('Soggetto', back_populates='ruoli')
    ruolo = db.relationship('Ruolo', back_populates='soggetti')

    __table_args__ = (db.UniqueConstraint('soggetto_id', 'ruolo_id', name='uq_soggetto_ruolo'),)

    def __repr__(self):
        return f'<SoggettoRuolo soggetto={self.soggetto_id} ruolo={self.ruolo_id}>'

    def to_dict(self):
        return {
            'id': self.id, 'soggetto_id': self.soggetto_id, 'ruolo_id': self.ruolo_id,
            'ruolo_codice': self.ruolo.codice if self.ruolo else None,
            'ruolo_nome': self.ruolo.nome if self.ruolo else None,
            'data_inizio': self.data_inizio.isoformat() if self.data_inizio else None,
            'data_fine': self.data_fine.isoformat() if self.data_fine else None,
            'stato': self.stato, 'parametri': self.parametri,
        }


class Indirizzo(db.Model):
    """Indirizzo geografico riutilizzabile."""
    __tablename__ = 'indirizzi'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)
    denominazione = db.Column(db.String(200))
    numero_civico = db.Column(db.String(20))
    CAP = db.Column(db.String(10))
    città = db.Column(db.String(100), nullable=False)
    provincia = db.Column(db.String(50))
    regione = db.Column(db.String(50))
    nazione = db.Column(db.String(2), default='IT')
    latitudine = db.Column(db.Float)
    longitudine = db.Column(db.Float)
    indirizzo_completo = db.Column(db.String(500))
    tipo = db.Column(db.String(30))
    geocoded = db.Column(db.Boolean, default=False)
    geocoding_data = db.Column(db.Text)

    tenant = db.relationship('Tenant', backref=db.backref('indirizzi', lazy='dynamic'))
    soggetti = db.relationship('SoggettoIndirizzo', back_populates='indirizzo', lazy='dynamic')

    def __repr__(self):
        return f'<Indirizzo {self.denominazione}, {self.città}>'

    def to_formatted(self):
        parts = [self.denominazione, self.numero_civico, self.CAP, self.città]
        return ', '.join([p for p in parts if p])

    def to_dict(self):
        return {
            'id': self.id, 'denominazione': self.denominazione, 'numero_civico': self.numero_civico,
            'CAP': self.CAP, 'città': self.città, 'provincia': self.provincia,
            'regione': self.regione, 'nazione': self.nazione, 'latitudine': self.latitudine,
            'longitudine': self.longitudine, 'indirizzo_completo': self.indirizzo_completo or self.to_formatted(),
            'tipo': self.tipo, 'geocoded': self.geocoded,
        }


class SoggettoIndirizzo(db.Model):
    """Associazione tra Soggetto e Indirizzo."""
    __tablename__ = 'soggetti_indirizzi'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    soggetto_id = db.Column(db.Integer, db.ForeignKey('soggetti.id'), nullable=False)
    indirizzo_id = db.Column(db.Integer, db.ForeignKey('indirizzi.id'), nullable=False)
    tipo_riferimento = db.Column(db.String(30))
    is_preferred = db.Column(db.Boolean, default=False)
    data_inizio = db.Column(db.Date)
    data_fine = db.Column(db.Date)

    soggetto = db.relationship('Soggetto', back_populates='indirizzi')
    indirizzo = db.relationship('Indirizzo', back_populates='soggetti')

    def __repr__(self):
        return f'<SoggettoIndirizzo soggetto={self.soggetto_id} indirizzo={self.indirizzo_id}>'

    def to_dict(self):
        return {
            'id': self.id, 'soggetto_id': self.soggetto_id, 'indirizzo_id': self.indirizzo_id,
            'indirizzo': self.indirizzo.to_dict() if self.indirizzo else None,
            'tipo_riferimento': self.tipo_riferimento, 'is_preferred': self.is_preferred,
            'data_inizio': self.data_inizio.isoformat() if self.data_inizio else None,
            'data_fine': self.data_fine.isoformat() if self.data_fine else None,
        }


class Contatto(db.Model):
    """Canale di contatto riutilizzabile."""
    __tablename__ = 'contatti'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)
    canale = db.Column(db.String(30), nullable=False)
    valore = db.Column(db.String(255), nullable=False)
    tipo_utilizzo = db.Column(db.String(30))
    is_verified = db.Column(db.Boolean, default=False)
    verifica_data = db.Column(db.DateTime)
    is_preferred = db.Column(db.Boolean, default=False)

    tenant = db.relationship('Tenant', backref=db.backref('contatti', lazy='dynamic'))
    soggetti = db.relationship('SoggettoContatto', back_populates='contatto', lazy='dynamic')

    def __repr__(self):
        return f'<Contatto {self.canale}: {self.valore}>'

    def to_dict(self):
        return {
            'id': self.id, 'canale': self.canale, 'valore': self.valore,
            'tipo_utilizzo': self.tipo_utilizzo, 'is_verified': self.is_verified, 'is_preferred': self.is_preferred,
        }


class SoggettoContatto(db.Model):
    """Associazione Soggetto - Contatto"""
    __tablename__ = 'soggetti_contatti'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    soggetto_id = db.Column(db.Integer, db.ForeignKey('soggetti.id'), nullable=False)
    contatto_id = db.Column(db.Integer, db.ForeignKey('contatti.id'), nullable=False)
    tipo_riferimento = db.Column(db.String(30))
    is_primary = db.Column(db.Boolean, default=False)

    soggetto = db.relationship('Soggetto', back_populates='contatti')
    contatto = db.relationship('Contatto', back_populates='soggetti')

    def __repr__(self):
        return f'<SoggettoContatto soggetto={self.soggetto_id} contatto={self.contatto_id}>'

    def to_dict(self):
        return {
            'id': self.id, 'soggetto_id': self.soggetto_id, 'contatto_id': self.contatto_id,
            'contatto': self.contatto.to_dict() if self.contatto else None,
            'tipo_riferimento': self.tipo_riferimento, 'is_primary': self.is_primary,
        }


class Comune(db.Model):
    """Comune italiano con dati ISTAT."""
    __tablename__ = 'comuni'

    id = db.Column(db.Integer, primary_key=True)

    # Codici ISTAT
    codice_istat = db.Column(db.String(10), unique=True, index=True)
    codice_regione = db.Column(db.String(2), index=True)
    codice_provincia = db.Column(db.String(3), index=True)
    prog_comune = db.Column(db.String(3))

    # Dati basic
    nome = db.Column(db.String(100), nullable=False, index=True)
    denominazione = db.Column(db.String(150))

    # Indirizzo
    cap = db.Column(db.String(5), index=True)

    # Coordinate
    latitudine = db.Column(db.Float)
    longitudine = db.Column(db.Float)

    # Dati ISTAT
    zona_altitudine = db.Column(db.String(1))
    superficie_kmq = db.Column(db.Float)
    popolazione = db.Column(db.Integer)

    # Info
    sito_web = db.Column(db.String(255))
    email = db.Column(db.String(120))
    pec = db.Column(db.String(120))
    telefono = db.Column(db.String(50))

    # Metadati
    is_manuale = db.Column(db.Boolean, default=False)  # True se aggiunto manualmente
    source = db.Column(db.String(50), default='ISTAT')  # ISTAT o MANUAL
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    synced_at = db.Column(db.DateTime)  # Ultima sincronizzazione

    __table_args__ = (
        db.Index('ix_comuni_regione_provincia', 'codice_regione', 'codice_provincia'),
    )

    def __repr__(self):
        return f'<Comune {self.codice_istat}: {self.nome}>'

    @property
    def provincia_sigla(self):
        """Restaura la sigla provinciale dal codice ISTAT."""
        if self.codice_provincia:
            return self.codice_provincia
        return None

    def to_dict(self):
        return {
            'id': self.id,
            'codice': self.codice_istat,
            'nome': self.nome,
            'denominazione': self.denominazione,
            'CAP': self.cap,
            'provincia': self.codice_provincia,
            'regione': self.codice_regione,
            'latitudine': self.latitudine,
            'longitudine': self.longitudine,
            'is_manuale': self.is_manuale,
            'display': f"{self.nome} ({self.codice_provincia})"
        }


class Regione(db.Model):
    """Regione italiana."""
    __tablename__ = 'regioni'

    id = db.Column(db.Integer, primary_key=True)
    codice = db.Column(db.String(2), unique=True, nullable=False)
    nome = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<Regione {self.codice}: {self.nome}>'

    def to_dict(self):
        return {
            'codice': self.codice,
            'nome': self.nome
        }


class Provincia(db.Model):
    """Provincia italiana."""
    __tablename__ = 'province'

    id = db.Column(db.Integer, primary_key=True)
    codice = db.Column(db.String(3), unique=True, nullable=False)
    nome = db.Column(db.String(50), nullable=False)
    codice_regione = db.Column(db.String(2), db.ForeignKey('regioni.codice'))

    regione = db.relationship('Regione', backref='province')

    def __repr__(self):
        return f'<Provincia {self.codice}: {self.nome}>'

    def to_dict(self):
        return {
            'codice': self.codice,
            'nome': self.nome,
            'regione': self.codice_regione
        }
