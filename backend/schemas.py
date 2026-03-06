from marshmallow import fields as mm_fields
from .extensions import ma
from .models import (
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
    from backend.core.models import AuditLog
except ImportError:
    pass

# Import Soggetto (replaces Party)
try:
    from backend.entities.soggetto import Soggetto
except ImportError:
    pass

class TimestampMixin:
    created_at = mm_fields.DateTime(dump_only=True)
    updated_at = mm_fields.DateTime(dump_only=True)


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
        model = Soggetto
        fields = ("id", "codice", "denominazione", "nome", "cognome", "ragione_sociale")


class SoggettoSummarySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Soggetto
        fields = ("id", "codice", "denominazione", "nome", "cognome", "ragione_sociale")


class UserDisplaySchema(ma.SQLAlchemyAutoSchema, TimestampMixin):
    """Schema for displaying user data (output)."""

    class Meta:
        model = User
        exclude = ("password_hash",)


class UserRegisterSchema(ma.SQLAlchemyAutoSchema, TimestampMixin):
    """Schema for registering a new user (input)."""

    class Meta:
        model = User
        load_instance = False  # Set to False to handle password hashing in the view
        # Exclude password_hash from serialization
        exclude = ("password_hash",)

    # Password field for loading (never shown in output)
    password = mm_fields.Str(required=True, load_only=True)


class UserUpdateSchema(ma.SQLAlchemyAutoSchema, TimestampMixin):
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
class ProjectSchema(ma.SQLAlchemyAutoSchema, TimestampMixin):
    # Show owner details in read-only mode
    owner = mm_fields.Nested(UserDisplaySchema(only=("id", "email")), dump_only=True)

    class Meta:
        model = Project
        load_instance = True
        include_fk = True
        # Fields managed automatically by the server
        dump_only = ("id", "created_at", "updated_at", "owner")


class ProjectUpdateSchema(ma.SQLAlchemyAutoSchema, TimestampMixin):
    class Meta:
        model = Project
        load_instance = True
        partial = True
        # Do not allow changing the owner via API
        exclude = ("owner_id", "name")


class ProjectMemberSchema(ma.Schema):
    user_id = mm_fields.Int(required=True)


# --- Schemas for the Builder ---
class SysFieldSchema(ma.SQLAlchemyAutoSchema, TimestampMixin):
    class Meta:
        model = SysField
        load_instance = True
        include_fk = True


class SysModelSchema(ma.SQLAlchemyAutoSchema, TimestampMixin):
    model_fields = mm_fields.List(mm_fields.Nested(SysFieldSchema), attribute="fields") # type: ignore
    project = mm_fields.Nested(ProjectSchema(only=("id", "name")))

    class Meta:
        model = SysModel
        load_instance = True
        include_fk = True


class SysModelCreateSchema(ma.SQLAlchemyAutoSchema, TimestampMixin):
    model_fields = mm_fields.List(mm_fields.Nested(SysFieldSchema), attribute="fields") # type: ignore

    class Meta:
        model = SysModel
        load_instance = True
        include_fk = True
        exclude = ("project_id", "project")


class AuditLogSchema(ma.SQLAlchemyAutoSchema, TimestampMixin):
    user = mm_fields.Nested(UserDisplaySchema(only=("id", "email")))

    class Meta:
        model = AuditLog
        load_instance = True
        include_fk = True


# --- Master Data Schemas ---
class PartySchema(ma.SQLAlchemyAutoSchema, TimestampMixin):
    class Meta:
        model = Soggetto
        load_instance = True
        include_fk = True
        exclude = ("tenant_id",)


class SoggettoSchema(ma.SQLAlchemyAutoSchema, TimestampMixin):
    class Meta:
        model = Soggetto
        load_instance = True
        include_fk = True
        exclude = ("tenant_id",)


class ProductSchema(ma.SQLAlchemyAutoSchema, TimestampMixin):
    class Meta:
        model = Product
        load_instance = True
        include_fk = True


# --- Sales Schemas ---
class SalesOrderLineSchema(ma.SQLAlchemyAutoSchema, TimestampMixin):
    class Meta:
        model = SalesOrderLine
        load_instance = True
        include_fk = True
        exclude = ("order",)  # Avoid recursion


class SalesOrderSchema(ma.SQLAlchemyAutoSchema, TimestampMixin):
    lines = mm_fields.List(mm_fields.Nested(SalesOrderLineSchema))
    customer = mm_fields.Nested(
        PartySchema(only=("id", "codice", "nome", "cognome", "ragione_sociale")),
        dump_only=True,
    )
    date = mm_fields.Date()

    class Meta:
        model = SalesOrder
        load_instance = True
        include_fk = True


class PurchaseOrderLineSchema(ma.SQLAlchemyAutoSchema, TimestampMixin):
    class Meta:
        model = PurchaseOrderLine
        load_instance = True
        include_fk = True
        exclude = ("order",)


class PurchaseOrderSchema(ma.SQLAlchemyAutoSchema, TimestampMixin):
    lines = mm_fields.List(mm_fields.Nested(PurchaseOrderLineSchema))
    supplier = mm_fields.Nested(
        SoggettoSchema(only=("id", "codice", "nome", "cognome", "ragione_sociale")),
        dump_only=True,
    )
    date = mm_fields.Date()

    class Meta:
        model = PurchaseOrder
        load_instance = True
        include_fk = True

# --- Analytics Schemas ---
class ChartLibraryConfigSchema(ma.SQLAlchemyAutoSchema, TimestampMixin):
    class Meta:
        model = ChartLibraryConfig
        load_instance = True


class SysChartSchema(ma.SQLAlchemyAutoSchema, TimestampMixin):
    class Meta:
        model = SysChart
        load_instance = True
        include_fk = True


class SysDashboardSchema(ma.SQLAlchemyAutoSchema, TimestampMixin):
    class Meta:
        model = SysDashboard
        load_instance = True
        include_fk = True


# --- Meta-Architecture Schemas ---
class SysViewSchema(ma.SQLAlchemyAutoSchema, TimestampMixin):
    model = mm_fields.Nested(SysModelSchema(only=("id", "name", "technical_name")))

    class Meta:
        model = SysView
        load_instance = True
        include_fk = True


class SysViewCreateSchema(ma.SQLAlchemyAutoSchema, TimestampMixin):
    class Meta:
        model = SysView
        load_instance = True
        include_fk = True
        exclude = ("model",)


class SysComponentSchema(ma.SQLAlchemyAutoSchema, TimestampMixin):
    class Meta:
        model = SysComponent
        load_instance = True
        include_fk = True


class SysComponentCreateSchema(ma.SQLAlchemyAutoSchema, TimestampMixin):
    class Meta:
        model = SysComponent
        load_instance = True
        include_fk = True


class SysActionSchema(ma.SQLAlchemyAutoSchema, TimestampMixin):
    view = mm_fields.Nested(SysViewSchema(only=("id", "name")))
    model = mm_fields.Nested(SysModelSchema(only=("id", "name", "technical_name")))

    class Meta:
        model = SysAction
        load_instance = True
        include_fk = True


class SysActionCreateSchema(ma.SQLAlchemyAutoSchema, TimestampMixin):
    class Meta:
        model = SysAction
        load_instance = True
        include_fk = True
