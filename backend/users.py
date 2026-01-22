from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import User
from .extensions import db
from .schemas import UserSchema, AdminPasswordResetSchema, UserUpdateSchema
from .decorators import admin_required
from .utils import apply_filters, paginate, apply_sorting

blp = Blueprint("users", __name__, description="Operations on users")

@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    @blp.response(201, UserSchema)
    def post(self, user_data):
        """Registra un nuovo utente"""
        email = user_data["email"].lower()
        if User.query.filter_by(email=email).first():
            abort(409, message="A user with that email already exists.")

        user = User(
            email=email,
            first_name=user_data.get("first_name"),
            last_name=user_data.get("last_name")
        )
        user.set_password(user_data["password"])
        
        db.session.add(user)
        db.session.commit()

        return user

@blp.route("/users")
class UserList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @admin_required()
    @blp.response(200, UserSchema(many=True))
    def get(self):
        """List all users (Admins only)"""
        query = User.query
        query = apply_filters(query, User, ['email', 'first_name', 'last_name'])
        query = apply_sorting(query, User)
        items, headers = paginate(query)
        return items, 200, headers

@blp.route("/users/<int:user_id>")
class UserResource(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @admin_required()
    @blp.response(200, UserSchema)
    def get(self, user_id):
        """Get user details (Admins only)"""
        return User.query.get_or_404(user_id)

    @blp.doc(security=[{"jwt": []}])
    @admin_required()
    @blp.arguments(UserUpdateSchema)
    @blp.response(200, UserSchema)
    def put(self, data, user_id):
        """Update user details (Admins only)"""
        user = User.query.get_or_404(user_id)

        if "email" in data:
            email = data["email"].lower()
            if email != user.email:
                if User.query.filter_by(email=email).first():
                    abort(409, message="Email already in use.")
                user.email = email

        for field in ["first_name", "last_name", "role", "is_active"]:
            if field in data:
                setattr(user, field, data[field])

        db.session.commit()
        return user

    @blp.doc(security=[{"jwt": []}])
    @admin_required()
    @blp.response(204)
    def delete(self, user_id):
        """Delete a user (Admins only)"""
        current_user_id = get_jwt_identity()
        if int(current_user_id) == user_id:
            abort(403, message="You cannot delete your own account.")

        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return ""

@blp.route("/users/<int:user_id>/password")
class AdminUserPasswordReset(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @admin_required()
    @blp.arguments(AdminPasswordResetSchema)
    def put(self, data, user_id):
        """Reset a user's password (Admins only)"""
        user = User.query.get_or_404(user_id)
        user.set_password(data["new_password"])
        user.force_password_change = True
        db.session.commit()
        return {"message": f"Password for user {user.email} has been reset."}