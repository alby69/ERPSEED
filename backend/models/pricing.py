from backend.core.models.base import BaseModel
from backend.extensions import db


class PriceList(BaseModel):
    __tablename__ = "price_lists"

    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    code = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    currency = db.Column(db.String(3), default="EUR")
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    valid_from = db.Column(db.Date, nullable=True)
    valid_to = db.Column(db.Date, nullable=True)

    tenant = db.relationship("Tenant", backref=db.backref("price_lists", lazy="dynamic"))

    __table_args__ = (
        db.UniqueConstraint("tenant_id", "code", name="uq_pricelist_tenant_code"),
    )

    def __repr__(self):
        return f"<PriceList {self.code}>"


class PriceListItem(BaseModel):
    __tablename__ = "price_list_items"

    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True)
    price_list_id = db.Column(db.Integer, db.ForeignKey("price_lists.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    price = db.Column(db.Float, nullable=False, default=0.0)
    max_discount = db.Column(db.Float, default=0.0)
    min_quantity = db.Column(db.Float, default=0.0)

    price_list = db.relationship("PriceList", backref="items")
    product = db.relationship("Product", backref="price_list_items")

    __table_args__ = (
        db.UniqueConstraint("price_list_id", "product_id", name="uq_pricelist_item_product"),
    )

    def __repr__(self):
        return f"<PriceListItem list={self.price_list_id} product={self.product_id}>"
