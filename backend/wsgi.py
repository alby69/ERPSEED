import eventlet
eventlet.monkey_patch()

import sys
import os

# Ensure the project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend import create_app
from backend.extensions import socketio

app = create_app()

# This file is the entry point for Gunicorn.
# Command: gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 --reload backend.wsgi:app