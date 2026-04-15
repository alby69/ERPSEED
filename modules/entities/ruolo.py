from datetime import datetime
from extensions import db


class Ruolo(db.Model):
    """Definizione di un ruolo nel sistema.

    Esempi: Cliente, Fornitore, Dipendente, Autista,
            Consulente, Spedizioniere, Agente, etc.
    """
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

    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'codice', name='uq_ruolo_tenant_codice'),
    )

    def __repr__(self):
        return f'<Ruolo {self.codice}>'

    def to_dict(self):
        return {
            'id': self.id,
            'codice': self.codice,
            'nome': self.nome,
            'descrizione': self.descrizione,
            'categoria': self.categoria,
            'richiede_credito': self.richiede_credito,
            'richiede_contratto': self.richiede_contratto,
            'soggetto_a_fatturazione': self.soggetto_a_fatturazione,
            'is_active': self.is_active,
        }


class SoggettoRuolo(db.Model):
    """Associazione N:N tra Soggetto e Ruolo.

    Un soggetto può avere molti ruoli.
    Un ruolo può essere assegnato a molti soggetti.
    """
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

    __table_args__ = (
        db.UniqueConstraint('soggetto_id', 'ruolo_id', name='uq_soggetto_ruolo'),
    )

    def __repr__(self):
        return f'<SoggettoRuolo soggetto={self.soggetto_id} ruolo={self.ruolo_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'soggetto_id': self.soggetto_id,
            'ruolo_id': self.ruolo_id,
            'ruolo_codice': self.ruolo.codice if self.ruolo else None,
            'ruolo_nome': self.ruolo.nome if self.ruolo else None,
            'data_inizio': self.data_inizio.isoformat() if self.data_inizio else None,
            'data_fine': self.data_fine.isoformat() if self.data_fine else None,
            'stato': self.stato,
            'parametri': self.parametri,
        }
