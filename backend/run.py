#!/usr/bin/env python3
"""
Entry point per lo sviluppo locale.
Per produzione usare: gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 backend.wsgi:app
"""
import os
import sys

# Ensure the project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend import create_app
from backend.extensions import socketio

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"

    print(f"Starting ERPSeed on port {port}...")
    socketio.run(app, host="0.0.0.0", port=port, debug=debug)
