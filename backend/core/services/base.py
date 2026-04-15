"""
Base service class and service layer utilities.
"""

class BaseService:
    """
    Base class for all services.
    Provides common functionality and ensures consistent error handling.
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

    def flush(self):
        """Flush session without commit."""
        self.db.session.flush()

    def commit(self):
        """Commit current transaction."""
        self.db.session.commit()

    def rollback(self):
        """Rollback current transaction."""
        self.db.session.rollback()
