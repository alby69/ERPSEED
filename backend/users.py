from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity

from .schemas import UserDisplaySchema, UserRegisterSchema, AdminPasswordResetSchema, UserUpdateSchema
from .decorators import admin_required
from .services import UserService

blp = Blueprint("users", __name__, description="Operations on users")

user_service = UserService()


@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserRegisterSchema)
    @blp.response(201, UserDisplaySchema)
    def post(self, user_data):
        """Register a new user"""
        data = user_data.__dict__ if hasattr(user_data, '__dict__') else user_data
        
        return user_service.register(
            email=data['email'],
            password=data['password'],
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            role=data.get('role', 'user')
        )


@blp.route("/users")
class UserList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @admin_required()
    @blp.response(200, UserDisplaySchema(many=True))
    def get(self):
        """List all users (Admins only)"""
        items, headers = user_service.get_all(search_fields=['email', 'first_name', 'last_name'])
        return items, 200, headers


@blp.route("/users/<int:user_id>")
class UserResource(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @admin_required()
    @blp.response(200, UserDisplaySchema)
    def get(self, user_id):
        """Get user details (Admins only)"""
        return user_service.get_by_id(user_id)

    @blp.doc(security=[{"jwt": []}])
    @admin_required()
    @blp.arguments(UserUpdateSchema)
    @blp.response(200, UserDisplaySchema)
    def put(self, update_data, user_id):
        """Update user details (Admins only)"""
        data = update_data.__dict__ if hasattr(update_data, '__dict__') else update_data
        return user_service.update(user_id, data)

    @blp.doc(security=[{"jwt": []}])
    @admin_required()
    @blp.response(204)
    def delete(self, user_id):
        """Delete a user (Admins only)"""
        current_user_id = get_jwt_identity()
        user_service.delete(user_id, current_user_id)
        return ""


@blp.route("/users/<int:user_id>/password")
class AdminUserPasswordReset(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @admin_required()
    @blp.arguments(AdminPasswordResetSchema)
    def put(self, data, user_id):
        """Reset a user's password (Admins only)"""
        password_data = data.__dict__ if hasattr(data, '__dict__') else data
        return {"message": user_service.reset_password(user_id, password_data['new_password'])}
