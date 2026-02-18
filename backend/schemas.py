from marshmallow import fields as mm_fields
from .extensions import ma
from .models import User, Project, SysModel, SysField, Party, Product, SalesOrder, SalesOrderLine, SysChart, SysDashboard

# Import new AuditLog if available
try:
    from backend.core.models import AuditLog
except ImportError:
    pass

class UserSummarySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        fields = ("id", "email")

class ProjectSummarySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Project
        fields = ("id", "name")

class PartySummarySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Party
        fields = ("id", "name")
class UserDisplaySchema(ma.SQLAlchemyAutoSchema):
    """Schema for displaying user data (output)."""
    class Meta:
        model = User
        exclude = ("password_hash",)

class UserRegisterSchema(ma.SQLAlchemyAutoSchema):
    """Schema for registering a new user (input)."""
    class Meta:
        model = User
        load_instance = False  # Set to False to handle password hashing in the view
        # Exclude password_hash from serialization
        exclude = ("password_hash",)
    
    # Password field for loading (never shown in output)
    password = mm_fields.Str(required=True, load_only=True)

class UserUpdateSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = False
        exclude = ("password_hash",)
        # All fields are optional for updates
        partial = True

class AdminPasswordResetSchema(ma.Schema):
    new_password = mm_fields.Str(required=True)

class UserLoginSchema(ma.Schema):
    email = mm_fields.Email(required=True)
    password = mm_fields.Str(required=True)

class AuthResponseSchema(ma.Schema):
    access_token = mm_fields.Str()
    refresh_token = mm_fields.Str()
    user = mm_fields.Nested(UserDisplaySchema)

class RefreshResponseSchema(ma.Schema):
    access_token = mm_fields.Str()

class PasswordChangeSchema(ma.Schema):
    current_password = mm_fields.Str(required=True)
    new_password = mm_fields.Str(required=True)

# --- Schemas for Projects ---
class ProjectSchema(ma.SQLAlchemyAutoSchema):
    # Show owner details in read-only mode
    owner = mm_fields.Nested(UserDisplaySchema(only=("id", "email")), dump_only=True)
    
    class Meta:
        model = Project
        load_instance = True
        include_fk = True
        # Fields managed automatically by the server
        dump_only = ("id", "created_at", "updated_at", "owner")

class ProjectUpdateSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Project
        load_instance = True
        partial = True
        # Do not allow changing the owner via API
        exclude = ("owner_id",)

class ProjectMemberSchema(ma.Schema):
    user_id = mm_fields.Int(required=True)

# --- Schemas for the Builder ---
class SysFieldSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = SysField
        load_instance = True
        include_fk = True

class SysModelSchema(ma.SQLAlchemyAutoSchema):
    fields = mm_fields.List(mm_fields.Nested(SysFieldSchema))
    project = mm_fields.Nested(ProjectSchema(only=("id", "name")))
    
    class Meta:
        model = SysModel
        load_instance = True
        include_fk = True

class SysModelCreateSchema(ma.SQLAlchemyAutoSchema):
    fields = mm_fields.List(mm_fields.Nested(SysFieldSchema))
    
    class Meta:
        model = SysModel
        load_instance = True
        include_fk = True
        exclude = ("project_id", "project")

class AuditLogSchema(ma.SQLAlchemyAutoSchema):
    user = mm_fields.Nested(UserDisplaySchema(only=("id", "email")))
    class Meta:
        model = AuditLog
        load_instance = True
        include_fk = True

# --- Master Data Schemas ---
class PartySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Party
        load_instance = True
        include_fk = True
        exclude = ('tenant_id',)

class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product
        load_instance = True
        include_fk = True

# --- Sales Schemas ---
class SalesOrderLineSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = SalesOrderLine
        load_instance = True
        include_fk = True
        exclude = ("order",) # Avoid recursion

class SalesOrderSchema(ma.SQLAlchemyAutoSchema):
    lines = mm_fields.List(mm_fields.Nested(SalesOrderLineSchema))
    customer = mm_fields.Nested(PartySchema(only=("id", "name")), dump_only=True)
    class Meta:
        model = SalesOrder
        load_instance = True
        include_fk = True

# --- Analytics Schemas ---
class SysChartSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = SysChart
        load_instance = True
        include_fk = True

class SysDashboardSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = SysDashboard
        load_instance = True
        include_fk = True