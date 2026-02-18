"""Add multi-tenant support

Revision ID: 001_add_tenant_support
Revises: 
Create Date: 2026-02-18
"""
from alembic import op
import sqlalchemy as sa

revision = '001_add_tenant_support'
down_revision = 'add_workflow_tables'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Create tenants table
    op.create_table(
        'tenants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('slug', sa.String(length=80), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('website', sa.String(length=255), nullable=True),
        sa.Column('address', sa.String(length=255), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('postal_code', sa.String(length=20), nullable=True),
        sa.Column('country', sa.String(length=2), nullable=True),
        sa.Column('timezone', sa.String(length=50), nullable=True),
        sa.Column('locale', sa.String(length=5), nullable=True),
        sa.Column('currency', sa.String(length=3), nullable=True),
        sa.Column('plan', sa.String(length=50), nullable=True),
        sa.Column('plan_expires_at', sa.DateTime(), nullable=True),
        sa.Column('max_users', sa.Integer(), nullable=True),
        sa.Column('max_storage_mb', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('logo', sa.String(length=255), nullable=True),
        sa.Column('primary_color', sa.String(length=7), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )
    op.create_index('ix_tenants_name', 'tenants', ['name'])
    op.create_index('ix_tenants_slug', 'tenants', ['slug'])
    
    # 2. Create user_roles table
    op.create_table(
        'user_roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('permissions', sa.Text(), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'name', name='uix_tenant_role_name')
    )
    op.create_index('ix_user_roles_tenant_id', 'user_roles', ['tenant_id'])
    
    # 3. Add tenant_id to users (allow NULL for migration)
    op.add_column('users', sa.Column('tenant_id', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('is_primary', sa.Boolean(), nullable=True))
    op.add_column('users', sa.Column('custom_role_id', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('password_reset_token', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('password_reset_expires', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('last_login_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('login_count', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    
    op.create_index('ix_users_tenant_id', 'users', ['tenant_id'])
    op.create_unique_constraint('uix_tenant_email', 'users', ['tenant_id', 'email'])
    op.create_index('ix_user_email_lower', 'users', [sa.func.lower('email')])
    
    # 4. Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('resource_type', sa.String(length=50), nullable=False),
        sa.Column('resource_id', sa.Integer(), nullable=True),
        sa.Column('changes', sa.Text(), nullable=True),
        sa.Column('old_values', sa.Text(), nullable=True),
        sa.Column('new_values', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('endpoint', sa.String(length=255), nullable=True),
        sa.Column('method', sa.String(length=10), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_audit_tenant_created', 'audit_logs', ['tenant_id', 'created_at'])
    op.create_index('ix_audit_user_created', 'audit_logs', ['user_id', 'created_at'])
    op.create_index('ix_audit_resource', 'audit_logs', ['resource_type', 'resource_id'])


def downgrade():
    op.drop_table('audit_logs')
    op.drop_column('users', 'tenant_id')
    op.drop_column('users', 'is_primary')
    op.drop_column('users', 'custom_role_id')
    op.drop_column('users', 'password_reset_token')
    op.drop_column('users', 'password_reset_expires')
    op.drop_column('users', 'last_login_at')
    op.drop_column('users', 'login_count')
    op.drop_column('users', 'deleted_at')
    op.drop_table('user_roles')
    op.drop_table('tenants')
