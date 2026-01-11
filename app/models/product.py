from app.extensions import db
from app.models.base import BaseModel

class Product(BaseModel):
    __tablename__ = 'products'

    name = db.Column(db.String(128), nullable=False, index=True)
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    sku = db.Column(db.String(64), unique=True, index=True)
    image = db.Column(db.String(256))
    stock_quantity = db.Column(db.Float, default=0.0, nullable=False)
    
    supplier_id = db.Column(db.Integer, db.ForeignKey('parties.id'))
    supplier = db.relationship('Party', backref='products')

    def __repr__(self):
        return f'<Product {self.name}>'