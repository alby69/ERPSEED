import logging
from functools import wraps
from flask import request
from backend.extensions import cache

logger = logging.getLogger(__name__)


def cached(timeout=300, key_prefix=None):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            tenant_id = request.headers.get("X-Tenant-ID", "0")
            base_key = key_prefix or f"{f.__module__}.{f.__name__}"
            cache_key = f"{base_key}:{tenant_id}"
            try:
                result = cache.get(cache_key)
                if result is not None:
                    return result
            except Exception:
                logger.warning("Cache get failed for key %s", cache_key, exc_info=True)
            result = f(*args, **kwargs)
            try:
                cache.set(cache_key, result, timeout=timeout)
            except Exception:
                logger.warning("Cache set failed for key %s", cache_key, exc_info=True)
            return result
        return wrapper
    return decorator


def cache_get(key):
    """Get from cache, returning None on failure."""
    try:
        return cache.get(key)
    except Exception:
        logger.warning("Cache get failed for key %s", key, exc_info=True)
        return None


def cache_set(key, value, timeout=300):
    """Set in cache, ignoring failures."""
    try:
        cache.set(key, value, timeout=timeout)
    except Exception:
        logger.warning("Cache set failed for key %s", key, exc_info=True)
