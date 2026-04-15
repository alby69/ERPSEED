from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_smorest import Api
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()
socketio = SocketIO()
api = Api()
ma = Marshmallow()