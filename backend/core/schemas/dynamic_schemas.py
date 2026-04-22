from marshmallow import fields, Schema

class AnyJsonSchema(Schema):
    """Generic schema that allows any JSON structure."""
    class Meta:
        unknown = "INCLUDE"

class BulkDeleteSchema(Schema):
    """Schema for bulk deletion operations."""
    ids = fields.List(fields.Int(), required=True)

class ImportFileSchema(Schema):
    """Schema for file import operations."""
    file = fields.Raw(metadata={"type": "file"}, required=True)

class ExportResponseSchema(Schema):
    """Schema for export operations response (JSON format)."""
    class Meta:
        unknown = "INCLUDE"
