"""
Unit of Work Pattern Implementation.

Provides transactional management for database operations with proper
commit/rollback handling. This ensures atomic operations across multiple
repositories.

Usage:
    with UnitOfWork(db) as uow:
        order = uow.sales_repo.create_order(data)
        uow.inventory_repo.reserve_stock(order['id'])
        uow.notifications_repo.send_confirmation(order['id'])
        # Automatic commit on success, rollback on exception
"""
from contextlib import contextmanager
from typing import Dict, Any, Optional, Callable, List, Type
from functools import wraps
import logging

from flask import has_request_context, request
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class UnitOfWork:
    """
    Unit of Work pattern implementation.
    
    Manages a transactional scope for multiple repository operations.
    All changes are held in memory until commit() is called or the
    context manager exits successfully.
    
    Usage:
        with UnitOfWork(db) as uow:
            uow.sales_repo.create(data)
            uow.inventory_repo.reserve_stock(...)
            # Both operations in same transaction
    """
    
    _current: Optional['UnitOfWork'] = None
    
    def __init__(self, db: Session = None):
        """
        Initialize Unit of Work.
        
        Args:
            db: SQLAlchemy session. If None, uses current app context session.
        """
        from backend.extensions import db as _db
        self.db = db or _db
        self._repositories: Dict[str, Any] = {}
        self._events: List[Any] = []
        self._committed = False
        self._nested = False
        
        if UnitOfWork._current is not None:
            self._nested = True
    
    def __enter__(self) -> 'UnitOfWork':
        """Enter context manager."""
        if not self._nested:
            UnitOfWork._current = self
            logger.debug("UoW: Started transaction")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager with commit or rollback."""
        if self._nested:
            return
        
        UnitOfWork._current = None
        
        if exc_type is not None:
            logger.warning(f"UoW: Rolling back transaction due to {exc_type.__name__}: {exc_val}")
            self.db.session.rollback()
        elif not self._committed:
            logger.debug("UoW: Committing transaction")
            self.db.session.commit()
        
        logger.debug(f"UoW: Transaction ended (committed={not self._committed or exc_type is None})")
    
    def register_repository(self, name: str, repository: Any) -> None:
        """
        Register a repository in this unit of work.
        
        Args:
            name: Repository name (e.g., 'sales', 'inventory')
            repository: Repository instance
        """
        self._repositories[name] = repository
        logger.debug(f"UoW: Registered repository '{name}'")
    
    def get_repository(self, name: str) -> Any:
        """
        Get a registered repository.
        
        Args:
            name: Repository name
            
        Returns:
            Repository instance
            
        Raises:
            KeyError: If repository not registered
        """
        if name not in self._repositories:
            raise KeyError(f"Repository '{name}' not registered in UnitOfWork")
        return self._repositories[name]
    
    def add_event(self, event: Any) -> None:
        """
        Add an event to be published after commit.
        
        Events are collected during the transaction and published
        only after successful commit.
        
        Args:
            event: Domain event to publish
        """
        self._events.append(event)
    
    def commit(self) -> None:
        """
        Commit the current transaction.
        
        Should be called explicitly for read-write transactions.
        If not called, auto-commit happens on context exit.
        """
        if self._committed:
            logger.warning("UoW: Commit called twice!")
            return
        
        self.db.session.commit()
        self._committed = True
        
        self._publish_events()
        logger.info("UoW: Transaction committed successfully")
    
    def rollback(self) -> None:
        """
        Rollback the current transaction.
        
        Discards all changes made during the transaction.
        """
        self.db.session.rollback()
        self._committed = True
        self._events.clear()
        logger.info("UoW: Transaction rolled back")
    
    def flush(self) -> None:
        """
        Flush pending changes to database without committing.
        
        Useful for getting IDs or validating constraints
        before final commit.
        """
        self.db.session.flush()
    
    def _publish_events(self) -> None:
        """Publish collected events after commit."""
        if not self._events:
            return
        
        logger.info(f"UoW: Publishing {len(self._events)} events")
        
        try:
            from backend.shared.events.event_bus import EventBus
            event_bus = EventBus()
            
            for event in self._events:
                try:
                    event_bus.publish(event)
                except Exception as e:
                    logger.error(f"UoW: Failed to publish event {event}: {e}")
            
            self._events.clear()
        except ImportError:
            logger.warning("UoW: EventBus not available, events not published")
    
    @classmethod
    def get_current(cls) -> Optional['UnitOfWork']:
        """Get the current active UnitOfWork if any."""
        return cls._current


class TransactionContext:
    """
    Thread-local transaction context for accessing UnitOfWork outside handlers.
    
    Usage:
        uow = TransactionContext.current()
        if uow:
            repo = uow.get_repository('sales')
        else:
            # No transaction active, create standalone repo
            repo = SalesRepository()
    """
    
    _local = None
    
    @classmethod
    def get_current(cls) -> Optional[UnitOfWork]:
        """Get current UnitOfWork from thread-local storage."""
        if cls._local is None:
            return None
        return getattr(cls._local, 'uow', None)
    
    @classmethod
    def set_current(cls, uow: UnitOfWork) -> None:
        """Set current UnitOfWork in thread-local storage."""
        import threading
        if cls._local is None:
            cls._local = threading.local()
        cls._local.uow = uow
    
    @classmethod
    def clear_current(cls) -> None:
        """Clear current UnitOfWork from thread-local storage."""
        if cls._local is not None:
            cls._local.uow = None


def transactional(func: Callable = None, *, auto_commit: bool = True) -> Callable:
    """
    Decorator to wrap a method in a Unit of Work transaction.
    
    Usage:
        @transactional
        def create_order(self, data):
            order = self.sales_repo.create(data)
            self.inventory_repo.reserve_stock(order['id'])
            return order
        
        # With manual commit
        @transactional(auto_commit=False)
        def complex_operation(self, data):
            # Multiple operations
            return result  # Caller must commit
    
    Args:
        func: Function to wrap
        auto_commit: If True, commit after successful execution.
                    If False, caller must call uow.commit()
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            from backend.extensions import db
            
            with UnitOfWork(db) as uow:
                result = f(self, *args, **kwargs)
                
                if auto_commit:
                    uow.commit()
                
                return result
        
        return wrapper
    
    if func is None:
        return decorator
    return decorator(func)


