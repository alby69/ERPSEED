from marshmallow import fields as mm_fields
from backend.extensions import ma
from backend.entities import (
    Soggetto, Ruolo, SoggettoRuolo,
    Indirizzo, SoggettoIndirizzo,
    Contatto, SoggettoContatto
)


class SoggettoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Soggetto
        load_instance = True
        include_fk = True
        dump_only = ("id", "created_at", "updated_at")
    
    denominazione = mm_fields.Str(dump_only=True)
    ruoli = mm_fields.List(mm_fields.Nested('SoggettoRuoloSchema'), dump_only=True)
    indirizzi = mm_fields.List(mm_fields.Nested('SoggettoIndirizzoSchema'), dump_only=True)
    contatti = mm_fields.List(mm_fields.Nested('SoggettoContattoSchema'), dump_only=True)


class SoggettoCreateSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Soggetto
        load_instance = False
        include_fk = True
        dump_only = ("id", "created_at", "updated_at")
    
    ruoli = mm_fields.List(mm_fields.Dict(), load_only=True, required=False)
    indirizzi = mm_fields.List(mm_fields.Dict(), load_only=True, required=False)
    contatti = mm_fields.List(mm_fields.Dict(), load_only=True, required=False)


class RuoloSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Ruolo
        load_instance = False
        include_fk = True
        dump_only = ("id", "created_at", "updated_at")


class SoggettoRuoloSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = SoggettoRuolo
        load_instance = True
        include_fk = True
        dump_only = ("id", "created_at", "updated_at")
    
    ruolo_codice = mm_fields.Str(dump_only=True)
    ruolo_nome = mm_fields.Str(dump_only=True)


class IndirizzoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Indirizzo
        load_instance = False
        include_fk = True
        dump_only = ("id", "created_at", "updated_at")
    
    regione = mm_fields.Str(required=False, allow_none=True)
    città = mm_fields.Str(required=False, allow_none=True)


class SoggettoIndirizzoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = SoggettoIndirizzo
        load_instance = False
        include_fk = True
        dump_only = ("id", "created_at", "updated_at")
    
    indirizzo = mm_fields.Nested('IndirizzoSchema', dump_only=True)


class ContattoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Contatto
        load_instance = False
        include_fk = True
        dump_only = ("id", "created_at", "updated_at")


class SoggettoContattoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = SoggettoContatto
        load_instance = False
        include_fk = True
        dump_only = ("id", "created_at", "updated_at")
    
    contatto = mm_fields.Nested('ContattoSchema', dump_only=True)
