from marshmallow import Schema, fields

class UserSchema(Schema):
    class Meta:
        from_attributes = True

    id = fields.Int(dump_only=True)
    email = fields.Email(required=True)
    password = fields.Str(load_only=True, required=True)
    first_name = fields.Str(allow_none=True)
    last_name = fields.Str(allow_none=True)
    role = fields.Str(dump_only=True, allow_none=True)
    force_password_change = fields.Bool(dump_only=True, allow_none=True)
    is_active = fields.Bool(dump_only=True, allow_none=True)
    is_admin = fields.Method("get_is_admin", dump_only=True)
    isAdmin = fields.Method("get_is_admin", dump_only=True)

    def get_is_admin(self, obj):
        return obj.role == 'admin'

class UserOutSchema(UserSchema):
    class Meta(UserSchema.Meta):
        exclude = ("password",)

class UserUpdateSchema(Schema):
    email = fields.Email()
    first_name = fields.Str(allow_none=True)
    last_name = fields.Str(allow_none=True)
    role = fields.Str(allow_none=True)
    is_active = fields.Bool()

class UserLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class PasswordChangeSchema(Schema):
    current_password = fields.Str(required=True)
    new_password = fields.Str(required=True)

class AdminPasswordResetSchema(Schema):
    new_password = fields.Str(required=True)

class ProjectSchema(Schema):
    class Meta:
        from_attributes = True

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    user_id = fields.Int(dump_only=True)

class PartySchema(Schema):
    class Meta:
        from_attributes = True

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    type = fields.Str(allow_none=True)
    email = fields.Email(allow_none=True)
    phone = fields.Str(allow_none=True)
    vat_number = fields.Str(allow_none=True)
    fiscal_code = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)

class ProductSchema(Schema):
    class Meta:
        from_attributes = True

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    code = fields.Str(allow_none=True)
    price = fields.Float(allow_none=True)
    description = fields.Str(allow_none=True)

class SalesOrderLineSchema(Schema):
    class Meta:
        from_attributes = True

    id = fields.Int(dump_only=True)
    product_id = fields.Int(allow_none=True)
    description = fields.Str(allow_none=True)
    quantity = fields.Float(required=True)
    unit_price = fields.Float(required=True)
    subtotal = fields.Float(dump_only=True)

class SalesOrderSchema(Schema):
    class Meta:
        from_attributes = True

    id = fields.Int(dump_only=True)
    number = fields.Str(required=True)
    date = fields.DateTime(dump_only=True)
    status = fields.Str(dump_only=True)
    customer_id = fields.Int(required=True)
    total = fields.Float(dump_only=True)
    # Nested schema per le righe dell'ordine
    lines = fields.List(fields.Nested(SalesOrderLineSchema), dump_only=True)

class AuthResponseSchema(Schema):
    access_token = fields.Str()
    refresh_token = fields.Str()
    user = fields.Nested(UserOutSchema)

class RefreshResponseSchema(Schema):
    access_token = fields.Str()

class SysFieldSchema(Schema):
    class Meta:
        from_attributes = True

    id = fields.Int(dump_only=True)
    model_id = fields.Int()
    name = fields.Str(required=True)
    title = fields.Str(allow_none=True)
    type = fields.Str(required=True)
    required = fields.Bool()
    options = fields.Str(allow_none=True)
    order = fields.Int()
    default_value = fields.Str(allow_none=True)
    formula = fields.Str(allow_none=True)
    summary_expression = fields.Str(allow_none=True)
    is_unique = fields.Bool()
    validation_regex = fields.Str(allow_none=True)
    validation_message = fields.Str(allow_none=True)
    tooltip = fields.Str(allow_none=True)

class SysModelSchema(Schema):
    class Meta:
        from_attributes = True

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    title = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    permissions = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    default_view = fields.Str(allow_none=True)
    kanban_status_field = fields.Str(allow_none=True)
    kanban_card_color_field = fields.Str(allow_none=True)
    kanban_card_avatar_field = fields.Str(allow_none=True)
    kanban_card_progress_field = fields.Str(allow_none=True)
    kanban_column_total_field = fields.Str(allow_none=True)
    fields = fields.List(fields.Nested(SysFieldSchema), dump_only=True)

class SysChartSchema(Schema):
    class Meta:
        from_attributes = True

    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    type = fields.Str(required=True)
    model_id = fields.Int(allow_none=True)
    x_axis = fields.Str(allow_none=True)
    y_axis = fields.Str(allow_none=True)
    aggregation = fields.Str(load_default='sum')
    filters = fields.Str(allow_none=True)
    content = fields.Str(allow_none=True)

class SysDashboardSchema(Schema):
    class Meta:
        from_attributes = True

    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    layout = fields.Str(allow_none=True)

class AuditLogSchema(Schema):
    class Meta:
        from_attributes = True

    id = fields.Int(dump_only=True)
    user_id = fields.Int(allow_none=True)
    user = fields.Nested(UserOutSchema, allow_none=True)
    model_name = fields.Str()
    record_id = fields.Int()
    action = fields.Str()
    changes = fields.Str(allow_none=True)
    timestamp = fields.DateTime()