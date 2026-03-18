from .extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

# Import core models to register them with SQLAlchemy
try:
    from backend.core.models import Tenant, TenantMember
except ImportError:
    pass

# Import entities - Soggetto is the main subject entity
try:
    from backend.entities.soggetto import Soggetto
except ImportError:
    pass


class BaseModel(db.Model):
    """Base model with common fields for all other models."""

    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )


project_members = db.Table(
    "project_members",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("project_id", db.Integer, db.ForeignKey("projects.id"), primary_key=True),
)


class Project(BaseModel):
    """
    Represents a Project or application instance created with the Builder.
    Each project is a container for a set of models (SysModel).
    """

    __tablename__ = "projects"
    name = db.Column(
        db.String(80),
        unique=True,
        nullable=False,
        comment="Internal project name (e.g., 'fleet_management')",
    )
    title = db.Column(
        db.String(120), nullable=False, comment="Display title for the project"
    )
    description = db.Column(db.Text)
    version = db.Column(db.String(20), default="1.0.0", comment="Project version")
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # Theme Settings
    primary_color = db.Column(db.String(20), default="#1677ff")
    border_radius = db.Column(db.Integer, default=6)
    theme_mode = db.Column(db.String(20), default="light")  # light, dark

    models = db.relationship(
        "SysModel",
        back_populates="project",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    owner = db.relationship("User")
    members = db.relationship(
        "User", secondary=project_members, back_populates="projects", lazy="dynamic"
    )
    user_memberships = db.relationship(
        "TenantMember",
        secondary=project_members,
        primaryjoin="Project.id == project_members.c.project_id",
        secondaryjoin="TenantMember.user_id == project_members.c.user_id",
        viewonly=True,
    )

    def __repr__(self):
        return f"<Project {self.name}>"


class User(BaseModel):
    """User model for system users."""

    __tablename__ = "users"

    # Tenant (required - will be added via migration)
    tenant_id = db.Column(
        db.Integer, db.ForeignKey("tenants.id"), nullable=True, index=True
    )

    # Credentials
    email = db.Column(db.String(120), nullable=False, index=True)
    password_hash = db.Column(db.String(256))
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    role = db.Column(
        db.String(80),
        default="user",
        nullable=False,
        comment="User role (e.g., admin, user)",
    )
    is_active = db.Column(db.Boolean, default=True)
    force_password_change = db.Column(db.Boolean, default=False)
    avatar = db.Column(db.String(255), nullable=True)

    # Multi-tenant fields
    is_primary = db.Column(db.Boolean, default=False, comment="Primary admin of tenant")
    last_login_at = db.Column(db.DateTime)
    login_count = db.Column(db.Integer, default=0)
    password_reset_token = db.Column(db.String(255))
    password_reset_expires = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime, nullable=True, index=True)

    # Relationships
    tenant = db.relationship(
        "Tenant", backref=db.backref("tenant_users", lazy="dynamic")
    )
    # Note: custom_role_id temporarily disabled until migration is applied
    # custom_role_id = db.Column(db.Integer, db.ForeignKey("user_roles.id", ondelete="SET NULL"))
    projects = db.relationship(
        "Project", secondary=project_members, back_populates="members", lazy="dynamic"
    )
    tenant_members = db.relationship(
        "TenantMember",
        back_populates="user",
        foreign_keys="TenantMember.user_id",
        lazy="dynamic",
    )
    project_memberships = db.relationship(
        "TenantMember",
        secondary=project_members,
        primaryjoin="User.id == project_members.c.user_id",
        secondaryjoin="TenantMember.user_id == project_members.c.user_id",
        viewonly=True,
    )

    # Constraints
    __table_args__ = (
        db.UniqueConstraint("tenant_id", "email", name="uix_tenant_email"),
    )

    def __repr__(self):
        return f"<User {self.email}>"

    @property
    def full_name(self):
        full = f"{self.first_name or ''} {self.last_name or ''}".strip()
        return full or self.email

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        self.force_password_change = False
        self.password_reset_token = None
        self.password_reset_expires = None

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def record_login(self):
        """Record user login."""
        self.last_login_at = datetime.datetime.utcnow()
        self.login_count += 1

    def to_dict(self, include_email=True):
        """Serialize user."""
        def format_datetime(value):
            if value is None:
                return None
            if isinstance(value, str):
                return value
            return value.isoformat()
        
        result = {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "role": self.role,
            "is_active": self.is_active,
            "is_primary": self.is_primary,
            "tenant_id": self.tenant_id,
            "created_at": format_datetime(self.created_at),
            "updated_at": format_datetime(self.updated_at),
        }
        if not include_email:
            result.pop("email", None)
        return result


