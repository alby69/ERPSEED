from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity

from core.schemas.schemas import UserDisplaySchema, UserRegisterSchema, AdminPasswordResetSchema, UserUpdateSchema
from core.decorators.decorators import admin_required
from modules.users.service import get_user_service

blp = Blueprint("users", __name__, description="Operations on users")

user_service = get_user_service()


@blp.route("/registrations")
class UserRegister(MethodView):
    @blp.arguments(UserRegisterSchema)
    @blp.response(201, UserDisplaySchema)
    def post(self, user_data):
        """Register a new user"""
        return user_service.register(
            email=user_data['email'],
            password=user_data['password'],
            first_name=user_data.get('first_name'),
            last_name=user_data.get('last_name'),
            role=user_data.get('role', 'user')
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


@blp.route("/users/<int:userId>")
class UserResource(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @admin_required()
    @blp.response(200, UserDisplaySchema)
    def get(self, userId):
        """Get user details (Admins only)"""
        return user_service.get_by_id(userId)

    @blp.doc(security=[{"jwt": []}])
    @admin_required()
    @blp.arguments(UserUpdateSchema)
    @blp.response(200, UserDisplaySchema)
    def put(self, update_data, userId):
        """Update user details (Admins only)"""
        return user_service.update(userId, update_data)

    @blp.doc(security=[{"jwt": []}])
    @admin_required()
    @blp.response(204)
    def delete(self, userId):
        """Delete a user (Admins only)"""
        current_userId = get_jwt_identity()
        user_service.delete(userId, current_userId)
        return ""


@blp.route("/users/<int:userId>/password")
class AdminUserPasswordReset(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @admin_required()
    @blp.arguments(AdminPasswordResetSchema)
    @blp.response(200)
    def put(self, data, userId):
        """Reset a user's password (Admins only)"""
        return {"message": user_service.reset_password(userId, data['new_password'])}
