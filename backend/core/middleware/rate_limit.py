from flask import request, jsonify
import time
from collections import defaultdict

class RateLimiter:
    """
    Simple in-memory rate limiter for demonstration.
    In production, use flask-limiter with Redis.
    """
    def __init__(self, requests_per_minute=60):
        self.requests_per_minute = requests_per_minute
        self.visits = defaultdict(list)

    def is_allowed(self, key):
        now = time.time()
        # Clean old visits
        self.visits[key] = [v for v in self.visits[key] if v > now - 60]

        if len(self.visits[key]) >= self.requests_per_minute:
            return False

        self.visits[key].append(now)
        return True

_limiter = RateLimiter(requests_per_minute=100)

def rate_limit_middleware(app):
    @app.before_request
    def limit_remote_addr():
        # Skip for testing or local
        if app.config.get('TESTING'):
            return

        key = request.remote_addr
        if not _limiter.is_allowed(key):
            return jsonify({"error": "Rate limit exceeded"}), 429
