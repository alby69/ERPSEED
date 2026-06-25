"""
User Service - Handles user management business logic.
"""
from .base import BaseService


class UserService(BaseService):
    """
    Service for managing system users.
    Handles registration, updates, password management.
    """

    def register(self, email, password, first_name=None, last_name=None, role='user'):
        """
        Register a new user.

        Args:
            email: User email (will be lowercased).
            password: Plain text password.
            first_name: Optional first name.
            last_name: Optional last name.
            role: User role (default: 'user').

        Returns:
            Newly created User instance.

        Raises:
            409: If email already exists.
        """
        from ..models import User

        email = email.lower()

        existing = User.query.filter_by(email=email).first()
        if existing:
            from flask_smorest import abort
            abort(409, message="A user with that email already exists.")

        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        user.set_password(password)

        self.db.session.add(user)
        self.db.session.commit()

        try:
            from ..webhook_triggers import on_user_created
            on_user_created(user)
        except Exception:
            pass

        return user

    def get_all(self, search_fields=None):
        """
        Get all users with optional search.

        Args:
            search_fields: Fields to search in.

        Returns:
            Tuple of (users, pagination_headers).
        """
        from ..models import User
        from ..utils import apply_filters, apply_sorting, paginate

        query = User.query

        if search_fields:
            query = apply_filters(query, User, search_fields)

        query = apply_sorting(query, User)

        return paginate(query)

    def get_by_id(self, user_id):
        """
        Get a user by ID.

        Args:
            user_id: User ID.

        Returns:
            User instance or 404.
        """
        from ..models import User
        return self.db.session.get(User, user_id)

    def update(self, user_id, data):
        """
        Update a user.

        Args:
            user_id: ID of user to update.
            data: Dictionary of fields to update.

        Returns:
            Updated User instance.

        Raises:
            409: If email is already in use.
        """
        from ..models import User

        user = self.db.session.get(User, user_id)
        if not user:
            from flask_smorest import abort
            abort(404, message="User not found.")

        if "email" in data:
            email = data["email"].lower()
            if email != user.email:
                existing = User.query.filter_by(email=email).first()
                if existing:
                    from flask_smorest import abort
                    abort(409, message="Email already in use.")
                user.email = email

        for field in ["first_name", "last_name", "role", "is_active"]:
            if field in data:
                setattr(user, field, data[field])

        self.db.session.commit()

        try:
            from ..webhook_triggers import on_user_updated
            on_user_updated(user)
        except Exception:
            pass

        return user

    def delete(self, user_id, current_user_id):
        """
        Delete a user.

        Args:
            user_id: ID of user to delete.
            current_user_id: ID of user making the request.

        Raises:
            403: If trying to delete own account.
        """
        from ..models import User

        if int(current_user_id) == user_id:
            from flask_smorest import abort
            abort(403, message="You cannot delete your own account.")

        user = self.db.session.get(User, user_id)
        if not user:
            from flask_smorest import abort
            abort(404, message="User not found.")

        self.db.session.delete(user)
        self.db.session.commit()

    def reset_password(self, user_id, new_password):
        """
        Reset a user's password (admin function).

        Args:
            user_id: ID of user to reset.
            new_password: New password.

        Returns:
            Success message.
        """
        from ..models import User

        user = self.db.session.get(User, user_id)
        if not user:
            from flask_smorest import abort
            abort(404, message="User not found.")

        user.set_password(new_password)
        user.force_password_change = True
        self.db.session.commit()

        return f"Password for user {user.email} has been reset."

    def change_password(self, user_id, current_password, new_password):
        """
        Change own password.

        Args:
            user_id: ID of user changing password.
            current_password: Current password for verification.
            new_password: New password.

        Raises:
            401: If current password is incorrect.
        """
        from ..models import User

        user = self.db.session.get(User, user_id)
        if not user:
            from flask_smorest import abort
            abort(404, message="User not found.")

        if not user.check_password(current_password):
            from flask_smorest import abort
            abort(401, message="Current password is incorrect.")

        user.set_password(new_password)
        user.force_password_change = False
        self.db.session.commit()

        return "Password updated successfully."
