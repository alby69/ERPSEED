import logging
from functools import wraps
from flask import request
from backend.extensions import cache

logger = logging.getLogger(__name__)


def _has_query_filters():
    """Check if the request has filter/search params that should bypass cache."""
    for key in request.args:
        if key not in ("page", "per_page", "sort_by", "sort_order"):
            return True
    return False


def cached(timeout=300, key_prefix=None):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if _has_query_filters():
                return f(*args, **kwargs)
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


def cache_delete(key):
    """Delete a specific cache key, ignoring failures."""
    try:
        cache.delete(key)
    except Exception:
        logger.warning("Cache delete failed for key %s", key, exc_info=True)


def invalidate_tenant_cache(key_prefix):
    """Invalidate cache entries for all tenants by prefix. Uses pattern delete if available."""
    try:
        cache.delete(key_prefix)
    except Exception:
        logger.warning("Cache invalidate failed for prefix %s", key_prefix, exc_info=True)
