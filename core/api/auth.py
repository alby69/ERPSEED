"""
Authentication API endpoints.
"""
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User
from core.models import Tenant
from core.services import AuthService, TenantContext
from extensions import db
from core.api.auth_schemas import (
    LoginSchema,
    RegisterSchema,
    PasswordResetRequestSchema,
    PasswordResetConfirmSchema,
    PasswordChangeSchema,
    AuthResponseSchema,
    RefreshResponseSchema,
    UserSchema,
)

auth_bp = Blueprint('auth', __name__, description='Authentication')


@auth_bp.route('/register')
class Register(MethodView):
    @auth_bp.arguments(RegisterSchema)
    @auth_bp.response(201, AuthResponseSchema)
    def post(self, data):
        """
        Register new tenant and admin user.

        Body:
            - email: Admin email
            - password: Password
            - first_name: First name
            - last_name: Last name
            - tenant_name: Company name
            - tenant_slug: URL slug (e.g., 'my-company')
        """
        try:
            result = AuthService.register(
                email=data.get('email', ''),
                password=data.get('password', ''),
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', ''),
                tenant_name=data.get('tenant_name', ''),
                tenant_slug=data.get('tenant_slug', '')
            )
            return result
        except ValueError as e:
            abort(400, message=str(e))


@auth_bp.route('/login')
class Login(MethodView):
    @auth_bp.arguments(LoginSchema)
    @auth_bp.response(200, AuthResponseSchema)
    def post(self, data):
        """
        User login.

        Body:
            - email: User email
            - password: Password
            - tenant_id: Optional tenant ID (for direct API login)
        """
        try:
            result = AuthService.login(
                email=data.get('email', ''),
                password=data.get('password', ''),
                tenant_id=data.get('tenant_id')
            )
            return result
        except ValueError as e:
            abort(401, message=str(e))


@auth_bp.route('/me')
class CurrentUser(MethodView):
    @auth_bp.doc(security=[{"bearerAuth": []}])
    @jwt_required()
    @auth_bp.response(200, UserSchema)
    def get(self):
        """Get current user info."""
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            abort(404, message="User not found")
        return user.to_dict()


@auth_bp.route('/refresh')
class Refresh(MethodView):
    @auth_bp.doc(security=[{"bearerAuth": []}])
    @jwt_required(refresh=True)
    @auth_bp.response(200, RefreshResponseSchema)
    def post(self):
        """Refresh access token."""
        try:
            return AuthService.refresh_token()
        except ValueError as e:
            abort(401, message=str(e))


@auth_bp.route('/password/reset')
class PasswordResetRequest(MethodView):
    @auth_bp.arguments(PasswordResetRequestSchema)
    @auth_bp.response(200, schema={"type": "object"})
    def post(self, data):
        """
        Request password reset.

        Body:
            - email: User email
        """
        result = AuthService.request_password_reset(data.get('email', ''))
        return result


@auth_bp.route('/password/reset/confirm')
class PasswordResetConfirm(MethodView):
    @auth_bp.arguments(PasswordResetConfirmSchema)
    @auth_bp.response(200, schema={"type": "object"})
    def post(self, data):
        """
        Confirm password reset.

        Body:
            - token: Reset token
            - new_password: New password
        """
        try:
            result = AuthService.reset_password(
                token=data.get('token', ''),
                new_password=data.get('new_password', '')
            )
            return result
        except ValueError as e:
            abort(400, message=str(e))


@auth_bp.route('/me/password')
class PasswordChange(MethodView):
    @auth_bp.doc(security=[{"bearerAuth": []}])
    @jwt_required()
    @auth_bp.arguments(PasswordChangeSchema)
    @auth_bp.response(200, schema={"type": "object"})
    def put(self, data):
        """
        Change current user's password.

        Body:
            - current_password: Current password
            - new_password: New password
        """
        user_id = get_jwt_identity()

        try:
            result = AuthService.change_password(
                user_id=int(user_id),
                current_password=data.get('current_password', ''),
                new_password=data.get('new_password', '')
            )
            return result
        except ValueError as e:
            abort(400, message=str(e))
