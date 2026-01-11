from marshmallow import Schema, fields, ValidationError, post_load
from app.models.sales import SalesOrderLine

def validate_vat_number(value):
    """Valida la Partita IVA italiana (11 cifre, checksum)."""
    if not value:
        return

    if len(value) != 11 or not value.isdigit():
        raise ValidationError("La Partita IVA deve contenere 11 cifre numeriche.")

    s = 0
    for i in range(11):
        n = int(value[i])
        if (i % 2) == 1: # Indici dispari sono le posizioni pari (2, 4, 6...)
            n *= 2
            if n > 9:
                n -= 9
        s += n
    
    if s % 10 != 0:
        raise ValidationError("Partita IVA non valida (checksum errato).")

def validate_fiscal_code(value):
    """Valida il Codice Fiscale (16 caratteri per persone, 11 per aziende)."""
    if not value:
        return

    value = value.upper()
    
    # Caso Azienda (11 cifre, stesso controllo P.IVA)
    if len(value) == 11:
        if not value.isdigit():
             raise ValidationError("Il Codice Fiscale numerico deve contenere 11 cifre.")
        validate_vat_number(value)
        return

    # Caso Persona Fisica (16 caratteri)
    if len(value) != 16 or not value.isalnum():
        raise ValidationError("Il Codice Fiscale deve contenere 16 caratteri alfanumerici (o 11 numerici per aziende).")

    # Calcolo Checksum per 16 caratteri (Algoritmo di controllo CIN)
    odd_values = {
        '0': 1, '1': 0, '2': 5, '3': 7, '4': 9, '5': 13, '6': 15, '7': 17, '8': 19, '9': 21,
        'A': 1, 'B': 0, 'C': 5, 'D': 7, 'E': 9, 'F': 13, 'G': 15, 'H': 17, 'I': 19, 'J': 21,
        'K': 2, 'L': 4, 'M': 18, 'N': 20, 'O': 11, 'P': 3, 'Q': 6, 'R': 8, 'S': 12, 'T': 14,
        'U': 16, 'V': 10, 'W': 22, 'X': 25, 'Y': 24, 'Z': 23
    }

    total = 0
    for i in range(15):
        char = value[i]
        # Posizioni dispari (1, 3...) hanno indice pari (0, 2...) in Python
        if i % 2 == 0:
            total += odd_values.get(char, 0)
        else:
            # Posizioni pari (2, 4...) hanno indice dispari (1, 3...)
            # Se è numero usa il valore numerico, se lettera usa ord(c) - ord('A')
            if char.isdigit():
                total += int(char)
            else:
                total += ord(char) - ord('A')

    control_char = chr((total % 26) + ord('A'))
    if control_char != value[15]:
        raise ValidationError("Codice Fiscale non valido (checksum errato).")

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)
    created_at = fields.DateTime(dump_only=True)
    role = fields.Str(dump_only=True)

class UserLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)

class PasswordResetRequestSchema(Schema):
    email = fields.Email(required=True)

class PasswordResetSchema(Schema):
    token = fields.Str(required=True)
    new_password = fields.Str(required=True)

class PasswordChangeSchema(Schema):
    current_password = fields.Str(required=True)
    new_password = fields.Str(required=True)

class AdminPasswordResetSchema(Schema):
    new_password = fields.Str(required=True)

class PartySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    type = fields.Str(load_default='company') # 'company' o 'person'
    vat_number = fields.Str(validate=validate_vat_number)
    fiscal_code = fields.Str(validate=validate_fiscal_code)
    email = fields.Email()
    phone = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class ProductSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str()
    price = fields.Float()
    sku = fields.Str()
    image = fields.Str(dump_only=True) # Il nome file viene restituito, l'upload è gestito a parte
    supplier_id = fields.Int()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class SalesOrderLineSchema(Schema):
    id = fields.Int(dump_only=True)
    product_id = fields.Int(required=True)
    product_name = fields.Str(dump_only=True, attribute="product.name") # Campo semantico da tabella correlata
    quantity = fields.Float(required=True)
    unit_price = fields.Float(required=True)
    total = fields.Float(dump_only=True)

class SalesOrderSchema(Schema):
    id = fields.Int(dump_only=True)
    number = fields.Str(required=True)
    date = fields.DateTime(dump_only=True)
    status = fields.Str(dump_only=True)
    
    customer_id = fields.Int(required=True)
    customer = fields.Nested(PartySchema(only=["id", "name", "vat_number"]), dump_only=True) # Join semantica
    
    lines = fields.List(fields.Nested(SalesOrderLineSchema))
    total_amount = fields.Float(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

    @post_load
    def make_objects(self, data, **kwargs):
        """Converte i dizionari delle righe in oggetti SalesOrderLine prima del salvataggio"""
        if 'lines' in data:
            data['lines'] = [SalesOrderLine(**line) for line in data['lines']]
        return data