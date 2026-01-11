from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from flask_smorest import abort
from app.models.user import User

def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user or user.role != 'admin':
                abort(403, message="Admin privilege required.")
            return fn(*args, **kwargs)
        return decorator
    return wrapper