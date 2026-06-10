import sys
import os

# Ensure the project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Monkey-patch BEFORE importing any other modules
try:
    import eventlet

    eventlet.monkey_patch()
except ImportError:
    try:
        import gevent.monkey

        gevent.monkey.patch_all()
    except ImportError:
        pass

from backend import create_app
from backend.extensions import socketio

app = create_app()
