"""
System Metadata Models
----------------------
This module defines the core metadata entities that power the No-Code Builder.
These models store the definitions for dynamic models (SysModel), their fields
(SysField), visual representations (SysView, SysComponent, SysAction, SysChart),
and versioning/performance optimizations (SysModelVersion, SysReadModel).
"""
from backend.extensions import db
from backend.core.models.base import BaseModel


class SysModel(BaseModel):
    """Definition of a model (table) created dynamically by the Builder."""

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
    translations = db.Column(db.JSON, comment="JSON for translated titles and descriptions")

    table_name = db.Column(db.String(100), nullable=False)

    module_id = db.Column(
        db.Integer, db.ForeignKey("modules.id"), comment="Module this model belongs to"
    )

    is_system = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
        comment="Is a system model (cannot be deleted)",
    )
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    status = db.Column(
        db.String(20), default="draft", nullable=False
    )

    permissions = db.Column(
        db.Text, comment="JSON string for Access Control List (ACL)"
    )
    tool_options = db.Column(
        db.Text,
        comment="JSON for tool configuration (enabled operations, custom descriptions, etc.)",
    )

    projectId = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)

    __table_args__ = (
        db.UniqueConstraint("projectId", "name", name="_project_model_name_uc"),
        db.UniqueConstraint(
            "projectId", "technical_name", name="_project_model_technical_name_uc"
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
    """
    Definition of a field (column) for a SysModel.
    Supports basic types, relations, formulas, and UI-specific hints.
    """

    __tablename__ = "sys_fields"
    name = db.Column(db.String(80), nullable=False, comment="Field name for display")
    technical_name = db.Column(
        db.String(80), nullable=False, comment="Technical column name in DB"
    )
    title = db.Column(db.String(120), comment="Label for UI")
    type = db.Column(db.String(50), nullable=False, comment="Field type")
    translations = db.Column(db.JSON, comment="JSON for translated titles and help text")

    required = db.Column(db.Boolean, default=False)
    is_unique = db.Column(db.Boolean, default=False)
    is_index = db.Column(db.Boolean, default=False, comment="Create database index")
    is_active = db.Column(db.Boolean, default=True)

    default_value = db.Column(db.String(255))

    relation_model = db.Column(
        db.String(80), comment="Related model for relations (many2one)"
    )
    relation_type = db.Column(db.String(20), comment="one2many, many2many")
    relation_field = db.Column(db.String(80), comment="Inverse field name for one2many")

    options = db.Column(
        db.Text, comment="JSON for select options, relation config, etc."
    )

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

    order = db.Column(db.Integer, default=0)

    is_computed = db.Column(db.Boolean, default=False, comment="Is a computed field")
    compute_script = db.Column(db.Text, comment="Python code to compute field value")
    depends_on = db.Column(
        db.String(255), comment="Comma-separated fields this depends on"
    )

    formula = db.Column(db.String(255), comment="Legacy: use is_computed instead")
    summary_expression = db.Column(
        db.String(255), comment="Aggregate expression from related"
    )

    validation_regex = db.Column(db.String(255))
    validation_message = db.Column(db.String(255))
    validation_min = db.Column(db.Float, comment="Min value for numbers")
    validation_max = db.Column(db.Float, comment="Max value for numbers")

    help_text = db.Column(db.Text, comment="Help text for users")

    modelId = db.Column(db.Integer, db.ForeignKey("sys_models.id"), nullable=False)

    model = db.relationship("SysModel", back_populates="fields")

    def __repr__(self):
        return f"<SysField {self.name} ({self.type}) in {self.model.name}>"


class SysView(BaseModel):
    """View configuration for a SysModel."""

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

    modelId = db.Column(db.Integer, db.ForeignKey("sys_models.id"), nullable=False)

    config = db.Column(
        db.Text,
        comment="JSON configuration: columns, filters, sorting, actions, etc.",
    )
    layout = db.Column(
        db.Text,
        comment="Visual layout (x, y, w, h) for canvas",
    )

    is_default = db.Column(
        db.Boolean, default=False, comment="Is default view for this model"
    )
    is_active = db.Column(db.Boolean, default=True)

    order = db.Column(db.Integer, default=0, comment="Order in view selector")

    __table_args__ = (
        db.UniqueConstraint("modelId", "name", name="_model_view_name_uc"),
    )

    model = db.relationship("SysModel", backref=db.backref("views", lazy="dynamic"))

    def get_layout(self):
        """Get parsed layout."""
        try:
            import json
            return json.loads(self.layout) if self.layout else []
        except:
            return []

    def set_layout(self, layout):
        """Set layout from list/dict."""
        import json
        self.layout = json.dumps(layout)


class SysComponent(BaseModel):
    """Reusable UI component definition."""

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

    component_path = db.Column(
        db.String(255),
        comment="React component path (e.g., '@/components/Table')",
    )

    default_config = db.Column(
        db.Text,
        comment="JSON default configuration",
    )

    props_schema = db.Column(
        db.Text,
        comment="JSON schema for component properties",
    )

    icon = db.Column(db.String(50), comment="Icon name (e.g., 'table', 'form')")

    is_active = db.Column(db.Boolean, default=True)

    is_custom = db.Column(
        db.Boolean, default=False, comment="Is a custom user-defined component"
    )

    def __repr__(self):
        return f"<SysComponent {self.name}>"


class SysAction(BaseModel):
    """Action definition for views."""

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

    target = db.Column(
        db.String(50),
        nullable=False,
        comment="Action target: view, api, script, webhook, workflow",
    )

    viewId = db.Column(db.Integer, db.ForeignKey("sys_views.id"), nullable=True)

    modelId = db.Column(db.Integer, db.ForeignKey("sys_models.id"), nullable=True)

    config = db.Column(
        db.Text,
        comment="JSON configuration: api path, script, conditions, etc.",
    )

    icon = db.Column(db.String(50))
    style = db.Column(db.String(50), comment="Button style: primary, secondary, danger")
    position = db.Column(
        db.String(50),
        comment="Position: toolbar, header, row, bulk",
    )

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

    def get_localized_title(self, lang='en'):
        """Return translated title if available."""
        if self.translations and lang in self.translations:
            return self.translations[lang].get('title', self.title)
        return self.title


class SysChart(BaseModel):
    __tablename__ = "sys_charts"
    title = db.Column(db.String(120), nullable=False)
    library = db.Column(
        db.String(20), nullable=False, default="chartjs"
    )
    chart_type = db.Column(db.String(50))
    modelId = db.Column(db.Integer, db.ForeignKey("sys_models.id"), nullable=False)
    x_axis = db.Column(db.String(80))
    y_axis = db.Column(db.String(80))
    aggregation = db.Column(db.String(20))
    filters = db.Column(db.Text)
    filters_config = db.Column(db.JSON)
    library_options = db.Column(db.JSON)

    model = db.relationship("SysModel")


class SysDashboard(BaseModel):
    __tablename__ = "sys_dashboards"
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    layout = db.Column(
        db.Text
    )
    is_public = db.Column(db.Boolean, default=False)
    refresh_interval = db.Column(db.Integer, default=0)
    default_library = db.Column(db.String(20))
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))


