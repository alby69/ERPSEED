from .extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    role = db.Column(db.String(50), default='user')
    is_active = db.Column(db.Boolean, default=True)
    force_password_change = db.Column(db.Boolean, default=False)
    avatar = db.Column(db.String(255))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('projects', lazy=True))

class Party(db.Model):
    __tablename__ = 'parties'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), default='customer') # customer, supplier
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    vat_number = db.Column(db.String(20))
    fiscal_code = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), unique=True)
    price = db.Column(db.Float, default=0.0)
    description = db.Column(db.Text)

class SalesOrder(db.Model):
    __tablename__ = 'sales_orders'

    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(20), unique=True, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='draft')
    customer_id = db.Column(db.Integer, db.ForeignKey('parties.id'), nullable=False)
    customer = db.relationship('Party', backref='sales_orders')
    total = db.Column(db.Float, default=0.0)

class SalesOrderLine(db.Model):
    __tablename__ = 'sales_order_lines'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('sales_orders.id'), nullable=False)
    order = db.relationship('SalesOrder', backref=db.backref('lines', cascade='all, delete-orphan'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    product = db.relationship('Product')
    description = db.Column(db.String(200))
    quantity = db.Column(db.Float, default=1.0)
    unit_price = db.Column(db.Float, default=0.0)
    subtotal = db.Column(db.Float, default=0.0)

class SysModel(db.Model):
    __tablename__ = 'sys_models'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False) # Nome interno tabella (es. 'vehicles')
    title = db.Column(db.String(100), nullable=False) # Nome visualizzato (es. 'Veicoli')
    description = db.Column(db.Text)
    permissions = db.Column(db.Text) # JSON ACL: {"read": ["role1"], "write": ["role2"]}
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    default_view = db.Column(db.String(50), default='table') # table, kanban, etc.
    kanban_status_field = db.Column(db.String(100)) # Name of the field to use for Kanban columns
    kanban_card_color_field = db.Column(db.String(100)) # Name of the field to use for Kanban card color
    kanban_card_avatar_field = db.Column(db.String(100)) # Name of the field to use for Kanban card avatar (relation)
    kanban_card_progress_field = db.Column(db.String(100)) # Name of the field to use for Kanban card progress (integer/float)
    kanban_column_total_field = db.Column(db.String(100)) # Name of the field to sum for column total

    fields = db.relationship('SysField', backref='model', lazy='selectin', cascade="all, delete-orphan")

class SysField(db.Model):
    __tablename__ = 'sys_fields'
    __table_args__ = (db.UniqueConstraint('model_id', 'name', name='_model_field_uc'),)

    id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.Integer, db.ForeignKey('sys_models.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False) # Nome colonna (es. 'license_plate')
    title = db.Column(db.String(100)) # Etichetta (es. 'Targa')
    type = db.Column(db.String(50), nullable=False) # string, integer, boolean, date, select, relation
    required = db.Column(db.Boolean, default=False)
    options = db.Column(db.Text) # JSON per opzioni extra (es. valori select o target relation)
    order = db.Column(db.Integer, default=0)
    default_value = db.Column(db.String(255)) # Default value for the field
    formula = db.Column(db.Text) # Formula to compute the value, e.g., "{price} * {quantity}"
    summary_expression = db.Column(db.Text) # Aggregation expression, e.g. "SUM(subtotal)"
    is_unique = db.Column(db.Boolean, default=False) # If true, the field must be unique
    validation_regex = db.Column(db.Text) # Custom regex for validation
    validation_message = db.Column(db.String(255)) # Custom error message for regex
    tooltip = db.Column(db.String(255)) # Tooltip/Help text for the field

class SysChart(db.Model):
    __tablename__ = 'sys_charts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False) # bar, line, pie, doughnut, area
    model_id = db.Column(db.Integer, db.ForeignKey('sys_models.id'), nullable=True) # Data source (nullable for text widgets)
    x_axis = db.Column(db.String(100), nullable=True) # Field for X axis (categories)
    y_axis = db.Column(db.String(100), nullable=True) # Field for Y axis (values)
    aggregation = db.Column(db.String(50), default='sum') # sum, count, avg, min, max
    filters = db.Column(db.Text) # JSON filters: {"status": "confirmed"}
    content = db.Column(db.Text) # Static content for text/html widgets
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SysDashboard(db.Model):
    __tablename__ = 'sys_dashboards'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    layout = db.Column(db.Text) # JSON layout configuration (grid positions of charts)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    user = db.relationship('User')
    model_name = db.Column(db.String(100), nullable=False)
    record_id = db.Column(db.Integer, nullable=False)
    action = db.Column(db.String(20), nullable=False) # CREATE, UPDATE, DELETE, CLONE
    changes = db.Column(db.Text) # JSON string of changes
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)