class SysModel(BaseModel):
    """Definition of a model (table) created dynamically by the Builder.

    This is the core of the meta-model architecture.
    Models are defined in the database, not in Python code.
    """

    __tablename__ = "sys_models"
    name = db.Column(
        db.String(80), nullable=False, comment="Technical name (e.g., 'customer')"
    )
    technical_name = db.Column(
        db.String(80),
        nullable=False,
        comment="Full technical name (e.g., 'crm.customer')",
    )
    title = db.Column(db.String(120), comment="Display title (e.g., 'Cliente')")
    description = db.Column(db.Text)

    # Table name in database (can be different from technical_name)
    table_name = db.Column(db.String(100), nullable=False)

    # Module system
    module_id = db.Column(
        db.Integer, db.ForeignKey("modules.id"), comment="Module this model belongs to"
    )

    # System flags
    is_system = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
        comment="Is a system model (cannot be deleted)",
    )
    is_active = db.Column(db.Boolean, default=True, nullable=False, comment="Is active")

    status = db.Column(
        db.String(20), default="draft", nullable=False
    )  # draft, testing, published, deprecated

    permissions = db.Column(
        db.Text, comment="JSON string for Access Control List (ACL)"
    )
    tool_options = db.Column(
        db.Text,
        comment="JSON for tool configuration (enabled operations, custom descriptions, etc.)",
    )

    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)

    __table_args__ = (
        db.UniqueConstraint("project_id", "name", name="_project_model_name_uc"),
        db.UniqueConstraint(
            "project_id", "technical_name", name="_project_model_technical_name_uc"
        ),
    )

    fields = db.relationship(
        "SysField",
        back_populates="model",
        lazy="joined",
        cascade="all, delete-orphan",
        order_by="SysField.order",
    )
    project = db.relationship("Project", back_populates="models")

    def __repr__(self):
        return f"<SysModel {self.name}>"


class SysField(BaseModel):
    """Definition of a field (column) for a SysModel.

    Supports all field types needed for ERP-grade functionality:
    - Basic: char, text, integer, float, boolean, date, datetime
    - Advanced: select, many2one, one2many, many2many, json, file, image
    - Computed: calculated fields with Python expressions
    """

    __tablename__ = "sys_fields"
    name = db.Column(db.String(80), nullable=False, comment="Field name for display")
    technical_name = db.Column(
        db.String(80), nullable=False, comment="Technical column name in DB"
    )
    title = db.Column(db.String(120), comment="Label for UI")
    type = db.Column(db.String(50), nullable=False, comment="Field type")

    # Basic properties
    required = db.Column(db.Boolean, default=False)
    is_unique = db.Column(db.Boolean, default=False)
    is_index = db.Column(db.Boolean, default=False, comment="Create database index")
    is_active = db.Column(db.Boolean, default=True)

    default_value = db.Column(db.String(255))

    # Relation configuration
    relation_model = db.Column(
        db.String(80), comment="Related model for relations (many2one)"
    )
    relation_type = db.Column(db.String(20), comment="one2many, many2many")
    relation_field = db.Column(db.String(80), comment="Inverse field name for one2many")

    # Options for select, radio, etc.
    options = db.Column(
        db.Text, comment="JSON for select options, relation config, etc."
    )

    # UI configuration
    ui_widget = db.Column(
        db.String(50),
        comment="UI widget: text, textarea, select, radio, checkbox, datepicker, fileupload, etc.",
    )
    ui_placeholder = db.Column(db.String(255), comment="Placeholder text")
    ui_group = db.Column(
        db.String(80),
        comment="Group field in forms (e.g., 'Anagrafica', 'Contabilità')",
    )
    ui_order = db.Column(db.Integer, default=0, comment="Order in form")
    ui_visible = db.Column(db.Boolean, default=True, comment="Visible in UI")
    ui_readonly = db.Column(db.Boolean, default=False, comment="Read-only in UI")
    ui_searchable = db.Column(db.Boolean, default=True, comment="Included in search")
    ui_filterable = db.Column(
        db.Boolean, default=True, comment="Filterable in list views"
    )

    # Order in lists/forms
    order = db.Column(db.Integer, default=0)

    # Computed fields
    is_computed = db.Column(db.Boolean, default=False, comment="Is a computed field")
    compute_script = db.Column(db.Text, comment="Python code to compute field value")
    depends_on = db.Column(
        db.String(255), comment="Comma-separated fields this depends on"
    )

    # Aggregates (summary from related)
    formula = db.Column(db.String(255), comment="Legacy: use is_computed instead")
    summary_expression = db.Column(
        db.String(255), comment="Aggregate expression from related"
    )

    # Validation
    validation_regex = db.Column(db.String(255))
    validation_message = db.Column(db.String(255))
    validation_min = db.Column(db.Float, comment="Min value for numbers")
    validation_max = db.Column(db.Float, comment="Max value for numbers")

    # Help
    help_text = db.Column(db.Text, comment="Help text for users")

    model_id = db.Column(db.Integer, db.ForeignKey("sys_models.id"), nullable=False)

    model = db.relationship("SysModel", back_populates="fields")

    def __repr__(self):
        return f"<SysField {self.name} ({self.type}) in {self.model.name}>"


