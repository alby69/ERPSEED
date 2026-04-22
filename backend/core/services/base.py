"""
Base service class and service layer utilities.
"""
from datetime import datetime
from ..utils.utils import paginate as paginate_response

class BaseService:
    """
    Base class for all services.
    Provides common functionality and ensures consistent error handling.
    (Fase 1.2 Refactoring DRY)
    """

    def __init__(self, db=None):
        """
        Initialize service with database instance.

        Args:
            db: SQLAlchemy database instance. Will be imported from extensions if not provided.
        """
        self._db = db

    @property
    def db(self):
        """Lazy load database instance."""
        if self._db is None:
            from ..extensions import db
            return db
        return self._db

    def save(self, instance):
        """Save instance to database."""
        self.db.session.add(instance)
        self.db.session.commit()
        return instance

    def delete(self, instance):
        """Delete instance from database."""
        self.db.session.delete(instance)
        self.db.session.commit()

    def soft_delete(self, instance):
        """
        Mark record as deleted using deleted_at timestamp.
        (Fase 1.2 BaseService Method)
        """
        if hasattr(instance, 'deleted_at'):
            instance.deleted_at = datetime.utcnow()
            self.db.session.commit()
        else:
            self.delete(instance)

    def check_unique(self, model, field, value, exclude_id=None):
        """
        Verify if a value is unique for a given field in a model.
        (Fase 1.2 BaseService Method)
        """
        query = model.query.filter(getattr(model, field) == value)
        if exclude_id:
            query = query.filter(model.id != exclude_id)
        return query.first() is None

    def paginate(self, query):
        """
        Standardized pagination for all services.
        (Fase 1.2 BaseService Method)
        """
        return paginate_response(query)

    def flush(self):
        """Flush session without commit."""
        self.db.session.flush()

    def commit(self):
        """Commit current transaction."""
        self.db.session.commit()

    def rollback(self):
        """Rollback current transaction."""
        self.db.session.rollback()
