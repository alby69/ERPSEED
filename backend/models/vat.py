from backend.core.models.base import BaseModel
from backend.extensions import db


class VatRegisterEntry(BaseModel):
    """Registro IVA entry generated from invoices."""
    __tablename__ = "vat_register_entries"

    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    register_type = db.Column(db.String(20), nullable=False)  # sales, purchases, corrispettivi
    entry_number = db.Column(db.Integer, nullable=False)
    entry_date = db.Column(db.Date, nullable=False)
    document_number = db.Column(db.String(100))
    document_date = db.Column(db.Date)

    soggetto_id = db.Column(db.Integer, db.ForeignKey("soggetti.id"), nullable=True)
    soggetto_name = db.Column(db.String(200))
    soggetto_vat = db.Column(db.String(50))

    invoice_id = db.Column(db.Integer, nullable=True)
    taxable_amount = db.Column(db.Float, default=0.0)
    vat_amount = db.Column(db.Float, default=0.0)
    vat_rate = db.Column(db.Float, default=0.0)
    vat_code = db.Column(db.String(20))
    tax_nature = db.Column(db.String(10), default="I")  # I=imponibile, NI=non imp., E=esente, etc.

    fiscal_year = db.Column(db.Integer, nullable=False)
    period = db.Column(db.String(7), nullable=False)  # YYYY-MM
    is_liquidation = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)

    __table_args__ = (
        db.UniqueConstraint("tenant_id", "register_type", "entry_number", "fiscal_year",
                           name="uq_vat_entry_number"),
        db.Index("ix_vat_register_period", "tenant_id", "register_type", "period"),
    )


class VatLiquidation(BaseModel):
    """Liquidazione IVA periodica."""
    __tablename__ = "vat_liquidations"

    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    fiscal_year = db.Column(db.Integer, nullable=False)
    period = db.Column(db.String(7), nullable=False)  # YYYY-MM for monthly, YYYY-QQ for quarterly
    type = db.Column(db.String(20), default="monthly")  # monthly, quarterly

    sales_taxable = db.Column(db.Float, default=0.0)
    sales_vat = db.Column(db.Float, default=0.0)
    purchases_taxable = db.Column(db.Float, default=0.0)
    purchases_vat = db.Column(db.Float, default=0.0)
    net_vat = db.Column(db.Float, default=0.0)  # sales_vat - purchases_vat
    previous_credit = db.Column(db.Float, default=0.0)
    to_pay = db.Column(db.Float, default=0.0)
    to_credit = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default="draft")  # draft, computed, paid, credited
    notes = db.Column(db.Text)
    computed_at = db.Column(db.DateTime)
    paid_at = db.Column(db.Date)

    __table_args__ = (
        db.UniqueConstraint("tenant_id", "fiscal_year", "period", "type",
                           name="uq_vat_liquidation_period"),
    )


class IntrastatDeclaration(BaseModel):
    """Dichiarazione Intrastat (cessioni/acquisti intra-UE)."""
    __tablename__ = "intrastat_declarations"

    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    fiscal_year = db.Column(db.Integer, nullable=False)
    period = db.Column(db.String(7), nullable=False)  # YYYY-MM
    type = db.Column(db.String(20), nullable=False)  # sales (cessioni), purchases (acquisti)
    is_quarterly = db.Column(db.Boolean, default=False)

    soggetto_id = db.Column(db.Integer, db.ForeignKey("soggetti.id"), nullable=False)
    soggetto_partita_iva = db.Column(db.String(50))
    soggetto_nazione = db.Column(db.String(5))

    amount = db.Column(db.Float, default=0.0)
    vat_amount = db.Column(db.Float, default=0.0)
    nature = db.Column(db.String(10), default="A")  # A=beni, B=servizi
    delivery_terms = db.Column(db.String(10))
    transport = db.Column(db.String(10))
    notes = db.Column(db.Text)

    status = db.Column(db.String(20), default="draft")  # draft, submitted
    submitted_at = db.Column(db.DateTime)

    __table_args__ = (
        db.Index("ix_intrastat_period", "tenant_id", "fiscal_year", "period", "type"),
    )
