import sys
import os

# Ensure the project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Monkey-patch BEFORE importing any other modules - must be the very first thing
import eventlet

eventlet.monkey_patch()

from backend import create_app
from backend.extensions import socketio

app = create_app()
