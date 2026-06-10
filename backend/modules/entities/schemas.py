from marshmallow import fields as mm_fields, EXCLUDE
from backend.extensions import ma
from backend.core.schemas.schemas import BaseSchema
from backend.modules.entities import (
    Soggetto,
    Ruolo,
    SoggettoRuolo,
    Indirizzo,
    SoggettoIndirizzo,
    Contatto,
    SoggettoContatto,
)


class SoggettoSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = Soggetto
        load_instance = True
        include_fk = True
        exclude = BaseSchema.Meta.exclude + ("tenant_id",)
        dump_only = ("id",)

    denominazione = mm_fields.Function(lambda obj: obj.denominazione, dump_only=True)
    ruoli = mm_fields.List(mm_fields.Nested("SoggettoRuoloSchema"), dump_only=True)
    indirizzi = mm_fields.List(
        mm_fields.Nested("SoggettoIndirizzoSchema"), dump_only=True
    )
    contatti = mm_fields.List(
        mm_fields.Nested("SoggettoContattoSchema"), dump_only=True
    )


class SoggettoCreateSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = Soggetto
        load_instance = False
        exclude = BaseSchema.Meta.exclude + ("tenant_id",)
        dump_only = ("id",)
        unknown = EXCLUDE

    ruoli = mm_fields.List(mm_fields.Dict(), load_only=True, required=False)
    indirizzi = mm_fields.List(mm_fields.Dict(), load_only=True, required=False)
    contatti = mm_fields.List(mm_fields.Dict(), load_only=True, required=False)


class RuoloSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = Ruolo
        load_instance = False
        exclude = BaseSchema.Meta.exclude + ("tenant_id",)
        dump_only = ("id",)


class SoggettoRuoloSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = SoggettoRuolo
        dump_only = ("id",)

    ruolo_codice = mm_fields.Str(dump_only=True, attribute="ruolo.codice")
    ruolo_nome = mm_fields.Str(dump_only=True, attribute="ruolo.nome")


class IndirizzoSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = Indirizzo
        load_instance = False
        exclude = BaseSchema.Meta.exclude + ("tenant_id",)
        dump_only = ("id",)
        unknown = EXCLUDE

    regione = mm_fields.Str(required=False, allow_none=True)
    città = mm_fields.Str(required=False, allow_none=True)
    soggetto_id = mm_fields.Integer(load_only=True, required=False, allow_none=True)
    is_preferred = mm_fields.Boolean(load_only=True, required=False, allow_none=True)
    soggetto = mm_fields.Function(
        lambda obj: (
            obj.soggetti.first().soggetto.to_dict()
            if obj.soggetti.first() and obj.soggetti.first().soggetto
            else None
        ),
        dump_only=True,
    )
    regione_nome = mm_fields.Function(
        lambda obj: obj.regione_rel.nome if obj.regione_rel else None,
        dump_only=True,
    )
    provincia_nome = mm_fields.Function(
        lambda obj: obj.provincia_rel.nome if obj.provincia_rel else None,
        dump_only=True,
    )


class SoggettoIndirizzoSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = SoggettoIndirizzo
        load_instance = False
        dump_only = ("id",)

    indirizzo = mm_fields.Nested("IndirizzoSchema", dump_only=True)


class ContattoSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = Contatto
        load_instance = False
        exclude = BaseSchema.Meta.exclude + ("tenant_id",)
        dump_only = ("id",)
        unknown = EXCLUDE

    soggetto_id = mm_fields.Integer(load_only=True, required=False, allow_none=True)
    is_primary = mm_fields.Boolean(load_only=True, required=False, allow_none=True)
    soggetto = mm_fields.Function(
        lambda obj: (
            obj.soggetti.first().soggetto.to_dict()
            if obj.soggetti.first() and obj.soggetti.first().soggetto
            else None
        ),
        dump_only=True,
    )


class SoggettoContattoSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = SoggettoContatto
        load_instance = False
        dump_only = ("id",)

    contatto = mm_fields.Nested("ContattoSchema", dump_only=True)
