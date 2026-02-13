import os
from datetime import timedelta
from flask.views import MethodView
from flask import request, current_app
from flask_smorest import Blueprint, abort
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, decode_token
from flask_mail import Message
from marshmallow import fields
from app.extensions import db, mail
from backend.models import User
from app.decorators import admin_required
from app.schemas import UserSchema, UserLoginSchema, PasswordResetRequestSchema, PasswordResetSchema, PasswordChangeSchema, AdminPasswordResetSchema

# Schema for user editing: allows empty password (which will be ignored)
class UserEditSchema(UserSchema):
    password = fields.String(load_default=None, allow_none=True, validate=None)

def save_avatar(file):
    if not file: return None
    filename = secure_filename(file.filename)
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    file.save(os.path.join(upload_folder, filename))
    return filename

blp = Blueprint("users", __name__, description="Operations on users")

@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    @blp.response(201, UserSchema)
    def post(self, user_data):
        """Register a new user."""
        if User.query.filter_by(email=user_data["email"]).first():
            abort(409, message="A user with that email already exists.")

        user = User(
            email=user_data["email"]
        )
        user.set_password(user_data["password"])
        db.session.add(user)
        db.session.commit()

        return user

@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserLoginSchema)
    def post(self, user_data):
        """Logs a user in and returns tokens."""
        user = User.query.filter_by(email=user_data["email"]).first()
        if user and user.check_password(user_data["password"]):
            access_token = create_access_token(identity=str(user.id))
            refresh_token = create_refresh_token(identity=str(user.id))
            return {
                "access_token": access_token, 
                "refresh_token": refresh_token,
                "force_password_change": user.force_password_change
            }
        abort(401, message="Invalid credentials.")

@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        """Generate a new access token using the refresh token."""
        current_user = get_jwt_identity()
        new_access_token = create_access_token(identity=current_user)
        return {"access_token": new_access_token}

@blp.route("/me")
class UserMe(MethodView):
    @jwt_required()
    @blp.response(200, UserSchema)
    def get(self):
        """Get the data of the logged-in user (Token Required)."""
        user_id = get_jwt_identity()
        return User.query.get_or_404(user_id)

    @jwt_required()
    @blp.response(200, UserSchema)
    def put(self):
        """Update the profile of the logged-in user (Avatar, Name, Surname)."""
        user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)
        
        # Handle multipart/form-data for file upload
        if 'avatar' in request.files:
            filename = save_avatar(request.files['avatar'])
            if filename:
                user.avatar = filename
        
        data = request.form
        if 'first_name' in data: user.first_name = data['first_name']
        if 'last_name' in data: user.last_name = data['last_name']
        
        db.session.commit()
        return user

@blp.route("/me/password")
class UserPasswordChange(MethodView):
    @jwt_required()
    @blp.arguments(PasswordChangeSchema)
    def put(self, data):
        """Change the password of the logged-in user."""
        user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)

        if not user.check_password(data["current_password"]):
            abort(401, message="Current password is incorrect.")

        user.set_password(data["new_password"])
        user.force_password_change = False
        db.session.commit()
        return {"message": "Password updated successfully."}

@blp.route("/users")
class UserList(MethodView):
    @admin_required()
    @blp.response(200, UserSchema(many=True))
    def get(self):
        """List all users (Admin Only)."""
        return User.query.all()

    @admin_required()
    @blp.arguments(UserSchema)
    @blp.response(201, UserSchema)
    def post(self, user_data):
        """Create a new user (Admin Only)."""
        if User.query.filter_by(email=user_data["email"]).first():
            abort(409, message="A user with that email already exists.")
        
        user = User(
            email=user_data["email"],
            first_name=user_data.get("first_name"),
            last_name=user_data.get("last_name"),
            role=user_data.get("role", "user"),
            is_active=user_data.get("is_active", True)
        )
        if "password" in user_data and user_data["password"]:
            user.set_password(user_data["password"])
        
        db.session.add(user)
        db.session.commit()
        return user

@blp.route("/users/<int:user_id>")
class UserResource(MethodView):
    @admin_required()
    @blp.response(200, UserSchema)
    def get(self, user_id):
        """Get user details (Admin Only)."""
        return User.query.get_or_404(user_id)

    @admin_required()
    @blp.arguments(UserEditSchema(partial=True))
    @blp.response(200, UserSchema)
    def put(self, user_data, user_id):
        """Edit a user (Admin Only)."""
        user = User.query.get_or_404(user_id)
        
        if "email" in user_data and user_data["email"] != user.email:
            if User.query.filter_by(email=user_data["email"]).first():
                abort(409, message="A user with that email already exists.")

        for key, value in user_data.items():
            if key == "password":
                if value:
                    user.set_password(value)
            else:
                setattr(user, key, value)
        
        db.session.commit()
        return user

    @admin_required()
    @blp.response(204)
    def delete(self, user_id):
        """Delete a user (Admin Only)."""
        user = User.query.get_or_404(user_id)
        current_user_id = get_jwt_identity()
        if str(user.id) == str(current_user_id):
             abort(400, message="Cannot delete yourself.")
             
        db.session.delete(user)
        db.session.commit()
        return ""

@blp.route("/users/<int:user_id>/password")
class AdminUserPasswordReset(MethodView):
    @admin_required()
    @blp.arguments(AdminPasswordResetSchema)
    def put(self, data, user_id):
        """Reset a user's password (Admin Only)."""
        user = User.query.get_or_404(user_id)
        user.set_password(data["new_password"])
        user.force_password_change = True
        db.session.commit()
        return {"message": f"Password for user {user.email} reset successfully."}

@blp.route("/forgot-password")
class ForgotPassword(MethodView):
    @blp.arguments(PasswordResetRequestSchema)
    def post(self, data):
        """Request a password reset (sends a simulated email)."""
        user = User.query.filter_by(email=data["email"]).first()
        if not user:
            # For security, we don't reveal if the email exists or not
            return {"message": "If the email exists, a reset link has been sent."}
        
        # Create a token valid for 15 minutes
        expires = timedelta(minutes=15)
        reset_token = create_access_token(identity=str(user.id), additional_claims={"type": "reset"}, expires_delta=expires)
        
        # TODO: The URL should not be hardcoded
        link = f"http://localhost:5173/reset-password?token={reset_token}"
        
        msg = Message("Password Reset Request", recipients=[user.email])
        msg.body = f"To reset your password, visit the following link: {link}"
        
        # Send the email (make sure MAIL_SERVER is configured or use a try/except block for dev)
        try:
            mail.send(msg)
        except Exception as e:
            print(f"Error sending email: {e}")
            # In dev mode, we still print the link for testing
            print(f"RESET LINK FOR {user.email}: {link}")
        
        return {"message": "If the email exists, a reset link has been sent.", "debug_link": link}

@blp.route("/reset-password")
class ResetPassword(MethodView):
    @blp.arguments(PasswordResetSchema)
    def post(self, data):
        """Reset the password using the token."""
        # Note: flask-smorest/jwt-extended usually expect the token in the Authorization header.
        # Here we pass it in the body, so we have to decode it manually.
        try:
            decoded_token = decode_token(data["token"])
            if decoded_token.get("type") != "reset":
                abort(400, message="Invalid token type.")
            
            user_id = decoded_token["sub"]
            user = User.query.get(user_id)
            if not user:
                abort(404, message="User not found.")
                
            user.set_password(data["new_password"])
            db.session.commit()
            
            return {"message": "Password reset successfully."}
        except Exception as e:
            abort(400, message="Invalid or expired token.")