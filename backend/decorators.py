from functools import wraps
from flask_jwt_extended import get_jwt_identity
from flask_smorest import abort
from .models import User

def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if user and user.role == 'admin':
                return fn(*args, **kwargs)
            else:
                abort(403, message="Access restricted to administrators.")
        return decorator
    return wrapper