"""
Permission Middleware & Helpers for Field-Level RBAC and endpoint access control.
"""
from functools import wraps
from flask import abort, g, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from backend.models import User
from backend.core.services.permission_service import PermissionService, FIELD_PERMISSIONS_BY_ROLE


def field_masking_middleware(resource_type: str):
    """
    Decorator to automatically apply field-level masking on JSON response objects
    based on the current user's role and resource permissions.
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            response = f(*args, **kwargs)

            # Retrieve user
            user_id = get_jwt_identity()
            if not user_id:
                return response

            user = User.query.get(user_id)
            if not user:
                return response

            hidden_fields = PermissionService.get_hidden_fields(user, resource_type)
            if not hidden_fields:
                return response

            # Mask tuple response (data, status_code, headers) or direct dict/list
            if isinstance(response, tuple):
                data, status_code = response[0], response[1]
                headers = response[2] if len(response) > 2 else {}
            else:
                data, status_code, headers = response, 200, {}

            if isinstance(data, dict):
                data = PermissionService.mask_dict(user, resource_type, data)
            elif isinstance(data, list):
                data = [
                    PermissionService.mask_dict(user, resource_type, item) if isinstance(item, dict) else item
                    for item in data
                ]

            if headers:
                return data, status_code, headers
            return data, status_code

        return decorated
    return decorator


def get_user_permissions_summary(user: User) -> dict:
    """
    Generates a permission summary dictionary for the user including role,
    effective permissions list, and field masking restrictions.
    """
    if not user:
        return {
            "role": "anonymous",
            "permissions": [],
            "hidden_fields": {}
        }

    from backend.core.services.permission_service import DEFAULT_ROLES

    role_permissions = DEFAULT_ROLES.get(user.role, [])
    if user.role == 'admin' or user.is_primary:
        permissions = list(set([p for role_perms in DEFAULT_ROLES.values() for p in role_perms]))
    else:
        permissions = role_permissions

    hidden_fields = FIELD_PERMISSIONS_BY_ROLE.get(user.role, {})

    return {
        "role": user.role,
        "is_primary": user.is_primary,
        "permissions": permissions,
        "hidden_fields": hidden_fields
    }
