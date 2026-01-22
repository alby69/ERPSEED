from backend import create_app
from backend.extensions import socketio

app = create_app()

if __name__ == '__main__':
    # Use Gunicorn to run the app, see docker-compose.yml
    # This is a fallback for running without gunicorn/docker
    socketio.run(app, host='0.0.0.0', port=5000)