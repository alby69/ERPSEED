"""
ORM Fields - Field types for the dynamic ORM.

Defines all field types supported by FlaskERP's meta-model.
"""

from typing import Any, Optional
from datetime import datetime, date
import json


class Field:
    """Base class for all field types."""

    type = "unknown"

    def __init__(
        self,
        name: str = None,
        required: bool = False,
        default=None,
        index: bool = False,
        unique: bool = False,
        readonly: bool = False,
        help_text: str = None,
        **kwargs,
    ):
        self.name = name
        self.required = required
        self.default = default
        self.index = index
        self.unique = unique
        self.readonly = readonly
        self.help_text = help_text
        self.kwargs = kwargs

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name}>"


class Char(Field):
    """Short text field."""

    type = "char"
    db_type = "VARCHAR"

    def __init__(self, length: int = 255, **kwargs):
        super().__init__(**kwargs)
        self.length = length


class Text(Field):
    """Long text field."""

    type = "text"
    db_type = "TEXT"


class Integer(Field):
    """Integer number field."""

    type = "integer"
    db_type = "INTEGER"

    def __init__(self, min_value=None, max_value=None, **kwargs):
        super().__init__(**kwargs)
        self.min_value = min_value
        self.max_value = max_value


class Float(Field):
    """Decimal number field."""

    type = "float"
    db_type = "FLOAT"

    def __init__(self, digits: tuple = (10, 2), **kwargs):
        super().__init__(**kwargs)
        self.digits = digits


class Boolean(Field):
    """True/False field."""

    type = "boolean"
    db_type = "BOOLEAN"


class Date(Field):
    """Date field (without time)."""

    type = "date"
    db_type = "DATE"


class DateTime(Field):
    """DateTime field (with time)."""

    type = "datetime"
    db_type = "TIMESTAMP"


class Json(Field):
    """JSON field for arbitrary data."""

    type = "json"
    db_type = "JSONB"


class Select(Field):
    """Single selection from options."""

    type = "select"
    db_type = "VARCHAR"

    def __init__(self, options: list = None, **kwargs):
        super().__init__(**kwargs)
        self.options = options or []


class MultiSelect(Field):
    """Multiple selection from options."""

    type = "multiselect"
    db_type = "JSONB"

    def __init__(self, options: list = None, **kwargs):
        super().__init__(**kwargs)
        self.options = options or []


class Many2one(Field):
    """Many-to-one relation (ForeignKey)."""

    type = "many2one"
    db_type = "INTEGER"

    def __init__(self, model: str, on_delete: str = "cascade", **kwargs):
        super().__init__(**kwargs)
        self.relation_model = model
        self.on_delete = on_delete


class One2many(Field):
    """One-to-many relation (inverse of many2one)."""

    type = "one2many"
    db_type = None  # Not a real DB column

    def __init__(self, model: str, field: str, **kwargs):
        super().__init__(**kwargs)
        self.relation_model = model
        self.relation_field = field


class Many2many(Field):
    """Many-to-many relation."""

    type = "many2many"
    db_type = "INTEGER"  # Through table

    def __init__(self, model: str, relation_table: str = None, **kwargs):
        super().__init__(**kwargs)
        self.relation_model = model
        self.relation_table = relation_table


class File(Field):
    """File upload field."""

    type = "file"
    db_type = "VARCHAR"


class Image(Field):
    """Image upload field."""

    type = "image"
    db_type = "VARCHAR"


class Computed(Field):
    """Computed field (calculated from other fields)."""

    type = "computed"
    db_type = None  # Virtual field

    def __init__(self, compute: callable = None, depends: list = None, **kwargs):
        super().__init__(**kwargs)
        self.compute = compute
        self.depends = depends or []


# Field type mapping from SysField.type to ORM Field class
FIELD_TYPE_MAPPING = {
    "char": Char,
    "string": Char,
    "text": Text,
    "integer": Integer,
    "int": Integer,
    "float": Float,
    "decimal": Float,
    "boolean": Boolean,
    "bool": Boolean,
    "date": Date,
    "datetime": DateTime,
    "json": Json,
    "select": Select,
    "multiselect": MultiSelect,
    "many2one": Many2one,
    "one2many": One2many,
    "many2many": Many2many,
    "file": File,
    "image": Image,
    "computed": Computed,
}


def get_field_class(field_type: str) -> type:
    """Get the ORM Field class for a given SysField type."""
    return FIELD_TYPE_MAPPING.get(field_type, Char)
