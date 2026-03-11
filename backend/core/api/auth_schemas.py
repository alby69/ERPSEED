"""
Auth API Schemas.
"""
from marshmallow import Schema, fields, validate


class LoginSchema(Schema):
    """Schema for login request."""
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True)
    tenant_id = fields.Integer(required=False, allow_none=True)


class RegisterSchema(Schema):
    """Schema for register request."""
    email = fields.Email(required=True)
    password = fields.String(
        required=True, 
        load_only=True,
        validate=validate.Length(min=6, error="Password must be at least 6 characters")
    )
    first_name = fields.String(required=True, validate=validate.Length(min=1))
    last_name = fields.String(required=True, validate=validate.Length(min=1))
    tenant_name = fields.String(required=True, validate=validate.Length(min=1))
    tenant_slug = fields.String(
        required=True, 
        validate=[
            validate.Regexp(
                r'^[a-z0-9][a-z0-9-]*[a-z0-9]$',
                error="Slug must be lowercase alphanumeric with hyphens"
            ),
            validate.Length(min=3, max=50, error="Slug must be between 3 and 50 characters")
        ]
    )


class PasswordResetRequestSchema(Schema):
    """Schema for password reset request."""
    email = fields.Email(required=True)


class PasswordResetConfirmSchema(Schema):
    """Schema for password reset confirmation."""
    token = fields.String(required=True)
    new_password = fields.String(
        required=True, 
        load_only=True,
        validate=validate.Length(min=6, error="Password must be at least 6 characters")
    )


class PasswordChangeSchema(Schema):
    """Schema for password change."""
    current_password = fields.String(required=True, load_only=True)
    new_password = fields.String(
        required=True, 
        load_only=True,
        validate=validate.Length(min=6, error="Password must be at least 6 characters")
    )


class AuthResponseSchema(Schema):
    """Schema for auth response."""
    access_token = fields.String()
    refresh_token = fields.String()
    user = fields.Dict()


class RefreshResponseSchema(Schema):
    """Schema for refresh response."""
    access_token = fields.String()


class UserSchema(Schema):
    """Schema for user response."""
    id = fields.Integer()
    email = fields.Email()
    first_name = fields.String(allow_none=True)
    last_name = fields.String(allow_none=True)
    full_name = fields.String()
    role = fields.String()
    is_active = fields.Boolean()
    is_primary = fields.Boolean()
    tenant_id = fields.Integer(allow_none=True)
    created_at = fields.String(allow_none=True)
    updated_at = fields.String(allow_none=True)
