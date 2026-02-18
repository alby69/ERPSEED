"""
Tenant management API endpoints.
"""
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models import User
from backend.core.models import Tenant
from backend.core.services import TenantContext, PermissionService, Permission
from backend.core.api.tenant_schemas import (
    TenantSchema,
    TenantUpdateSchema,
    UserCreateSchema,
    UserUpdateSchema,
)
from backend.extensions import db

tenant_bp = Blueprint('tenant', __name__, description='Tenant Management')


@tenant_bp.route('/')
class TenantResource(MethodView):
    @tenant_bp.doc(security=[{"bearerAuth": []}])
    @jwt_required()
    def get(self):
        """Get current tenant info."""
        tenant = TenantContext.get_tenant()
        if not tenant:
            abort(404, message="Tenant not found")
        return tenant.to_dict()
    
    @tenant_bp.doc(security=[{"bearerAuth": []}])
    @jwt_required()
    @PermissionService.require_permission(Permission.MANAGE_TENANT)
    @tenant_bp.arguments(TenantUpdateSchema)
    @tenant_bp.response(200, TenantSchema)
    def put(self, data):
        """Update current tenant."""
        tenant = TenantContext.get_tenant()
        
        # Allowed fields for update
        allowed_fields = [
            'name', 'email', 'phone', 'website', 
            'address', 'city', 'postal_code', 'country',
            'timezone', 'locale', 'currency', 'logo', 'primary_color'
        ]
        
        for key, value in data.items():
            if key in allowed_fields:
                setattr(tenant, key, value)
        
        db.session.commit()
        return tenant.to_dict()


@tenant_bp.route('/users')
class TenantUsers(MethodView):
    @tenant_bp.doc(security=[{"bearerAuth": []}])
    @jwt_required()
    @tenant_bp.response(200)
    def get(self):
        """List users in current tenant."""
        tenant_id = TenantContext.get_tenant_id()
        users = User.query.filter_by(tenant_id=tenant_id).all()
        return [u.to_dict() for u in users]
    
    @tenant_bp.doc(security=[{"bearerAuth": []}])
    @jwt_required()
    @PermissionService.require_permission(Permission.MANAGE_USERS)
    @tenant_bp.arguments(UserCreateSchema)
    @tenant_bp.response(201)
    def post(self, data):
        """Create new user in tenant."""
        tenant = TenantContext.get_tenant()
        
        # Check user limit
        if not tenant.can_add_user():
            abort(400, message="User limit reached")
        
        # Check email not exists
        existing = User.query.filter_by(
            tenant_id=tenant.id,
            email=data.get('email', '').lower()
        ).first()
        if existing:
            abort(400, message="Email already exists in organization")
        
        user = User(
            tenant_id=tenant.id,
            email=data.get('email', '').lower(),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            role=data.get('role', 'user'),
            is_primary=False
        )
        user.set_password(data.get('password', 'changeme123'))
        
        db.session.add(user)
        db.session.commit()
        
        return user.to_dict()


@tenant_bp.route('/users/<int:user_id>')
class TenantUserDetail(MethodView):
    @tenant_bp.doc(security=[{"bearerAuth": []}])
    @jwt_required()
    @tenant_bp.response(200)
    def get(self, user_id):
        """Get user detail."""
        tenant_id = TenantContext.get_tenant_id()
        user = User.query.filter_by(id=user_id, tenant_id=tenant_id).first()
        if not user:
            abort(404, message="User not found")
        return user.to_dict()
    
    @tenant_bp.doc(security=[{"bearerAuth": []}])
    @jwt_required()
    @PermissionService.require_permission(Permission.MANAGE_USERS)
    @tenant_bp.arguments(UserUpdateSchema)
    @tenant_bp.response(200)
    def put(self, data, user_id):
        """Update user."""
        tenant_id = TenantContext.get_tenant_id()
        user = User.query.filter_by(id=user_id, tenant_id=tenant_id).first()
        if not user:
            abort(404, message="User not found")
        
        # Allowed fields
        allowed_fields = ['first_name', 'last_name', 'phone', 'role', 'is_active']
        
        for key, value in data.items():
            if key in allowed_fields:
                setattr(user, key, value)
        
        # Password change requires specific endpoint
        if 'new_password' in data:
            user.set_password(data['new_password'])
        
        db.session.commit()
        return user.to_dict()
    
    @tenant_bp.doc(security=[{"bearerAuth": []}])
    @jwt_required()
    @PermissionService.require_permission(Permission.MANAGE_USERS)
    @tenant_bp.response(204)
    def delete(self, user_id):
        """Delete (deactivate) user."""
        tenant_id = TenantContext.get_tenant_id()
        user = User.query.filter_by(id=user_id, tenant_id=tenant_id).first()
        if not user:
            abort(404, message="User not found")
        
        # Can't delete primary admin
        if user.is_primary:
            abort(400, message="Cannot delete primary admin")
        
        # Soft delete
        user.is_active = False
        db.session.commit()
        
        return '', 204
