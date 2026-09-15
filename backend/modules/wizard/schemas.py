"""
Wizard Marshmallow Schemas.
"""
from marshmallow import Schema, fields


class WizardSessionSchema(Schema):
    id = fields.Int(dump_only=True)
    tenant_id = fields.Int(dump_only=True)
    session_name = fields.Str()
    industry = fields.Str(allow_none=True)
    answers = fields.Dict(allow_none=True)
    domain_spec = fields.Dict(allow_none=True)
    status = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class DomainAnalysisRequestSchema(Schema):
    company_name = fields.Str(required=False, dump_default="Mia Azienda")
    industry = fields.Str(required=False, dump_default="Generico")
    has_inventory = fields.Bool(required=False, dump_default=True)
    has_purchases = fields.Bool(required=False, dump_default=True)
    has_projects = fields.Bool(required=False, dump_default=False)
    custom_description = fields.Str(required=False, dump_default="")


class ProvisionDomainRequestSchema(Schema):
    session_id = fields.Int(required=False, allow_none=True)
    project_id = fields.Int(required=False, dump_default=1)
    domain_spec = fields.Dict(required=True)
