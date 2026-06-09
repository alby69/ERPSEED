from datetime import datetime
from backend.extensions import db


class Nazione(db.Model):
    __tablename__ = 'nazioni'

    codice_iso = db.Column(db.String(3), primary_key=True)
    codice_iso2 = db.Column(db.String(2), unique=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    nome_inglese = db.Column(db.String(100))
    continente = db.Column(db.String(2))
    nazionalita = db.Column(db.String(100))
    valuta = db.Column(db.String(3))
    prefisso_telefonico = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Nazione {self.codice_iso}: {self.nome}>'

    def to_dict(self):
        return {
            'codice_iso': self.codice_iso,
            'codice_iso2': self.codice_iso2,
            'nome': self.nome,
            'nome_inglese': self.nome_inglese,
            'continente': self.continente,
            'nazionalita': self.nazionalita,
            'valuta': self.valuta,
            'prefisso_telefonico': self.prefisso_telefonico,
        }
