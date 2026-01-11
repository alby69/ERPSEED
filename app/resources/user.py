from datetime import timedelta
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, decode_token
from flask_mail import Message
from app.extensions import db, mail
from app.models.user import User
from app.decorators import admin_required
from app.schemas import UserSchema, UserLoginSchema, PasswordResetRequestSchema, PasswordResetSchema, PasswordChangeSchema, AdminPasswordResetSchema

blp = Blueprint("users", __name__, description="Operations on users")

@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    @blp.response(201, UserSchema)
    def post(self, user_data):
        if User.query.filter_by(email=user_data["email"]).first():
            abort(409, message="A user with that email already exists.")

        user = User(
            email=user_data["email"],
            password_hash=generate_password_hash(user_data["password"])
        )
        db.session.add(user)
        db.session.commit()

        return user

@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserLoginSchema)
    def post(self, user_data):
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
        """Genera un nuovo access token usando il refresh token"""
        current_user = get_jwt_identity()
        new_access_token = create_access_token(identity=current_user)
        return {"access_token": new_access_token}

@blp.route("/me")
class UserMe(MethodView):
    @jwt_required()
    @blp.response(200, UserSchema)
    def get(self):
        """Recupera i dati dell'utente loggato (Richiede Token)"""
        user_id = get_jwt_identity()
        return User.query.get_or_404(user_id)

@blp.route("/me/password")
class UserPasswordChange(MethodView):
    @jwt_required()
    @blp.arguments(PasswordChangeSchema)
    def put(self, data):
        """Cambia la password dell'utente loggato"""
        user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)

        if not user.check_password(data["current_password"]):
            abort(401, message="Current password is incorrect.")

        user.password_hash = generate_password_hash(data["new_password"])
        user.force_password_change = False
        db.session.commit()
        return {"message": "Password updated successfully."}

@blp.route("/users")
class UserList(MethodView):
    @admin_required()
    @blp.response(200, UserSchema(many=True))
    def get(self):
        """Lista tutti gli utenti (Solo Admin)"""
        return User.query.all()

@blp.route("/users/<int:user_id>/password")
class AdminUserPasswordReset(MethodView):
    @admin_required()
    @blp.arguments(AdminPasswordResetSchema)
    def put(self, data, user_id):
        """Reset password utente (Solo Admin)"""
        user = User.query.get_or_404(user_id)
        user.password_hash = generate_password_hash(data["new_password"])
        user.force_password_change = True
        db.session.commit()
        return {"message": f"Password for user {user.email} reset successfully."}

@blp.route("/forgot-password")
class ForgotPassword(MethodView):
    @blp.arguments(PasswordResetRequestSchema)
    def post(self, data):
        """Richiede il reset della password (invia email simulata)"""
        user = User.query.filter_by(email=data["email"]).first()
        if not user:
            # Per sicurezza, non riveliamo se l'email esiste o no
            return {"message": "If the email exists, a reset link has been sent."}
        
        # Crea un token valido per 15 minuti
        expires = timedelta(minutes=15)
        reset_token = create_access_token(identity=str(user.id), additional_claims={"type": "reset"}, expires_delta=expires)
        
        link = f"http://localhost:5173/reset-password?token={reset_token}"
        
        msg = Message("Password Reset Request", recipients=[user.email])
        msg.body = f"To reset your password, visit the following link: {link}"
        
        # Invia l'email (assicurati che MAIL_SERVER sia configurato o usa un blocco try/except per dev)
        try:
            mail.send(msg)
        except Exception as e:
            print(f"Error sending email: {e}")
            # In dev mode, stampiamo comunque il link
            print(f"RESET LINK FOR {user.email}: {link}")
        
        return {"message": "If the email exists, a reset link has been sent.", "debug_link": link}

@blp.route("/reset-password")
class ResetPassword(MethodView):
    @blp.arguments(PasswordResetSchema)
    def post(self, data):
        """Resetta la password usando il token"""
        user_id = get_jwt_identity() # Questo funziona perché il token viene validato da @jwt_required o manualmente
        # Nota: flask-smorest/jwt-extended richiedono il token nell'header Authorization di solito.
        # Qui lo passiamo nel body, quindi dobbiamo decodificarlo manualmente o usare un approccio diverso.
        # Per semplicità, usiamo il token passato nel body e lo decodifichiamo.
        try:
            decoded_token = decode_token(data["token"])
            if decoded_token.get("type") != "reset":
                abort(400, message="Invalid token type.")
            
            user_id = decoded_token["sub"]
            user = User.query.get(user_id)
            if not user:
                abort(404, message="User not found.")
                
            user.password_hash = generate_password_hash(data["new_password"])
            db.session.commit()
            
            return {"message": "Password reset successfully."}
        except Exception as e:
            abort(400, message="Invalid or expired token.")