class SysModelVersion(BaseModel):
    """Snapshot of a SysModel definition at a specific point in time."""

    __tablename__ = "sys_model_versions"

    modelId = db.Column(db.Integer, db.ForeignKey("sys_models.id"), nullable=False)
    version_number = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)

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
        return f"<SysModelVersion {self.modelId} v{self.version_number}>"


from sqlalchemy.dialects.postgresql import JSONB

class SysReadModel(BaseModel):
    """
    Denormalized read model for high-performance queries.
    Stores record data in a JSONB field (PostgreSQL) for fast, schema-less access.
    Used mainly for dashboards and consolidated views.
    """

    __tablename__ = "sys_read_models"

    model_name = db.Column(db.String(80), nullable=False, index=True)
    record_id = db.Column(db.Integer, nullable=False, index=True)
    projectId = db.Column(db.Integer, nullable=False, index=True)

    # The actual data in JSONB format for PostgreSQL performance
    data = db.Column(db.JSON().with_variant(JSONB, "postgresql"), nullable=False)

    @property
    def json_data(self):
        return self.data

    # Metadata for filtering/versioning
    version = db.Column(db.Integer, default=1)
    last_sync = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    __table_args__ = (
        db.UniqueConstraint("projectId", "model_name", "record_id", name="_project_record_uc"),
    )

    def __repr__(self):
        return f"<SysReadModel {self.model_name}:{self.record_id} (Project {self.projectId})>"

    def get_localized_title(self, lang='en'):
        """Return translated title if available."""
        if self.translations and lang in self.translations:
            return self.translations[lang].get('title', self.title)
        return self.title
