"""
Modello Comune per la gestione dei comuni italiani.
支持 sync con ISTAT e aggiunta manuale.
"""
from datetime import datetime
from backend.extensions import db


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
