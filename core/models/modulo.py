"""
Modulo - definition of a module in the catalog.
"""
from datetime import datetime
from core.models.base import BaseModel
from extensions import db


class Modulo(BaseModel):
    """
    Module definition in the catalog.
    Modules are global (shared by all tenants), not tenant-specific.
    Version format: 1.0.0_20260219
    """
    __tablename__ = 'moduli'

    # Identity
    nome = db.Column(db.String(50), unique=True, nullable=False, index=True,
                     comment="Module name (e.g., 'contabilita', 'magazzino')")
    versione = db.Column(db.String(20), nullable=False,
                         comment="Version: 1.0.0_20260219")

    # Metadata
    titolo = db.Column(db.String(150), nullable=False)
    descrizione = db.Column(db.Text)
    autore = db.Column(db.String(100))

    # Module type
    tipo = db.Column(
        db.String(20),
        default='custom',
        comment="Type: core, builtin, custom"
    )

    # Status
    stato = db.Column(
        db.String(20),
        default='attivo',
        comment="Status: attivo, obsoleto, in_sviluppo"
    )

    # Dependencies
    dipendenze = db.Column(db.JSON, default=list,
                           comment="Array of module names this depends on")

    # Configuration schema
    config_schema = db.Column(db.JSON, default=dict,
                              comment="JSON schema for module config")

    # Module definition (YAML/JSON content)
    definizione = db.Column(db.Text,
                            comment="Module definition (YAML/JSON)")

    # Previous version (for upgrades)
    versione_precedente_id = db.Column(
        db.Integer,
        db.ForeignKey('moduli.id'),
        nullable=True
    )

    # Relations
    versione_precedente = db.relationship(
        'Modulo',
        remote_side=[id],
        backref='versioni_successive'
    )
    attivazioni = db.relationship(
        'ModuloAttivato',
        back_populates='modulo',
        cascade='all, delete-orphan'
    )

    __table_args__ = (
        db.Index('ix_moduleName_stato', 'nome', 'stato'),
    )

    def __repr__(self):
        return f'<Modulo {self.nome} v{self.versione}>'

    @property
    def version_number(self):
        """Extract version number (e.g., '1.0.0' from '1.0.0_20260219')"""
        return self.versione.split('_')[0]

    @property
    def version_date(self):
        """Extract version date (e.g., '20260219' from '1.0.0_20260219')"""
        parts = self.versione.split('_')
        return parts[1] if len(parts) > 1 else None

    def to_dict(self, include_definizione=False):
        data = {
            'id': self.id,
            'nome': self.nome,
            'versione': self.versione,
            'version_number': self.version_number,
            'version_date': self.version_date,
            'titolo': self.titolo,
            'descrizione': self.descrizione,
            'autore': self.autore,
            'tipo': self.tipo,
            'stato': self.stato,
            'dipendenze': self.dipendenze or [],
            'config_schema': self.config_schema or {},
            'versione_precedente_id': self.versione_precedente_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if include_definizione:
            data['definizione'] = self.definizione
        return data


class ModuloAttivato(BaseModel):
    """
    Module activated for a specific tenant.
    """
    __tablename__ = 'moduli_attivati'

    tenant_id = db.Column(
        db.Integer,
        db.ForeignKey('tenants.id'),
        nullable=False,
        index=True
    )

    modulo_id = db.Column(
        db.Integer,
        db.ForeignKey('moduli.id'),
        nullable=False,
        index=True
    )

    # Tenant-specific configuration
    config_tenant = db.Column(db.JSON, default=dict,
                              comment="Tenant-specific module config")

    # Activation info
    attivato_da_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    data_attivazione = db.Column(db.DateTime, default=datetime.utcnow)
    data_disattivazione = db.Column(db.DateTime)

    # Status
    stato = db.Column(
        db.String(20),
        default='attivo',
        comment="Status: attivo, sospeso"
    )

    # Relations
    tenant = db.relationship('Tenant', back_populates='moduli_attivati')
    modulo = db.relationship('Modulo', back_populates='attivazioni')
    attivato_da = db.relationship('User')

    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'modulo_id', name='uix_tenant_modulo'),
        db.Index('ix_modulo_attivato_stato', 'tenant_id', 'stato'),
    )

    def __repr__(self):
        return f'<ModuloAttivato tenant={self.tenant_id} modulo={self.modulo_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'modulo_id': self.modulo_id,
            'modulo': self.modulo.to_dict() if self.modulo else None,
            'config_tenant': self.config_tenant or {},
            'attivato_da_id': self.attivato_da_id,
            'data_attivazione': self.data_attivazione.isoformat() if self.data_attivazione else None,
            'data_disattivazione': self.data_disattivazione.isoformat() if self.data_disattivazione else None,
            'stato': self.stato,
        }
