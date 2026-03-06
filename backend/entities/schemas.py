from marshmallow import fields as mm_fields
from backend.extensions import ma
from backend.entities import (
    Soggetto, Ruolo, SoggettoRuolo,
    Indirizzo, SoggettoIndirizzo,
    Contatto, SoggettoContatto
)


class TimestampMixin:
    created_at = mm_fields.DateTime(dump_only=True)
    updated_at = mm_fields.DateTime(dump_only=True)


class SoggettoSchema(ma.SQLAlchemyAutoSchema, TimestampMixin):
    class Meta:
        model = Soggetto
        load_instance = True
        include_fk = True
        exclude = ("tenant_id",)
        dump_only = ("id",)
    
    denominazione = mm_fields.Str(dump_only=True)
    ruoli = mm_fields.List(mm_fields.Nested('SoggettoRuoloSchema'), dump_only=True)
    indirizzi = mm_fields.List(mm_fields.Nested('SoggettoIndirizzoSchema'), dump_only=True)
    contatti = mm_fields.List(mm_fields.Nested('SoggettoContattoSchema'), dump_only=True)


class SoggettoCreateSchema(ma.SQLAlchemyAutoSchema, TimestampMixin):
    class Meta:
        model = Soggetto
        load_instance = False
        include_fk = True
        exclude = ("tenant_id",)
        dump_only = ("id",)
    
    ruoli = mm_fields.List(mm_fields.Dict(), load_only=True, required=False)
    indirizzi = mm_fields.List(mm_fields.Dict(), load_only=True, required=False)
    contatti = mm_fields.List(mm_fields.Dict(), load_only=True, required=False)


class RuoloSchema(ma.SQLAlchemyAutoSchema, TimestampMixin):
    class Meta:
        model = Ruolo
        load_instance = False
        include_fk = True
        exclude = ("tenant_id",)
        dump_only = ("id",)


class SoggettoRuoloSchema(ma.SQLAlchemyAutoSchema, TimestampMixin):
    class Meta:
        model = SoggettoRuolo
        load_instance = True
        include_fk = True
        dump_only = ("id",)
    
    ruolo_codice = mm_fields.Str(dump_only=True)
    ruolo_nome = mm_fields.Str(dump_only=True)


class IndirizzoSchema(ma.SQLAlchemyAutoSchema, TimestampMixin):
    class Meta:
        model = Indirizzo
        load_instance = False
        include_fk = True
        exclude = ("tenant_id",)
        dump_only = ("id",)
    
    regione = mm_fields.Str(required=False, allow_none=True)
    città = mm_fields.Str(required=False, allow_none=True)


class SoggettoIndirizzoSchema(ma.SQLAlchemyAutoSchema, TimestampMixin):
    class Meta:
        model = SoggettoIndirizzo
        load_instance = False
        include_fk = True
        dump_only = ("id",)
    
    indirizzo = mm_fields.Nested('IndirizzoSchema', dump_only=True)


class ContattoSchema(ma.SQLAlchemyAutoSchema, TimestampMixin):
    class Meta:
        model = Contatto
        load_instance = False
        include_fk = True
        exclude = ("tenant_id",)
        dump_only = ("id",)


class SoggettoContattoSchema(ma.SQLAlchemyAutoSchema, TimestampMixin):
    class Meta:
        model = SoggettoContatto
        load_instance = False
        include_fk = True
        dump_only = ("id",)
    
    contatto = mm_fields.Nested('ContattoSchema', dump_only=True)
