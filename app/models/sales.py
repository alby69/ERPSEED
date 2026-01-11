from sqlalchemy import event
from flask_smorest import abort
from app.extensions import db
from app.models.base import BaseModel
from sqlalchemy.sql import func

class SalesOrder(BaseModel):
    __tablename__ = 'sales_orders'

    date = db.Column(db.DateTime(timezone=True), server_default=func.now())
    number = db.Column(db.String(20), unique=True, nullable=False)
    status = db.Column(db.String(20), default='draft') # draft, confirmed, done
    
    # Relazione N:1 con Party (Cliente)
    customer_id = db.Column(db.Integer, db.ForeignKey('parties.id'), nullable=False)
    customer = db.relationship('Party', backref='sales_orders')

    # Relazione 1:N con Righe Ordine
    lines = db.relationship('SalesOrderLine', backref='order', cascade="all, delete-orphan")

    @property
    def total_amount(self):
        return sum(line.total for line in self.lines)

class SalesOrderLine(BaseModel):
    __tablename__ = 'sales_order_lines'

    order_id = db.Column(db.Integer, db.ForeignKey('sales_orders.id'), nullable=False)
    
    # Relazione N:1 con Prodotto
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    product = db.relationship('Product')

    quantity = db.Column(db.Float, nullable=False, default=1.0)
    unit_price = db.Column(db.Float, nullable=False, default=0.0)
    
    @property
    def total(self):
        return self.quantity * self.unit_price

# --- Event Listeners per Gestione Magazzino ---

def _deduct_stock(order):
    """Scala la giacenza dai prodotti dell'ordine."""
    for line in order.lines:
        if line.product.stock_quantity < line.quantity:
            abort(422, message=f"Giacenza insufficiente per '{line.product.name}'. Disponibile: {line.product.stock_quantity}, Richiesto: {line.quantity}")
        line.product.stock_quantity -= line.quantity

def check_stock_and_confirm(mapper, connection, target):
    state = db.inspect(target)
    
    # Caso 1: Aggiornamento stato (da draft a confirmed)
    if state.attrs.status.history.has_changes() and state.attrs.status.history.added[0] == 'confirmed':
        _deduct_stock(target)
    # Caso 2: Creazione diretta come confirmed
    elif state.transient and target.status == 'confirmed':
        _deduct_stock(target)

event.listen(SalesOrder, 'before_update', check_stock_and_confirm)
event.listen(SalesOrder, 'before_insert', check_stock_and_confirm)