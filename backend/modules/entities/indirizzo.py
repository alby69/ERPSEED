from datetime import datetime
from backend.extensions import db


class Indirizzo(db.Model):
    """Indirizzo geografico riutilizzabile.

    Value Object: non ha identità propria, conta solo il valore.
    Può essere associato a più soggetti (sede legale, magazzino, etc.)
    """
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
            'id': self.id,
            'denominazione': self.denominazione,
            'numero_civico': self.numero_civico,
            'CAP': self.CAP,
            'città': self.città,
            'provincia': self.provincia,
            'regione': self.regione,
            'nazione': self.nazione,
            'latitudine': self.latitudine,
            'longitudine': self.longitudine,
            'indirizzo_completo': self.indirizzo_completo or self.to_formatted(),
            'tipo': self.tipo,
            'geocoded': self.geocoded,
        }


class SoggettoIndirizzo(db.Model):
    """Associazione tra Soggetto e Indirizzo.

    Permette a un soggetto di avere più indirizzi,
    e a un indirizzo di essere associato a più soggetti.
    """
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
            'id': self.id,
            'soggetto_id': self.soggetto_id,
            'indirizzo_id': self.indirizzo_id,
            'indirizzo': self.indirizzo.to_dict() if self.indirizzo else None,
            'tipo_riferimento': self.tipo_riferimento,
            'is_preferred': self.is_preferred,
            'data_inizio': self.data_inizio.isoformat() if self.data_inizio else None,
            'data_fine': self.data_fine.isoformat() if self.data_fine else None,
        }
