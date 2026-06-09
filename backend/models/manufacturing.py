from backend.core.models.base import BaseModel
from backend.extensions import db


class BillOfMaterial(BaseModel):
    __tablename__ = "bom"

    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    code = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(200))
    version = db.Column(db.Integer, default=1)
    status = db.Column(db.String(20), default="draft")  # draft, active, archived
    total_quantity = db.Column(db.Float, default=1.0)
    notes = db.Column(db.Text)

    product = db.relationship("Product")
    lines = db.relationship("BOMLine", back_populates="bom", lazy="joined", cascade="all, delete-orphan")

    __table_args__ = (
        db.UniqueConstraint("tenant_id", "product_id", "version", name="uq_bom_product_version"),
        db.Index("ix_bom_tenant_status", "tenant_id", "status"),
    )


class BOMLine(BaseModel):
    __tablename__ = "bom_lines"

    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    bom_id = db.Column(db.Integer, db.ForeignKey("bom.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Float, nullable=False, default=1.0)
    unit_of_measure = db.Column(db.String(20))
    scrap_percentage = db.Column(db.Float, default=0.0)
    position = db.Column(db.Integer, default=0)
    notes = db.Column(db.String(255))

    bom = db.relationship("BillOfMaterial", back_populates="lines")
    product = db.relationship("Product")


class WorkCycle(BaseModel):
    __tablename__ = "work_cycles"

    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    code = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    total_setup_time = db.Column(db.Float, default=0.0)  # minutes
    total_run_time = db.Column(db.Float, default=0.0)  # minutes
    status = db.Column(db.String(20), default="draft")

    phases = db.relationship("WorkPhase", back_populates="work_cycle", lazy="joined", cascade="all, delete-orphan",
                             order_by="WorkPhase.phase_number")

    __table_args__ = (
        db.UniqueConstraint("tenant_id", "code", name="uq_work_cycle_code"),
    )


class WorkPhase(BaseModel):
    __tablename__ = "work_phases"

    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    work_cycle_id = db.Column(db.Integer, db.ForeignKey("work_cycles.id"), nullable=False)
    phase_number = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    setup_time = db.Column(db.Float, default=0.0)  # minutes
    run_time = db.Column(db.Float, default=0.0)  # minutes per unit
    machine = db.Column(db.String(100))
    resource_type = db.Column(db.String(50))  # manual, machine, automated

    work_cycle = db.relationship("WorkCycle", back_populates="phases")


class ProductionOrder(BaseModel):
    __tablename__ = "production_orders"

    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    number = db.Column(db.String(50), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    bom_id = db.Column(db.Integer, db.ForeignKey("bom.id"), nullable=True)
    work_cycle_id = db.Column(db.Integer, db.ForeignKey("work_cycles.id"), nullable=True)
    quantity = db.Column(db.Float, nullable=False)
    quantity_produced = db.Column(db.Float, default=0.0)
    planned_start_date = db.Column(db.Date)
    planned_end_date = db.Column(db.Date)
    actual_start_date = db.Column(db.DateTime)
    actual_end_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default="planned")  # planned, released, in_progress, completed, cancelled
    notes = db.Column(db.Text)

    product = db.relationship("Product")
    bom = db.relationship("BillOfMaterial")
    work_cycle = db.relationship("WorkCycle")
    materials = db.relationship("ProductionOrderMaterial", back_populates="order", lazy="joined",
                                cascade="all, delete-orphan")

    __table_args__ = (
        db.UniqueConstraint("tenant_id", "number", name="uq_production_order_number"),
        db.Index("ix_production_order_tenant_status", "tenant_id", "status"),
    )


class ProductionOrderMaterial(BaseModel):
    __tablename__ = "production_order_materials"

    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    production_order_id = db.Column(db.Integer, db.ForeignKey("production_orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    required_quantity = db.Column(db.Float, nullable=False)
    consumed_quantity = db.Column(db.Float, default=0.0)

    order = db.relationship("ProductionOrder", back_populates="materials")
    product = db.relationship("Product")
