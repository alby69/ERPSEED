from backend.models import User
from backend.extensions import db
from flask_smorest import abort
from backend.core.events.triggers import on_user_created, on_user_updated

class UserCommandHandler:
    def handle_register(self, cmd):
        email = cmd.email.lower()
        existing = User.query.filter_by(email=email).first()
        if existing:
            abort(409, message="A user with that email already exists.")

        user = User(
            email=email,
            first_name=cmd.first_name,
            last_name=cmd.last_name,
            role=cmd.role
        )
        user.set_password(cmd.password)
        db.session.add(user)
        db.session.commit()

        try:
            on_user_created(user)
        except Exception:
            pass
        return user

    def handle_update(self, cmd):
        user = db.session.get(User, cmd.userId)
        if not user:
            abort(404, message="User not found.")

        data = cmd.data
        if "email" in data:
            email = data["email"].lower()
            if email != user.email:
                existing = User.query.filter_by(email=email).first()
                if existing:
                    abort(409, message="Email already in use.")
                user.email = email

        for field in ["first_name", "last_name", "role", "is_active"]:
            if field in data:
                setattr(user, field, data[field])

        db.session.commit()
        try:
            on_user_updated(user)
        except Exception:
            pass
        return user

    def handle_delete(self, cmd):
        if int(cmd.current_userId) == cmd.userId:
            abort(403, message="You cannot delete your own account.")

        user = db.session.get(User, cmd.userId)
        if not user:
            abort(404, message="User not found.")

        db.session.delete(user)
        db.session.commit()
        return True

    def handle_reset_password(self, cmd):
        user = db.session.get(User, cmd.userId)
        if not user:
            abort(404, message="User not found.")

        user.set_password(cmd.new_password)
        user.force_password_change = True
        db.session.commit()
        return f"Password for user {user.email} has been reset."