class RepositoryUnitOfWork(UnitOfWork):
    """
    UnitOfWork with automatic repository initialization.
    
    Subclass this and define _repositories to auto-register
    repositories when entering the context.
    
    Usage:
        class SalesUnitOfWork(RepositoryUnitOfWork):
            _repositories = {
                'sales': SalesRepository,
                'inventory': InventoryRepository,
            }
        
        with SalesUnitOfWork() as uow:
            uow.sales.create(data)
    """
    
    _repositories: Dict[str, Type] = {}
    
    def __init__(self, db: Session = None):
        super().__init__(db)
        self._repository_instances: Dict[str, Any] = {}
    
    def __enter__(self) -> 'RepositoryUnitOfWork':
        """Enter context and initialize repositories."""
        super().__enter__()
        
        for name, repo_class in self._repositories.items():
            if isinstance(repo_class, type):
                instance = repo_class(self.db)
            else:
                instance = repo_class
            self._repository_instances[name] = instance
            self.register_repository(name, instance)
        
        return self
    
    def __getattr__(self, name: str) -> Any:
        """
        Allow dot notation access to repositories.
        
        Usage:
            with SalesUnitOfWork() as uow:
                uow.sales.create(data)  # Instead of uow.get_repository('sales')
        """
        if name in self._repository_instances:
            return self._repository_instances[name]
        raise AttributeError(f"Repository '{name}' not found in UnitOfWork")


def savepoint(func: Callable) -> Callable:
    """
    Decorator to wrap a method in a database savepoint.
    
    Unlike full transaction, savepoint allows partial rollback
    while keeping outer transaction active.
    
    Usage:
        @savepoint
        def risky_operation(self, data):
            # If this fails, only this operation rolls back
            return self._do_risky_operation(data)
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        from backend.extensions import db
        
        savepoint = db.session.begin_nested()
        try:
            result = func(self, *args, **kwargs)
            savepoint.commit()
            return result
        except Exception:
            savepoint.rollback()
            raise
    
    return wrapper
