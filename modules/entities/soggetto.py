from datetime import datetime
from extensions import db

class Soggetto(db.Model):
    """Entità base per qualsiasi soggetto nel sistema.

    Un Soggetto può essere:
    - Persona fisica
    - Persona giuridica
    - Ente

    Rappresenta l'identità anagrafica, indipendente dai ruoli.
    """
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

    __table_args__ = (
        db.Index('ix_soggetto_tenant_codice', 'tenant_id', 'codice'),
    )

    def __repr__(self):
        return f'<Soggetto {self.codice}: {self.denominazione}>'

    @property
    def denominazione(self):
        if self.tipo_soggetto == 'persona_giuridica':
            return self.ragione_sociale or self.nome
        return f"{self.cognome or ''} {self.nome}".strip()

    def to_dict(self):
        return {
            'id': self.id,
            'codice': self.codice,
            'tipo_soggetto': self.tipo_soggetto,
            'nome': self.nome,
            'cognome': self.cognome,
            'ragione_sociale': self.ragione_sociale,
            'denominazione': self.denominazione,
            'partita_iva': self.partita_iva,
            'codice_fiscale': self.codice_fiscale,
            'email_principale': self.email_principale,
            'telefono_principale': self.telefono_principale,
            'website': self.website,
            'stato': self.stato,
            'tags': self.tags,
            'ruoli': [sr.to_dict() for sr in self.ruoli.all()],
            'indirizzi': [si.to_dict() for si in self.indirizzi.all()],
            'contatti': [sc.to_dict() for sc in self.contatti.all()],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
