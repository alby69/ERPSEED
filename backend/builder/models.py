"""
Builder Models - Archetype, Component, Block
This module defines the core models for the Component/Block system.
"""

from backend.extensions import db
import datetime


class Archetype(db.Model):
    """
    Component template - base for all components.
    Defines the behavior, configuration schema, and API of a component type.
    """

    __tablename__ = "archetypes"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    component_type = db.Column(
        db.String(50),
        nullable=False,
        comment="Type: 'table', 'form', 'chart', 'kanban', 'metric', 'grid'",
    )
    description = db.Column(db.String(255))

    # Configuration
    default_config = db.Column(db.JSON, default=dict)
    api_schema = db.Column(db.JSON, default=dict)

    # UI
    icon = db.Column(db.String(50))
    preview_url = db.Column(db.String(255))

    # System flag (system archetypes cannot be deleted)
    is_system = db.Column(db.Boolean, default=False)

    # Hierarchy (for component composition)
    parent_id = db.Column(db.Integer, db.ForeignKey("archetypes.id"))

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    # Relationships
    parent = db.relationship("Archetype", remote_side=[id], backref="children")
    components = db.relationship("Component", back_populates="archetype")

    def __repr__(self):
        return f"<Archetype {self.name} ({self.component_type})>"


class Component(db.Model):
    """
    Component instance in a project.
    Represents a specific instance of an Archetype with its own configuration.
    """

    __tablename__ = "components"

    id = db.Column(db.Integer, primary_key=True)

    # References
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    archetype_id = db.Column(db.Integer, db.ForeignKey("archetypes.id"), nullable=False)

    # Identity
    name = db.Column(db.String(120))
    description = db.Column(db.String(255))

    # Configuration (instance-specific)
    config = db.Column(db.JSON, default=dict)

    # Layout positioning (for grid-based views)
    position_x = db.Column(db.Integer, default=0)
    position_y = db.Column(db.Integer, default=0)
    width = db.Column(db.Integer, default=6)
    height = db.Column(db.Integer, default=4)

    # Sorting
    order_index = db.Column(db.Integer, default=0)

    # Hierarchy
    parent_id = db.Column(db.Integer, db.ForeignKey("components.id"), nullable=True)
    block_id = db.Column(db.Integer, db.ForeignKey("blocks.id"), nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    # Relationships
    archetype = db.relationship("Archetype", back_populates="components")
    project = db.relationship("Project", backref="components")
    parent = db.relationship("Component", remote_side=[id], backref="children")
    block = db.relationship("Block", back_populates="components")

    def __repr__(self):
        return f"<Component {self.name} ({self.archetype.name})>"


class Block(db.Model):
    """
    Aggregated Block - collection of components with logic and relationships.
    A Block is a self-contained unit that can be published to the Marketplace.
    """

    __tablename__ = "blocks"

    id = db.Column(db.Integer, primary_key=True)

    # References
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))

    # Identity
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)

    # Component composition
    component_ids = db.Column(db.JSON, default=list)
    relationships = db.Column(db.JSON, default=dict)
    api_endpoints = db.Column(db.JSON, default=list)

    # Versioning
    version = db.Column(db.String(20), default="1.0.0")

    # Testing & Quality
    test_suite_id = db.Column(db.Integer, db.ForeignKey("test_suites.id"))
    quality_score = db.Column(db.Integer, default=0)
    is_certified = db.Column(db.Boolean, default=False)
    certification_date = db.Column(db.DateTime)

    # Status
    status = db.Column(
        db.String(20), default="draft", comment="draft, testing, published"
    )

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    # Relationships
    project = db.relationship("Project", backref="blocks")
    creator = db.relationship("User", backref="created_blocks")
    test_suite = db.relationship("TestSuite", backref="blocks")
    components = db.relationship("Component", back_populates="block")

    def __repr__(self):
        return f"<Block {self.name} v{self.version}>"


class BlockRelationship(db.Model):
    """
    Connections between components within a Block.
    Defines data flow, filters, and references.
    """

    __tablename__ = "block_relationships"

    id = db.Column(db.Integer, primary_key=True)

    # References
    block_id = db.Column(db.Integer, db.ForeignKey("blocks.id"), nullable=False)
    source_component_id = db.Column(db.Integer, db.ForeignKey("components.id"))
    target_component_id = db.Column(db.Integer, db.ForeignKey("components.id"))

    # Relationship definition
    relationship_type = db.Column(
        db.String(50), comment="data_flow, filter, reference, action"
    )
    config = db.Column(db.JSON, default=dict)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # Relationships
    block = db.relationship("Block", backref="component_relationships")
    source_component = db.relationship(
        "Component",
        foreign_keys=[source_component_id],
        backref="outgoing_relationships",
    )
    target_component = db.relationship(
        "Component",
        foreign_keys=[target_component_id],
        backref="incoming_relationships",
    )

    def __repr__(self):
        return f"<BlockRelationship {self.relationship_type}>"


# Import system archetypes
def create_system_archetypes():
    """Create default system archetypes."""
    archetypes = [
        {
            "name": "data_table",
            "component_type": "table",
            "description": "Data table with sorting, filtering, pagination",
            "icon": "TableOutlined",
            "is_system": True,
            "default_config": {
                "columns": [],
                "sortable": True,
                "filterable": True,
                "paginated": True,
                "pageSize": 10,
            },
            "api_schema": {
                "list": {"method": "GET", "path": "/data"},
                "create": {"method": "POST", "path": "/data"},
                "update": {"method": "PUT", "path": "/data/{id}"},
                "delete": {"method": "DELETE", "path": "/data/{id}"},
            },
        },
        {
            "name": "form",
            "component_type": "form",
            "description": "Data entry form with validation",
            "icon": "FormOutlined",
            "is_system": True,
            "default_config": {
                "fields": [],
                "layout": "vertical",
                "validate_on": "blur",
            },
            "api_schema": {
                "submit": {"method": "POST", "path": "/submit"},
            },
        },
        {
            "name": "chart",
            "component_type": "chart",
            "description": "Data visualization chart",
            "icon": "LineChartOutlined",
            "is_system": True,
            "default_config": {
                "chart_type": "bar",
                "library": "chartjs",
                "aggregation": "sum",
            },
            "api_schema": {
                "data": {"method": "GET", "path": "/chart-data"},
            },
        },
        {
            "name": "kanban",
            "component_type": "kanban",
            "description": "Kanban board with drag & drop",
            "icon": "ColumnsOutlined",
            "is_system": True,
            "default_config": {
                "columns": [],
                "draggable": True,
            },
            "api_schema": {
                "move": {"method": "PUT", "path": "/move"},
            },
        },
        {
            "name": "metric",
            "component_type": "metric",
            "description": "KPI metric card",
            "icon": "NumberOutlined",
            "is_system": True,
            "default_config": {
                "value_type": "number",
                "format": "number",
                "comparison": None,
            },
            "api_schema": {
                "value": {"method": "GET", "path": "/value"},
            },
        },
        {
            "name": "grid_layout",
            "component_type": "grid",
            "description": "Grid layout container for other components",
            "icon": "AppstoreOutlined",
            "is_system": True,
            "default_config": {
                "cols": 12,
                "row_height": 80,
                "margin": [16, 16],
                "draggable": True,
                "resizable": True,
            },
            "api_schema": {},
        },
    ]

    for arch_data in archetypes:
        existing = Archetype.query.filter_by(name=arch_data["name"]).first()
        if not existing:
            archetype = Archetype(**arch_data)
            db.session.add(archetype)

    db.session.commit()
