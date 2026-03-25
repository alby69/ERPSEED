"""
Transaction Management Module.

Provides Unit of Work pattern and transactional decorators for reliable
database operations with proper commit/rollback handling.
"""
from .unit_of_work import UnitOfWork, transactional, TransactionContext

__all__ = [
    'UnitOfWork',
    'transactional',
    'TransactionContext',
]
