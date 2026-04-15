from backend.extensions import db
from backend.models.base import BaseModel

class Archetype(BaseModel):
    """
    An Archetype represents a 'Blueprint' or a 'Category' of a business entity.
    Example: 'Partner', 'Product', 'Movement', 'Document'.
    """
    __tablename__ = 'sys_archetypes'
    name = db.Column(db.String(80), unique=True, nullable=False)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)

class Component(BaseModel):
    """
    A Component is a reusable UI element that can be attached to a Model or View.
    Example: 'Table', 'Form', 'Kanban', 'Chart'.
    """
    __tablename__ = 'sys_builder_components'
    name = db.Column(db.String(80), unique=True, nullable=False)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    component_type = db.Column(db.String(50)) # basic, layout, data, chart
    props_schema = db.Column(db.JSON) # JSON Schema for properties
    icon = db.Column(db.String(50))

class Block(BaseModel):
    """
    A Block is a functional unit of the ERP, composed of a Model, its Views, and Logic.
    It can be 'installed' or 'uninstalled' from a Project.
    """
    __tablename__ = 'blocks'
    name = db.Column(db.String(80), unique=True, nullable=False)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    version = db.Column(db.String(20), default='1.0.0')
    category_id = db.Column(db.Integer, db.ForeignKey('marketplace_categories.id'))
    archetype_id = db.Column(db.Integer, db.ForeignKey('sys_archetypes.id'))

    # Configuration and metadata
    config = db.Column(db.JSON)
    metadata_info = db.Column(db.JSON)

    is_system = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)

    archetype = db.relationship('Archetype', backref='blocks')

class BlockRelationship(BaseModel):
    """Defines dependencies between Blocks."""
    __tablename__ = 'sys_block_relationships'
    block_id = db.Column(db.Integer, db.ForeignKey('blocks.id'), nullable=False)
    depends_on_id = db.Column(db.Integer, db.ForeignKey('blocks.id'), nullable=False)
    rel_type = db.Column(db.String(20), default='requires') # requires, recommends, conflicts

def create_system_archetypes():
    """Initializes the base archetypes of the system."""
    archetypes = [
        {'name': 'partner', 'title': 'Soggetto (Partner)', 'icon': 'user', 'description': 'Anagrafiche di persone o aziende'},
        {'name': 'product', 'title': 'Prodotto/Servizio', 'icon': 'shopping-cart', 'description': 'Catalogo prodotti e servizi'},
        {'name': 'movement', 'title': 'Movimento', 'icon': 'swap', 'description': 'Transazioni finanziarie o di magazzino'},
        {'name': 'document', 'title': 'Documento', 'icon': 'file-text', 'description': 'Fatture, ordini, contratti'},
        {'name': 'process', 'title': 'Processo', 'icon': 'project', 'description': 'Workflow e stati di avanzamento'},
    ]

    for arch_data in archetypes:
        if not Archetype.query.filter_by(name=arch_data['name']).first():
            arch = Archetype(**arch_data)
            db.session.add(arch)
    db.session.commit()
