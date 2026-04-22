"""
Base service class and service layer utilities.
"""
from datetime import datetime, timezone
from backend.core.utils.utils import paginate, check_unique, log_audit

class BaseService:
    """
    Base class for all services.
    Provides common functionality and ensures consistent error handling.
    """

    def __init__(self, db=None, model=None):
        """
        Initialize service with database instance and optional model.

        Args:
            db: SQLAlchemy database instance. Will be imported from extensions if not provided.
            model: The SQLAlchemy model this service primarily handles.
        """
        self._db = db
        self.model = model
        # Fields that should not be updated via the generic update method
        self.protected_fields = {'id', 'created_at', 'updated_at', 'deleted_at'}

    @property
    def db(self):
        """Lazy load database instance."""
        if self._db is None:
            from backend.extensions import db
            return db
        return self._db

    def save(self, instance):
        """Save instance to database."""
        self.db.session.add(instance)
        self.db.session.commit()
        return instance

    def delete(self, instance, soft=True):
        """Delete instance from database (soft delete by default)."""
        if soft and hasattr(instance, 'soft_delete'):
            instance.soft_delete()
        else:
            self.db.session.delete(instance)
        self.db.session.commit()

    def soft_delete(self, instance):
        """
        Mark record as deleted using deleted_at timestamp.
        """
        if hasattr(instance, 'deleted_at'):
            instance.deleted_at = datetime.now(timezone.utc)
            self.db.session.commit()
        else:
            self.delete(instance, soft=False)

    def paginate(self, query, page=None, per_page=None):
        """Standardized pagination."""
        return paginate(query, page, per_page)

    def check_unique(self, field, value, exclude_id=None):
        """Check uniqueness using the service's model."""
        if self.model is None:
            # Fallback per compatibilità con test se passano il modello esplicitamente
            return True
        return check_unique(self.model, field, value, exclude_id)

    def log_action(self, user_id, record_id, action, changes=None):
        """Log an audit action."""
        model_name = self.model.__name__ if self.model else "Unknown"
        log_audit(user_id, model_name, record_id, action, changes)

    def flush(self):
        """Flush session without commit."""
        self.db.session.flush()

    def commit(self):
        """Commit current transaction."""
        self.db.session.commit()

    def rollback(self):
        """Rollback current transaction."""
        self.db.session.rollback()

    def get_all(self, query=None):
        """Get all records, optionally filtered by a query."""
        if query is None:
            if self.model is None:
                raise ValueError("Model not defined for this service")
            query = self.model.query
        return query.all()

    def get_by_id(self, id):
        """Get a single record by ID."""
        if self.model is None:
            raise ValueError("Model not defined for this service")
        return self.model.query.get(id)

    def create(self, data):
        """Create a new record."""
        if self.model is None:
            raise ValueError("Model not defined for this service")
        # Filter out protected fields from input data
        filtered_data = {k: v for k, v in data.items() if k not in self.protected_fields}
        instance = self.model(**filtered_data)
        return self.save(instance)

    def update(self, instance, data):
        """Update an existing record, protecting sensitive fields."""
        for key, value in data.items():
            if key not in self.protected_fields and hasattr(instance, key):
                setattr(instance, key, value)
        self.commit()
        return instance
