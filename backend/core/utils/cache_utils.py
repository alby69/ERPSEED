from functools import wraps
from flask import request
from backend.extensions import cache


def cached(timeout=300, key_prefix=None):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            tenant_id = request.headers.get("X-Tenant-ID", "0")
            base_key = key_prefix or f"{f.__module__}.{f.__name__}"
            cache_key = f"{base_key}:{tenant_id}"
            result = cache.get(cache_key)
            if result is not None:
                return result
            result = f(*args, **kwargs)
            cache.set(cache_key, result, timeout=timeout)
            return result
        return wrapper
    return decorator
