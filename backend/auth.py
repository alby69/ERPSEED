from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from .models import User
from .extensions import db
from .schemas import UserLoginSchema, UserSchema, AuthResponseSchema, PasswordChangeSchema, RefreshResponseSchema

auth_bp = Blueprint('auth', __name__, description="Authentication Operations")

@auth_bp.route('/login')
class Login(MethodView):
    @auth_bp.arguments(UserLoginSchema)
    @auth_bp.response(200, AuthResponseSchema)
    def post(self, user_data):
        """User login"""
        email = user_data['email'].lower()
        password = user_data['password']

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            abort(401, message="Invalid credentials.")

        if not user.is_active:
            abort(403, message="Account is disabled.")

        access_token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
        refresh_token = create_refresh_token(identity=str(user.id))

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user
        }

@auth_bp.route('/me')
class Me(MethodView):
    @auth_bp.doc(security=[{"jwt": []}])
    @jwt_required()
    @auth_bp.response(200, UserSchema)
    def get(self):
        """Get current user data"""
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            abort(404, message="User not found.")
        return user

@auth_bp.route('/refresh')
class Refresh(MethodView):
    @auth_bp.doc(security=[{"jwt": []}])
    @jwt_required(refresh=True)
    @auth_bp.response(200, RefreshResponseSchema)
    def post(self):
        """Refresh access token"""
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            abort(401, message="User not found or inactive.")

        new_access_token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
        return {"access_token": new_access_token}

@auth_bp.route('/me/password')
class PasswordChange(MethodView):
    @auth_bp.doc(security=[{"jwt": []}])
    @jwt_required()
    @auth_bp.arguments(PasswordChangeSchema)
    def put(self, data):
        """Change current user's password"""
        user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)

        if not user.check_password(data["current_password"]):
            abort(401, message="Current password is incorrect.")

        user.set_password(data["new_password"])
        user.force_password_change = False
        db.session.commit()

        return {"message": "Password updated successfully."}