from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_smorest import abort
from .models import User

def admin_required():
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            current_user_id = get_jwt_identity()
            current_user = User.query.get(current_user_id)
            if not current_user or current_user.role != 'admin':
                abort(403, message="Administrator access required.")
            return fn(*args, **kwargs)
        return decorator
    return wrapper