# NOTE: AuditLog moved to backend/core/models/audit.py
# Keeping old class for compatibility during migration

# class AuditLog(BaseModel):
#     """Log of significant actions performed in the system."""
#     __tablename__ = 'audit_logs'
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
#     model_name = db.Column(db.String(80))
#     record_id = db.Column(db.Integer)
#     action = db.Column(db.String(50), comment="CREATE, UPDATE, DELETE, LOGIN, etc.")
#     changes = db.Column(db.Text, comment="JSON diff of the changes")
#     timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow, index=True)
#
#     user = db.relationship('User')

# NOTE: Party model was replaced by Soggetto in backend/entities/soggetto.py
# Use Soggetto directly or import from backend.entities.soggetto


class Product(BaseModel):
    """Product/Service master data."""

    __tablename__ = "products"

    # Multi-tenant support
    tenant_id = db.Column(
        db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True
    )

    name = db.Column(db.String(150), nullable=False, index=True)
    code = db.Column(db.String(50), index=True)
    description = db.Column(db.Text)
    unit_price = db.Column(db.Float)
    category = db.Column(db.String(100))
    sku = db.Column(db.String(50))
    barcode = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    track_inventory = db.Column(db.Boolean, default=False)
    current_stock = db.Column(db.Float, default=0)
    reorder_level = db.Column(db.Float, default=0)
    unit_of_measure = db.Column(db.String(20), default="pcs")
    weight = db.Column(db.Float)
    dimensions = db.Column(db.String(50))

    # Relationships
    tenant = db.relationship("Tenant", backref=db.backref("products", lazy="dynamic"))

    # Constraints
    __table_args__ = (db.Index("ix_product_tenant_code", "tenant_id", "code"),)

    def __repr__(self):
        return f"<Product {self.name}>"


class SalesOrder(BaseModel):
    __tablename__ = "sales_orders"

    # Multi-tenant support
    tenant_id = db.Column(
        db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True
    )

    number = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, default=datetime.date.today)
    customer_id = db.Column(db.Integer, db.ForeignKey("soggetti.id"), nullable=False)
    status = db.Column(db.String(20), default="draft")
    total_amount = db.Column(db.Float, default=0)
    notes = db.Column(db.Text)

    # Relationships
    tenant = db.relationship(
        "Tenant", backref=db.backref("sales_orders", lazy="dynamic")
    )
    customer = db.relationship("Soggetto")
    lines = db.relationship(
        "SalesOrderLine", back_populates="order", cascade="all, delete-orphan"
    )

    # Constraints
    __table_args__ = (db.Index("ix_order_tenant_number", "tenant_id", "number"),)


