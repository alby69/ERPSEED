"""
Composition Module - Hook System for ERPE.

DEPRECATED: Only HookManager is kept for backward compatibility.
The rest of this module was experimental scaffolding and has been removed.

For CQRS patterns, use:
- backend.shared.events for domain events
- backend.domain.* for domain models
- backend.application.* for command handlers
"""

from .hooks import Hook, HookManager, HookType, hook

__all__ = [
    'Hook',
    'HookManager',
    'HookType',
    'hook',
]
