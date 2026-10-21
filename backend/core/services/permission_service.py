"""
Permission system - role-based access control.
"""
import json
from functools import wraps
from flask import abort
from flask_jwt_extended import get_jwt


class Permission:
    """Permission constants."""

    # Users
    MANAGE_USERS = 'manage_users'
    VIEW_USERS = 'view_users'

    # Tenant
    MANAGE_TENANT = 'manage_tenant'
    VIEW_TENANT = 'view_tenant'

    # Data
    VIEW_ALL = 'view_all'
    EDIT_ALL = 'edit_all'
    DELETE_ALL = 'delete_all'

    # Modules
    VIEW_ACCOUNTING = 'view_accounting'
    MANAGE_ACCOUNTING = 'manage_accounting'
    VIEW_INVENTORY = 'view_inventory'
    MANAGE_INVENTORY = 'manage_inventory'
    VIEW_SALES = 'view_sales'
    MANAGE_SALES = 'manage_sales'
    VIEW_PRODUCTS = 'view_products'
    MANAGE_PRODUCTS = 'manage_products'
    VIEW_PARTIES = 'view_parties'
    MANAGE_PARTIES = 'manage_parties'


# Default roles with permissions
DEFAULT_ROLES = {
    'admin': [
        Permission.MANAGE_USERS,
        Permission.VIEW_USERS,
        Permission.MANAGE_TENANT,
        Permission.VIEW_TENANT,
        Permission.VIEW_ALL,
        Permission.EDIT_ALL,
        Permission.DELETE_ALL,
        Permission.MANAGE_ACCOUNTING,
        Permission.MANAGE_INVENTORY,
        Permission.MANAGE_SALES,
        Permission.MANAGE_PRODUCTS,
        Permission.MANAGE_PARTIES,
    ],
    'manager': [
        Permission.VIEW_ALL,
        Permission.EDIT_ALL,
        Permission.MANAGE_SALES,
        Permission.MANAGE_PRODUCTS,
        Permission.MANAGE_PARTIES,
    ],
    'user': [
        Permission.VIEW_SALES,
        Permission.MANAGE_SALES,
        Permission.VIEW_PRODUCTS,
        Permission.MANAGE_PRODUCTS,
        Permission.VIEW_PARTIES,
        Permission.MANAGE_PARTIES,
    ],
    'viewer': [
        Permission.VIEW_ALL,
    ]
}

# Restricted fields by role for field-level RBAC masking
FIELD_PERMISSIONS_BY_ROLE = {
    'user': {
        'product': ['cost_price', 'margin'],
        'sales_order': ['cost_price', 'profit_margin'],
    },
    'viewer': {
        'product': ['cost_price', 'margin', 'unit_cost'],
        'sales_order': ['cost_price', 'profit_margin', 'discount_percent'],
    }
}


class PermissionService:
    """Service for permission management."""

    @staticmethod
    def has_permission(user, permission):
        """
        Check if user has a permission.

        Args:
            user: User instance
            permission: Permission string

        Returns:
            bool
        """
        if not user:
            return False

        # Admin has all permissions
        if user.role == 'admin':
            return True

        # Primary admin has all permissions
        if user.is_primary:
            return True

        # Check custom role
        if user.custom_role:
            try:
                permissions = json.loads(user.custom_role.permissions or '[]')
                return permission in permissions
            except (json.JSONDecodeError, TypeError):
                pass

        # Check default role
        role_permissions = DEFAULT_ROLES.get(user.role, [])
        return permission in role_permissions

    @staticmethod
    def has_any_permission(user, permissions):
        """Check if user has any of the permissions."""
        return any(PermissionService.has_permission(user, p) for p in permissions)

    @staticmethod
    def has_all_permissions(user, permissions):
        """Check if user has all permissions."""
        return all(PermissionService.has_permission(user, p) for p in permissions)

    @staticmethod
    def get_hidden_fields(user, resource_type: str) -> list:
        """
        Returns a list of field names that should be hidden/masked for a given user and resource type.
        """
        if not user or user.role in ['admin', 'manager'] or getattr(user, 'is_primary', False):
            return []

        restricted = FIELD_PERMISSIONS_BY_ROLE.get(user.role, {})
        return restricted.get(resource_type, [])

    @staticmethod
    def mask_dict(user, resource_type: str, data: dict) -> dict:
        """
        Masks/removes restricted fields from a single dictionary object based on user permissions.
        """
        hidden_fields = PermissionService.get_hidden_fields(user, resource_type)
        if not hidden_fields or not isinstance(data, dict):
            return data

        masked = dict(data)
        for field in hidden_fields:
            if field in masked:
                masked.pop(field, None)
        return masked

    @staticmethod
    def require_permission(permission):
        """
        Decorator to require a permission.
        """
        def decorator(f):
            @wraps(f)
            def decorated(*args, **kwargs):
                from flask_jwt_extended import get_jwt_identity
                from backend.core.models import User

                userId = get_jwt_identity()
                user = User.query.get(userId)

                if not user:
                    abort(404, description="User not found")

                if not PermissionService.has_permission(user, permission):
                    abort(403, description="Permission denied")

                return f(*args, **kwargs)
            return decorated
        return decorator

    @staticmethod
    def require_any_permission(permissions):
        """Decorator to require any of the permissions."""
        def decorator(f):
            @wraps(f)
            def decorated(*args, **kwargs):
                from flask_jwt_extended import get_jwt_identity
                from backend.core.models import User

                userId = get_jwt_identity()
                user = User.query.get(userId)

                if not user:
                    abort(404, description="User not found")

                if not PermissionService.has_any_permission(user, permissions):
                    abort(403, description="Permission denied")

                return f(*args, **kwargs)
            return decorated
        return decorator
