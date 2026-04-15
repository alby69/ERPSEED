from .application.handlers import UserCommandHandler
from .application.commands.user_commands import RegisterUserCommand, UpdateUserCommand, DeleteUserCommand, ResetPasswordCommand
from core.utils.utils import apply_filters, apply_sorting, paginate
from models import User
from extensions import db

class UserService:
    def __init__(self):
        self.handler = UserCommandHandler()

    def register(self, email, password, first_name=None, last_name=None, role='user'):
        cmd = RegisterUserCommand(email, password, first_name, last_name, role)
        return self.handler.handle_register(cmd)

    def update(self, userId, data):
        cmd = UpdateUserCommand(userId, data)
        return self.handler.handle_update(cmd)

    def delete(self, userId, current_userId):
        cmd = DeleteUserCommand(userId, current_userId)
        return self.handler.handle_delete(cmd)

    def reset_password(self, userId, new_password):
        cmd = ResetPasswordCommand(userId, new_password)
        return self.handler.handle_reset_password(cmd)

    def get_all(self, search_fields=None):
        query = User.query
        if search_fields:
            query = apply_filters(query, User, search_fields)
        query = apply_sorting(query, User)
        return paginate(query)

    def get_by_id(self, userId):
        return db.session.get(User, userId)

_user_service = None

def get_user_service():
    global _user_service
    if _user_service is None:
        _user_service = UserService()
    return _user_service
