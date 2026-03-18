from functools import wraps
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from flask_smorest import abort
from .models import User
from .core.services.tenant_context import TenantContext

def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if user and user.role == 'admin':
                return fn(*args, **kwargs)
            else:
                abort(403, message="Access restricted to administrators.")
        return decorator
    return wrapper

def tenant_required(f):
    """
    A decorator to ensure a tenant context is set.
    It retrieves the tenant_id and passes it as a keyword argument
    to the decorated function.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        tenant_id = TenantContext.get_tenant_id()
        if tenant_id is None:
            abort(403, message="Tenant context not found. A tenant must be selected to perform this action.")
        
        # Pass tenant_id to the decorated function
        return f(*args, tenant_id=tenant_id, **kwargs)
    return decorated_function