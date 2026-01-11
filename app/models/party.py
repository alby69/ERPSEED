from app.extensions import db
from app.models.base import BaseModel

class Party(BaseModel):
    __tablename__ = 'parties'

    name = db.Column(db.String(128), nullable=False, index=True)
    type = db.Column(db.String(20), nullable=False, default='company') # 'company', 'person'
    vat_number = db.Column(db.String(20), index=True) # Partita IVA
    fiscal_code = db.Column(db.String(20), index=True) # Codice Fiscale
    
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))

    def __repr__(self):
        return f'<Party {self.name}>'