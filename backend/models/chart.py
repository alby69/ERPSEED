from backend.extensions import db
from backend.core.models.base import BaseModel


class ChartLibraryConfig(BaseModel):
    __tablename__ = "chart_library_config"
    library_name = db.Column(
        db.String(20), unique=True, nullable=False
    )
    is_default = db.Column(db.Boolean, default=False)
    options = db.Column(db.JSON)
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"<ChartLibraryConfig {self.library_name}>"
