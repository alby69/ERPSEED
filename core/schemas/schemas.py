from marshmallow import fields as mm_fields
from extensions import ma
from models import (
    User,
    Project,
    SysModel,
    SysField,
    SysView,
    SysComponent,
    SysAction,
    Product,
    SalesOrder,
    SalesOrderLine,
    PurchaseOrder,
    PurchaseOrderLine,
    SysChart,
    SysDashboard,
    ChartLibraryConfig,
)

# Import new AuditLog if available
try:
    from core.models import AuditLog
except ImportError:
    pass

# Import Soggetto (replaces Party)
try:
    from modules.entities.soggetto import Soggetto
except ImportError:
    pass

class TimestampMixin:
    created_at = mm_fields.DateTime(dump_only=True)
    updated_at = mm_fields.DateTime(dump_only=True)

class BaseSchema(ma.SQLAlchemyAutoSchema, TimestampMixin):
    """Base schema to automatically exclude timestamps and set common options."""
    class Meta:
        load_instance = True
        include_fk = True
        exclude = ("created_at", "updated_at")


class UserSummarySchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = User
        fields = ("id", "email")

class ProjectSummarySchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = Project
        fields = ("id", "name")

class PartySummarySchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = Soggetto
        fields = ("id", "codice", "denominazione", "nome", "cognome", "ragione_sociale")

class SoggettoSummarySchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = Soggetto
        fields = ("id", "codice", "denominazione", "nome", "cognome", "ragione_sociale")

class UserDisplaySchema(BaseSchema):
    """Schema for displaying user data (output)."""
    full_name = mm_fields.Function(lambda obj: obj.full_name, dump_only=True)

    class Meta(BaseSchema.Meta):
        model = User
        exclude = BaseSchema.Meta.exclude + ("password_hash",)


class UserRegisterSchema(BaseSchema):
    """Schema for registering a new user (input)."""

    class Meta(BaseSchema.Meta):
        model = User
        load_instance = False  # Set to False to handle password hashing in the view
        # Exclude password_hash from serialization
        exclude = BaseSchema.Meta.exclude + ("password_hash",)

    # Password field for loading (never shown in output)
    password = mm_fields.Str(required=True, load_only=True)


class UserUpdateSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = User
        load_instance = False
        exclude = BaseSchema.Meta.exclude + ("password_hash",)
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
    projects = mm_fields.List(mm_fields.Nested("ProjectSchema"), dump_only=True)


class RefreshResponseSchema(ma.Schema):
    access_token = mm_fields.Str()


class PasswordChangeSchema(ma.Schema):
    current_password = mm_fields.Str(required=True)
    new_password = mm_fields.Str(required=True)


# --- Schemas for Projects ---
class ProjectSchema(BaseSchema):
    # Show owner details in read-only mode
    owner = mm_fields.Nested(UserDisplaySchema(only=("id", "email")), dump_only=True)

    class Meta(BaseSchema.Meta):
        model = Project
        # Fields managed automatically by the server
        dump_only = ("id",)


class ProjectUpdateSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = Project
        partial = True
        # Do not allow changing the owner via API
        exclude = BaseSchema.Meta.exclude + ("owner_id", "name")


class ProjectMemberSchema(ma.Schema):
    userId = mm_fields.Int(required=True)


# --- Schemas for the Builder ---
class SysFieldSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = SysField


class SysModelSchema(BaseSchema):
    model_fields = mm_fields.List(mm_fields.Nested(SysFieldSchema), attribute="fields") # type: ignore
    project = mm_fields.Nested(ProjectSchema(only=("id", "name")))

    class Meta(BaseSchema.Meta):
        model = SysModel


class SysModelCreateSchema(BaseSchema):
    projectId = mm_fields.Integer(required=True)
    model_fields = mm_fields.List(mm_fields.Nested(SysFieldSchema), attribute="fields") # type: ignore

    class Meta(BaseSchema.Meta):
        model = SysModel
        exclude = BaseSchema.Meta.exclude + ("project",)


class AuditLogSchema(BaseSchema):
    user = mm_fields.Nested(UserDisplaySchema(only=("id", "email")))

    class Meta(BaseSchema.Meta):
        model = AuditLog


# --- Master Data Schemas ---
class PartySchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = Soggetto
        exclude = BaseSchema.Meta.exclude + ("tenant_id",)


class SoggettoSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = Soggetto
        exclude = BaseSchema.Meta.exclude + ("tenant_id",)


class ProductSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = Product


# --- Sales Schemas ---
class SalesOrderLineSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = SalesOrderLine
        exclude = BaseSchema.Meta.exclude + ("order",)  # Avoid recursion


class SalesOrderSchema(BaseSchema):
    lines = mm_fields.List(mm_fields.Nested(SalesOrderLineSchema))
    customer = mm_fields.Nested(
        PartySchema(only=("id", "codice", "nome", "cognome", "ragione_sociale")),
        dump_only=True,
    )
    date = mm_fields.Date(load_default=None)

    class Meta(BaseSchema.Meta):
        model = SalesOrder
        exclude = BaseSchema.Meta.exclude + ("date",)


class PurchaseOrderLineSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = PurchaseOrderLine
        exclude = BaseSchema.Meta.exclude + ("order",)


class PurchaseOrderSchema(BaseSchema):
    lines = mm_fields.List(mm_fields.Nested(PurchaseOrderLineSchema))
    supplier = mm_fields.Nested(
        SoggettoSchema(only=("id", "codice", "nome", "cognome", "ragione_sociale")),
        dump_only=True,
    )
    date = mm_fields.Date(load_default=None)

    class Meta(BaseSchema.Meta):
        model = PurchaseOrder
        exclude = BaseSchema.Meta.exclude + ("date",)

# --- Analytics Schemas ---
class ChartLibraryConfigSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = ChartLibraryConfig


class SysChartSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = SysChart


class SysDashboardSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = SysDashboard


# --- Meta-Architecture Schemas ---
class SysViewSchema(BaseSchema):
    model = mm_fields.Nested(SysModelSchema(only=("id", "name", "technical_name")))

    class Meta(BaseSchema.Meta):
        model = SysView


class SysViewCreateSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = SysView
        exclude = BaseSchema.Meta.exclude + ("model",)


class SysComponentSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = SysComponent


class SysComponentCreateSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = SysComponent


class SysActionSchema(BaseSchema):
    view = mm_fields.Nested(SysViewSchema(only=("id", "name")))
    model = mm_fields.Nested(SysModelSchema(only=("id", "name", "technical_name")))

    class Meta(BaseSchema.Meta):
        model = SysAction


class SysActionCreateSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = SysAction
