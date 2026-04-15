"""
Authentication service with multi-tenant support.
"""
from datetime import datetime, timedelta
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    get_jwt
)
from backend.extensions import db
from backend.models import User
from backend.core.models import Tenant, AuditLog
import secrets


class AuthService:
    """Service for authentication management."""

    @staticmethod
    def login(email, password, tenant_id=None):
        """
        Authenticate user.

        Args:
            email: User email
            password: Plain password
            tenant_id: Tenant ID (optional)

        Returns:
            dict: {access_token, refresh_token, user}

        Raises:
            ValueError: Invalid credentials
        """
        email = email.lower().strip()

        # Build query
        query = User.query.filter(db.func.lower(User.email) == email)

        # If specified, verify tenant
        if tenant_id:
            query = query.filter_by(tenant_id=tenant_id)

        user = query.first()

        # Verify credentials
        if not user or not user.check_password(password):
            # Log failed attempt
            if user:
                AuditLog.log_login(user.id, user.tenant_id, success=False,
                                  error_message="Invalid password")
            raise ValueError("Invalid email or password")

        if not user.is_active:
            AuditLog.log_login(user.id, user.tenant_id, success=False,
                              error_message="Account disabled")
            raise ValueError("Account is disabled")

        # Verify tenant is active
        if not user.tenant.is_active:
            AuditLog.log_login(user.id, user.tenant_id, success=False,
                              error_message="Tenant disabled")
            raise ValueError("Organization is disabled")

        # Record login
        user.record_login()
        db.session.commit()

        # Log successful login
        AuditLog.log_login(user.id, user.tenant_id, success=True)

        # Generate tokens
        access_token = AuthService._create_access_token(user)
        refresh_token = create_refresh_token(identity=str(user.id))

        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict(),
            'force_password_change': user.force_password_change
        }

    @staticmethod
    def _create_access_token(user):
        """Create access token with custom claims."""
        additional_claims = {
            'role': user.role,
            'tenant_id': user.tenant_id,
            'email': user.email,
            'is_primary': user.is_primary
        }
        return create_access_token(
            identity=str(user.id),
            additional_claims=additional_claims
        )

    @staticmethod
    def refresh_token():
        """Refresh access token."""
        userId = get_jwt_identity()
        user = User.query.get(userId)

        if not user or not user.is_active:
            raise ValueError("Invalid user")

        return {
            'access_token': AuthService._create_access_token(user)
        }

    @staticmethod
    def register(email, password, first_name, last_name, tenant_name, tenant_slug):
        """
        Register new tenant + admin user.

        Args:
            email: Admin email
            password: Password
            first_name: First name
            last_name: Last name
            tenant_name: Company name
            tenant_slug: URL slug

        Returns:
            dict: {access_token, refresh_token, user, tenant}
        """
        # Validate slug
        if Tenant.query.filter_by(slug=tenant_slug).first():
            raise ValueError("Slug already in use")

        # Validate email not exists
        if User.query.filter(db.func.lower(User.email) == email.lower()).first():
            raise ValueError("Email already registered")

        # Create tenant
        tenant = Tenant(
            name=tenant_name,
            slug=tenant_slug,
            is_active=True
        )
        db.session.add(tenant)
        db.session.flush()

        # Create admin user
        user = User(
            tenant_id=tenant.id,
            email=email.lower(),
            first_name=first_name,
            last_name=last_name,
            role='admin',
            is_primary=True
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        # Generate tokens
        access_token = AuthService._create_access_token(user)
        refresh_token = create_refresh_token(identity=str(user.id))

        # Seed modules for new tenant based on plan
        try:
            from backend.core.seed_modules import seed_modules_for_tenant
            seed_modules_for_tenant(tenant.id, tenant.plan)
        except Exception as e:
            print(f"Warning: Could not seed modules: {e}")

        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict(),
            'tenant': tenant.to_dict()
        }

    @staticmethod
    def request_password_reset(email):
        """
        Request password reset.

        Args:
            email: User email

        Returns:
            dict: {success: True} (don't reveal if email exists)
        """
        user = User.query.filter_by(email=email.lower()).first()

        # Don't reveal if email exists
        if not user:
            return {'success': True}

        # Generate token
        reset_token = secrets.token_urlsafe(32)
        user.password_reset_token = reset_token
        user.password_reset_expires = datetime.utcnow() + timedelta(hours=24)

        db.session.commit()

        # TODO: Send email with reset_token

        return {
            'success': True,
            'reset_token': reset_token,  # Remove in production, use email
            'expires': user.password_reset_expires
        }

    @staticmethod
    def reset_password(token, new_password):
        """Reset password with token."""
        user = User.query.filter_by(password_reset_token=token).first()

        if not user:
            raise ValueError("Invalid token")

        if user.password_reset_expires < datetime.utcnow():
            raise ValueError("Token expired")

        user.set_password(new_password)
        db.session.commit()

        # Log password change
        AuditLog.log_create(
            userId=user.id,
            tenant_id=user.tenant_id,
            resource_type='user',
            resource_id=user.id,
            new_values={'action': 'password_reset'}
        )

        return {'success': True}

    @staticmethod
    def change_password(userId, current_password, new_password):
        """Change password with verification."""
        user = User.query.get(userId)

        if not user:
            raise ValueError("User not found")

        if not user.check_password(current_password):
            raise ValueError("Current password is incorrect")

        user.set_password(new_password)
        db.session.commit()

        # Log password change
        AuditLog.log_create(
            userId=user.id,
            tenant_id=user.tenant_id,
            resource_type='user',
            resource_id=user.id,
            new_values={'action': 'password_change'}
        )

        return {'success': True}
