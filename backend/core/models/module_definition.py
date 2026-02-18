"""
Module Definition - Catalogo moduli disponibili nel sistema.
"""
from backend.core.models.base import BaseModel
from backend.extensions import db


class ModuleDefinition(BaseModel):
    """
    Definizione di un modulo disponibile nel sistema.
    """
    __tablename__ = 'module_definitions'
    
    module_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # Category: core, builtin, premium, third_party
    category = db.Column(db.String(20), nullable=False, default='builtin')
    version = db.Column(db.String(20), default="1.0.0")
    
    # Licensing
    is_free = db.Column(db.Boolean, default=True)
    price = db.Column(db.Numeric(10, 2))
    plan_required = db.Column(db.String(50), default="starter")
    
    # Dependencies
    dependencies = db.Column(db.JSON, default=list)
    core_version_min = db.Column(db.String(20), default="1.0.0")
    
    # UI
    icon = db.Column(db.String(50), default="box")
    menu_position = db.Column(db.Integer, default=100)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<ModuleDefinition {self.module_id}>'
    
    def to_dict(self):
        """Serialize module definition."""
        return {
            'id': self.module_id,
            'module_id': self.module_id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'version': self.version,
            'is_free': self.is_free,
            'price': float(self.price) if self.price else None,
            'plan_required': self.plan_required,
            'dependencies': self.dependencies or [],
            'core_version_min': self.core_version_min,
            'icon': self.icon,
            'menu_position': self.menu_position,
            'is_active': self.is_active
        }