class SalesOrderLine(BaseModel):
    __tablename__ = "sales_order_lines"

    # Multi-tenant support
    tenant_id = db.Column(
        db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True
    )

    order_id = db.Column(db.Integer, db.ForeignKey("sales_orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    description = db.Column(db.String(255))
    quantity = db.Column(db.Float, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)

    # Relationships
    tenant = db.relationship("Tenant")
    order = db.relationship("SalesOrder", back_populates="lines")
    product = db.relationship("Product")


class PurchaseOrder(BaseModel):
    __tablename__ = "purchase_orders"

    tenant_id = db.Column(
        db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True
    )

    number = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, default=datetime.date.today)
    supplier_id = db.Column(db.Integer, db.ForeignKey("soggetti.id"), nullable=False)
    status = db.Column(db.String(20), default="draft")
    total_amount = db.Column(db.Float, default=0)
    expected_date = db.Column(db.Date)
    notes = db.Column(db.Text)

    tenant = db.relationship(
        "Tenant", backref=db.backref("purchase_orders", lazy="dynamic")
    )
    supplier = db.relationship("Soggetto")
    lines = db.relationship(
        "PurchaseOrderLine", back_populates="order", cascade="all, delete-orphan"
    )

    __table_args__ = (db.Index("ix_purchase_tenant_number", "tenant_id", "number"),)


class PurchaseOrderLine(BaseModel):
    __tablename__ = "purchase_order_lines"

    tenant_id = db.Column(
        db.Integer, db.ForeignKey("tenants.id"), nullable=False, index=True
    )

    order_id = db.Column(
        db.Integer, db.ForeignKey("purchase_orders.id"), nullable=False
    )
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    description = db.Column(db.String(255))
    quantity = db.Column(db.Float, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    quantity_received = db.Column(db.Float, default=0)

    tenant = db.relationship("Tenant")
    order = db.relationship("PurchaseOrder", back_populates="lines")
    product = db.relationship("Product")


class ChartLibraryConfig(BaseModel):
    __tablename__ = "chart_library_config"
    library_name = db.Column(
        db.String(20), unique=True, nullable=False
    )  # 'chartjs', 'apexcharts', 'echarts'
    is_default = db.Column(db.Boolean, default=False)
    options = db.Column(db.JSON)  # colori tema globali
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"<ChartLibraryConfig {self.library_name}>"


class SysChart(BaseModel):
    __tablename__ = "sys_charts"
    title = db.Column(db.String(120), nullable=False)
    library = db.Column(
        db.String(20), nullable=False, default="chartjs"
    )  # 'chartjs', 'apexcharts', 'echarts'
    chart_type = db.Column(db.String(50))  # 'bar', 'line', 'pie', 'area', 'radar', etc.
    model_id = db.Column(db.Integer, db.ForeignKey("sys_models.id"), nullable=False)
    x_axis = db.Column(db.String(80))
    y_axis = db.Column(db.String(80))
    aggregation = db.Column(db.String(20))  # 'sum', 'avg', 'count', 'min', 'max'
    filters = db.Column(db.Text)  # JSON filtri fissi
    filters_config = db.Column(db.JSON)  # Configurazione filtri dinamici UI
    library_options = db.Column(db.JSON)  # opzioni specifiche libreria

    model = db.relationship("SysModel")


class SysDashboard(BaseModel):
    __tablename__ = "sys_dashboards"
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    layout = db.Column(
        db.Text
    )  # JSON layout react-grid-layout (x, y, w, h per ogni widget)
    is_public = db.Column(db.Boolean, default=False)
    refresh_interval = db.Column(db.Integer, default=0)  # 0 = no auto-refresh
    default_library = db.Column(db.String(20))  # override globale
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))


class AIConversation(BaseModel):
    """
    Stores AI conversations for learning and context.
    Enables the AI to learn from previous interactions.
    """

    __tablename__ = "ai_conversations"

    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    user_message = db.Column(db.Text, nullable=False)
    ai_response = db.Column(db.Text)

    # Feedback for learning
    was_successful = db.Column(db.Boolean, default=False)
    user_correction = db.Column(db.Text, nullable=True)
    rating = db.Column(db.Integer, nullable=True)  # 1-5

    # Action taken
    action_taken = db.Column(
        db.String(50)
    )  # 'generate_json', 'create_model', 'apply_config', etc.
    entities_created = db.Column(db.JSON)  # List of created entity IDs

    # Context snapshot (project state at time of conversation)
    context_snapshot = db.Column(db.Text)

    project = db.relationship("Project")
    user = db.relationship("User")

    def __repr__(self):
        return f"<AIConversation project={self.project_id} user={self.user_id}>"


class SysView(BaseModel):
    """View configuration for a SysModel.

    Defines how a model's data is presented (list, form, kanban, etc.).
    """

    __tablename__ = "sys_views"

    name = db.Column(db.String(80), nullable=False, comment="View name")
    technical_name = db.Column(
        db.String(80),
        nullable=False,
        comment="Full technical name (e.g., 'crm.customer.list')",
    )
    title = db.Column(db.String(120), comment="Display title")
    description = db.Column(db.Text)

    view_type = db.Column(
        db.String(50),
        nullable=False,
        comment="View type: list, form, kanban, calendar, gantt, graph, pivot, dashboard",
    )

    model_id = db.Column(db.Integer, db.ForeignKey("sys_models.id"), nullable=False)

    config = db.Column(
        db.Text,
        comment="JSON configuration: columns, filters, sorting, actions, etc.",
    )

    is_default = db.Column(
        db.Boolean, default=False, comment="Is default view for this model"
    )
    is_active = db.Column(db.Boolean, default=True)

    order = db.Column(db.Integer, default=0, comment="Order in view selector")

    __table_args__ = (
        db.UniqueConstraint("model_id", "name", name="_model_view_name_uc"),
    )

    model = db.relationship("SysModel", backref=db.backref("views", lazy="dynamic"))


