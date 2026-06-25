from datetime import datetime
from backend.extensions import db


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
            'id': self.id,
            'canale': self.canale,
            'valore': self.valore,
            'tipo_utilizzo': self.tipo_utilizzo,
            'is_verified': self.is_verified,
            'is_preferred': self.is_preferred,
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
            'id': self.id,
            'soggetto_id': self.soggetto_id,
            'contatto_id': self.contatto_id,
            'contatto': self.contatto.to_dict() if self.contatto else None,
            'tipo_riferimento': self.tipo_riferimento,
            'is_primary': self.is_primary,
        }
