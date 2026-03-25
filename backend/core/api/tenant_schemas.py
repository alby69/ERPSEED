"""
Tenant API Schemas.
"""
from marshmallow import Schema, fields, validate


class TenantSchema(Schema):
    """Schema for tenant response."""
    id = fields.Integer()
    name = fields.String()
    slug = fields.String()
    email = fields.Email(allow_none=True)
    phone = fields.String(allow_none=True)
    website = fields.String(allow_none=True)
    address = fields.String(allow_none=True)
    city = fields.String(allow_none=True)
    postal_code = fields.String(allow_none=True)
    country = fields.String()
    timezone = fields.String()
    locale = fields.String()
    currency = fields.String()
    is_active = fields.Boolean()
    created_at = fields.DateTime(allow_none=True)
    updated_at = fields.DateTime(allow_none=True)


class TenantUpdateSchema(Schema):
    """Schema for tenant update."""
    name = fields.String(validate=validate.Length(min=1, max=150))
    email = fields.Email(allow_none=True)
    phone = fields.String(allow_none=True)
    website = fields.String(allow_none=True)
    address = fields.String(allow_none=True)
    city = fields.String(allow_none=True)
    postal_code = fields.String(allow_none=True)
    country = fields.String()
    timezone = fields.String()
    locale = fields.String()
    currency = fields.String()
    primary_color = fields.String()


class UserCreateSchema(Schema):
    """Schema for creating a user."""
    email = fields.Email(required=True)
    password = fields.String(required=True)
    first_name = fields.String(allow_none=True)
    last_name = fields.String(allow_none=True)
    role = fields.String(validate=validate.OneOf(['admin', 'manager', 'user', 'viewer']))


class UserUpdateSchema(Schema):
    """Schema for updating a user."""
    first_name = fields.String(allow_none=True)
    last_name = fields.String(allow_none=True)
    phone = fields.String(allow_none=True)
    role = fields.String(validate=validate.OneOf(['admin', 'manager', 'user', 'viewer']))
    is_active = fields.Boolean()
    new_password = fields.String(load_only=True)