class SysComponent(BaseModel):
    """Reusable UI component definition.

    Components can be used in views to build custom UIs.
    """

    __tablename__ = "sys_components"

    name = db.Column(db.String(80), nullable=False, comment="Component name")
    technical_name = db.Column(
        db.String(80),
        nullable=False,
        comment="Full technical name (e.g., 'table', 'form', 'kanban')",
    )
    title = db.Column(db.String(120), comment="Display title")
    description = db.Column(db.Text)

    component_type = db.Column(
        db.String(50),
        nullable=False,
        comment="Component category: basic, layout, data, chart, custom",
    )

    # Frontend component path
    component_path = db.Column(
        db.String(255),
        comment="React component path (e.g., '@/components/Table')",
    )

    # Default config for this component
    default_config = db.Column(
        db.Text,
        comment="JSON default configuration",
    )

    # Schema for component properties
    props_schema = db.Column(
        db.Text,
        comment="JSON schema for component properties",
    )

    # Icon for component palette
    icon = db.Column(db.String(50), comment="Icon name (e.g., 'table', 'form')")

    is_active = db.Column(db.Boolean, default=True)

    # For custom components
    is_custom = db.Column(
        db.Boolean, default=False, comment="Is a custom user-defined component"
    )

    def __repr__(self):
        return f"<SysComponent {self.name}>"


class SysAction(BaseModel):
    """Action definition for views.

    Defines buttons, links, and other interactive elements.
    """

    __tablename__ = "sys_actions"

    name = db.Column(db.String(80), nullable=False, comment="Action name")
    technical_name = db.Column(
        db.String(80),
        nullable=False,
        comment="Full technical name",
    )
    title = db.Column(db.String(120), comment="Display title")

    action_type = db.Column(
        db.String(50),
        nullable=False,
        comment="Action type: button, link, bulk, row_action",
    )

    # Target: view, api, script, webhook, workflow
    target = db.Column(
        db.String(50),
        nullable=False,
        comment="Action target: view, api, script, webhook, workflow",
    )

    # View this action belongs to
    view_id = db.Column(db.Integer, db.ForeignKey("sys_views.id"), nullable=True)

    # Model this action operates on
    model_id = db.Column(db.Integer, db.ForeignKey("sys_models.id"), nullable=True)

    # Configuration
    config = db.Column(
        db.Text,
        comment="JSON configuration: api path, script, conditions, etc.",
    )

    # UI properties
    icon = db.Column(db.String(50))
    style = db.Column(db.String(50), comment="Button style: primary, secondary, danger")
    position = db.Column(
        db.String(50),
        comment="Position: toolbar, header, row, bulk",
    )

    # Conditions
    conditions = db.Column(
        db.Text,
        comment="JSON conditions when action is available",
    )

    is_active = db.Column(db.Boolean, default=True)
    order = db.Column(db.Integer, default=0)

    view = db.relationship("SysView", backref=db.backref("actions", lazy="dynamic"))
    model = db.relationship("SysModel")

    def __repr__(self):
        return f"<SysAction {self.name}>"


class SysModelVersion(BaseModel):
    """Snapshot of a SysModel definition at a specific point in time."""

    __tablename__ = "sys_model_versions"

    model_id = db.Column(db.Integer, db.ForeignKey("sys_models.id"), nullable=False)
    version_number = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)

    # JSON snapshot of model and its fields
    data = db.Column(db.Text, nullable=False)

    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))

    model = db.relationship(
        "SysModel",
        backref=db.backref(
            "versions", lazy="dynamic", cascade="all, delete-orphan"
        ),
    )
    creator = db.relationship("User")

    def __repr__(self):
        return f"<SysModelVersion {self.model_id} v{self.version_number}>"


class UserRole(BaseModel):
    """
    Custom roles for tenant with specific permissions.
    Stored in backend/models.py (moved from backend/core/models/user.py).
    """
    __tablename__ = 'user_roles'
    
    tenant_id = db.Column(
        db.Integer, 
        db.ForeignKey('tenants.id'), 
        nullable=False,
        index=True
    )
    
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255))
    permissions = db.Column(db.Text, comment="JSON array of permissions")
    is_default = db.Column(db.Boolean, default=False)
    
    tenant = db.relationship('Tenant')
    # users relationship defined in User model to avoid conflicts
    
    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'name', name='uix_tenant_role_name'),
    )
