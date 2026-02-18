# ERPaaS - Specifiche Modulo Sales (Vendite)

## Documento #07 - Modulo Vendite e Ordini

---

## 1. Panoramica Modulo

### 1.1 Descrizione

Il modulo **Sales** gestisce l'intero ciclo vendita:
- Preventivi/Offerte
- Ordini cliente
- Vendite
- Resi

### 1.2 Flusso

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ Preventivo│───►│  Ordine  │───►│Consegna  │───►│Fattura  │
│ (Quote)  │    │ (Order)  │    │(Delivery)│    │(Invoice) │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
     │               │               │               │
  [30gg]        [conferma]      [spedito]       [pagato]
```

### 1.3 Entità

| Entità | Descrizione |
|--------|-------------|
| **SalesQuote** | Preventivo/Offerte |
| **SalesQuoteLine** | Righe preventivi |
| **SalesOrder** | Ordine cliente |
| **SalesOrderLine** | Righe ordine |
| **SalesDelivery** | Consegna/bolla |
| **SalesDeliveryLine** | Righe consegna |
| **SalesChannel** | Canale vendita |
| **SalesRule** | Regole business |

---

## 2. Modelli Database

### 2.1 SalesQuote (Preventivo)

```python
class SalesQuote(BaseModel):
    """Preventivo/Offerto."""
    __tablename__ = 'sales_quotes'
    
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
    # Identificazione
    quote_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    
    # Partner
    party_id = db.Column(db.Integer, db.ForeignKey('parties.id'), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey('party_contacts.id'))
    address_id = db.Column(db.Integer, db.ForeignKey('party_addresses.id'))
    
    # Date
    quote_date = db.Column(db.Date, nullable=False, default=datetime.date.today)
    valid_until = db.Column(db.Date)
    
    # Commerciale
    sales_channel_id = db.Column(db.Integer, db.ForeignKey('sales_channels.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # Commerciale
    
    # Totali
    subtotal = db.Column(db.Float, default=0)
    discount_amount = db.Column(db.Float, default=0)
    discount_percent = db.Column(db.Float, default=0)
    tax_amount = db.Column(db.Float, default=0)
    total = db.Column(db.Float, default=0)
    
    # Pagamento
    payment_term_id = db.Column(db.Integer, db.ForeignKey('payment_terms.id'))
    price_list_id = db.Column(db.Integer, db.ForeignKey('price_lists.id'))
    
    # Note
    note = db.Column(db.Text)
    terms = db.Column(db.Text)  # Condizioni generali
    
    # Stato
    state = db.Column(
        db.String(20), 
        default='draft',
        index=True
    )  # draft, sent, accepted, refused, expired, converted
    
    # Relazioni
    party = db.relationship('Party', backref='sales_quotes')
    contact = db.relationship('PartyContact')
    address = db.relationship('PartyAddress')
    lines = db.relationship('SalesQuoteLine', back_populates='quote', cascade='all, delete-orphan')
    user = db.relationship('User')
    channel = db.relationship('SalesChannel')
```

### 2.2 SalesQuoteLine (Riga Preventivo)

```python
class SalesQuoteLine(BaseModel):
    """Riga di preventivi."""
    __tablename__ = 'sales_quote_lines'
    
    quote_id = db.Column(db.Integer, db.ForeignKey('sales_quotes.id'), nullable=False)
    
    # Prodotto
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    product_name = db.Column(db.String(200))  # Denominazione se non collegato
    
    # Variante
    variant_id = db.Column(db.Integer, db.ForeignKey('product_variants.id'))
    
    # Quantità
    quantity = db.Column(db.Float, nullable=False, default=1)
    unit_of_measure = db.Column(db.String(10), default='pc')
    
    # Prezzo
    unit_price = db.Column(db.Float, nullable=False, default=0)
    discount_percent = db.Column(db.Float, default=0)
    discount_amount = db.Column(db.Float, default=0)
    
    # IVA
    tax_percent = db.Column(db.Float, default=22)
    
    # Calcolati
    subtotal = db.Column(db.Float, default=0)
    tax_amount = db.Column(db.Float, default=0)
    total = db.Column(db.Float, default=0)
    
    # Descrizione
    description = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    # Ordinamento
    sequence = db.Column(db.Integer, default=0)
    
    quote = db.relationship('SalesQuote', back_populates='lines')
    product = db.relationship('Product')
    variant = db.relationship('ProductVariant')
    
    def calculate(self):
        """Calcola totali riga."""
        # Calcolo sconto
        subtotal = self.quantity * self.unit_price
        if self.discount_percent > 0:
            self.discount_amount = subtotal * (self.discount_percent / 100)
        subtotal -= self.discount_amount
        
        # Calcolo IVA
        self.subtotal = subtotal
        self.tax_amount = subtotal * (self.tax_percent / 100)
        self.total = subtotal + self.tax_amount
        
        return self
```

### 2.3 SalesOrder (Ordine)

```python
class SalesOrder(BaseModel):
    """Ordine cliente."""
    __tablename__ = 'sales_orders'
    
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
    # Identificazione
    order_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    
    # Preventivo origine (se da preventivo)
    quote_id = db.Column(db.Integer, db.ForeignKey('sales_quotes.id'))
    
    # Partner
    party_id = db.Column(db.Integer, db.ForeignKey('parties.id'), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey('party_contacts.id'))
    address_id = db.Column(db.Integer, db.ForeignKey('party_addresses.id'))
    shipping_address_id = db.Column(db.Integer, db.ForeignKey('party_addresses.id'))
    
    # Date
    order_date = db.Column(db.Date, nullable=False, default=datetime.date.today)
    expected_date = db.Column(db.Date)  # Data prevista consegna
    
    # Commerciale
    sales_channel_id = db.Column(db.ForeignKey('sales_channels.id'))
    user_id = db.Column(db.ForeignKey('users.id'))
    
    # Totali
    subtotal = db.Column(db.Float, default=0)
    discount_amount = db.Column(db.Float, default=0)
    discount_percent = db.Column(db.Float, default=0)
    tax_amount = db.Column(db.Float, default=0)
    total = db.Column(db.Float, default=0)
    amount_paid = db.Column(db.Float, default=0)
    
    # Pagamento
    payment_term_id = db.Column(db.Integer, db.ForeignKey('payment_terms.id'))
    price_list_id = db.Column(db.Integer, db.ForeignKey('price_lists.id'))
    payment_method = db.Column(db.String(50))
    
    # Spedizione
    shipping_method = db.Column(db.String(50))
    shipping_cost = db.Column(db.Float, default=0)
    tracking_number = db.Column(db.String(100))
    
    # Note
    note = db.Column(db.Text)
    internal_note = db.Column(db.Text)
    
    # Stato
    state = db.Column(
        db.String(20), 
        default='draft',
        index=True
    )  # draft, confirmed, processing, shipped, delivered, cancelled, returned
    
    # Relazioni
    party = db.relationship('Party', backref='sales_orders')
    quote = db.relationship('SalesQuote', backref='converted_order')
    lines = db.relationship('SalesOrderLine', back_populates='order', cascade='all, delete-orphan')
    deliveries = db.relationship('SalesDelivery', back_populates='order')
    invoices = db.relationship('Invoice', back_populates='sales_order')
```

### 2.4 SalesOrderLine

```python
class SalesOrderLine(BaseModel):
    """Riga ordine."""
    __tablename__ = 'sales_order_lines'
    
    order_id = db.Column(db.Integer, db.ForeignKey('sales_orders.id'), nullable=False)
    
    # Prodotto
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    product_name = db.Column(db.String(200))
    variant_id = db.Column(db.Integer, db.ForeignKey('product_variants.id'))
    
    # Quantità
    quantity = db.Column(db.Float, nullable=False, default=1)
    unit_of_measure = db.Column(db.String(10), default='pc')
    
    # Prezzo
    unit_price = db.Column(db.Float, nullable=False, default=0)
    discount_percent = db.Column(db.Float, default=0)
    discount_amount = db.Column(db.Float, default=0)
    
    # IVA
    tax_percent = db.Column(db.Float, default=22)
    
    # Calcolati
    subtotal = db.Column(db.Float, default=0)
    tax_amount = db.Column(db.Float, default=0)
    total = db.Column(db.Float, default=0)
    
    # Spedizione
    quantity_delivered = db.Column(db.Float, default=0)
    quantity_shipped = db.Column(db.Float, default=0)
    
    # Descrizione
    description = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    sequence = db.Column(db.Integer, default=0)
    
    order = db.relationship('SalesOrder', back_populates='lines')
    product = db.relationship('Product')
    variant = db.relationship('ProductVariant')
    
    def calculate(self):
        """Calcola totali riga."""
        subtotal = self.quantity * self.unit_price
        if self.discount_percent > 0:
            self.discount_amount = subtotal * (self.discount_percent / 100)
        subtotal -= self.discount_amount
        
        self.subtotal = subtotal
        self.tax_amount = subtotal * (self.tax_percent / 100)
        self.total = subtotal + self.tax_amount
        
        return self
```

### 2.5 SalesDelivery (Consegna)

```python
class SalesDelivery(BaseModel):
    """Bolla di consegna."""
    __tablename__ = 'sales_deliveries'
    
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
    delivery_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    order_id = db.Column(db.Integer, db.ForeignKey('sales_orders.id'), nullable=False)
    
    delivery_date = db.Column(db.Date, nullable=False, default=datetime.date.today)
    
    # Indirizzo
    party_id = db.Column(db.Integer, db.ForeignKey('parties.id'), nullable=False)
    address_id = db.Column(db.Integer, db.ForeignKey('party_addresses.id'))
    
    # Note
    note = db.Column(db.Text)
    carrier = db.Column(db.String(100))
    tracking_number = db.Column(db.String(100))
    
    state = db.Column(db.String(20), default='draft')  # draft, confirmed, shipped
    
    party = db.relationship('Party', backref='sales_deliveries')
    order = db.relationship('SalesOrder', back_populates='deliveries')
    lines = db.relationship('SalesDeliveryLine', back_populates='delivery', cascade='all, delete-orphan')
```

### 2.6 PaymentTerm

```python
class PaymentTerm(BaseModel):
    """Termini di pagamento."""
    __tablename__ = 'payment_terms'
    
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20))
    
    # Definizione
    days = db.Column(db.Integer, default=0)  # Giorni dalla data documento
    day_of_month = db.Column(db.Integer)  # O il giorno del mese
    immediate = db.Column(db.Boolean, default=False)  # Contanti/subito
    
    # Rate (per pagamenti rateali)
    payment_mode = db.Column(db.String(20))  # immediate, end_of_month, specific_days
    installments = db.Column(db.Integer, default=1)  # Numero rate
    
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    
    tenant = db.relationship('Tenant')
    
    def get_due_date(self, base_date):
        """Calcola data scadenza."""
        if self.immediate:
            return base_date
        
        if self.day_of_month:
            # Pagamento il giorno X del mese
            from datetime import timedelta
            due = base_date.replace(day=self.day_of_month)
            if due < base_date:
                due = due + timedelta(days=30)
            return due
        
        return base_date + timedelta(days=self.days)
```

---

## 3. API Endpoints

### 3.1 Quotes (Preventivi)

| Method | Endpoint | Descrizione |
|--------|----------|-------------|
| GET | `/api/v1/sales/quotes` | Lista preventivi |
| POST | `/api/v1/sales/quotes` | Crea preventivo |
| GET | `/api/v1/sales/quotes/{id}` | Dettaglio |
| PUT | `/api/v1/sales/quotes/{id}` | Aggiorna |
| DELETE | `/api/v1/sales/quotes/{id}` | Elimina |
| POST | `/api/v1/sales/quotes/{id}/send` | Invia al cliente |
| POST | `/api/v1/sales/quotes/{id}/accept` | Accetta |
| POST | `/api/v1/sales/quotes/{id}/convert` | Converti in ordine |
| POST | `/api/v1/sales/quotes/{id}/pdf` | Genera PDF |

### 3.2 Orders (Ordini)

| Method | Endpoint | Descrizione |
|--------|----------|-------------|
| GET | `/api/v1/sales/orders` | Lista ordini |
| POST | `/api/v1/sales/orders` | Crea ordine |
| GET | `/api/v1/sales/orders/{id}` | Dettaglio |
| PUT | `/api/v1/sales/orders/{id}` | Aggiorna |
| POST | `/api/v1/sales/orders/{id}/confirm` | Conferma |
| POST | `/api/v1/sales/orders/{id}/ship` | Spedisci |
| POST | `/api/v1/sales/orders/{id}/deliver` | Consegna |
| POST | `/api/v1/sales/orders/{id}/cancel` | Annulla |
| POST | `/api/v1/sales/orders/{id}/invoice` | Fattura |

### 3.3 Deliveries (Consegne)

| Method | Endpoint | Descrizione |
|--------|----------|-------------|
| GET | `/api/v1/sales/deliveries` | Lista consegne |
| POST | `/api/v1/sales/deliveries` | Crea consegna |
| GET | `/api/v1/sales/deliveries/{id}/pdf` | PDF bolla |

---

## 4. Calcoli Automatici

### 4.1 Totali Ordine

```python
def calculate_order_totals(order):
    """Calcola tutti i totali dell'ordine."""
    
    # Somma righe
    subtotal = sum(line.total for line in order.lines)
    
    # Sconto globale
    if order.discount_percent > 0:
        order.discount_amount = subtotal * (order.discount_percent / 100)
    
    subtotal_after_discount = subtotal - order.discount_amount
    
    # Spese spedizione
    subtotal_with_shipping = subtotal_after_discount + order.shipping_cost
    
    # IVA
    order.subtotal = subtotal
    order.tax_amount = subtotal_after_discount * 0.22  # Calcolo IVA
    order.total = subtotal_with_shipping + order.tax_amount
    
    return order
```

### 4.2 Validazione

```
□ Quantità > 0
□ Prodotto attivo
□ Prezzo > 0 (se non zero)
□ Totale righe = totale documento
□ Indirizzo spedizione presente (se presente)
```

---

## 5. Dipendenze

| Modulo | Dipendenza |
|--------|------------|
| Core | Obbligatorio |
| Parties | Obbligatorio |
| Products | Obbligatorio |
| Accounting | Opzionale (per fatturazione) |
| Inventory | Opzionale (per gestione stock) |

---

## 6. Flussi Operativi

### 6.1 Da Preventivo a Ordine

```
1. Cliente richiede preventivo
2. Commerciale crea preventivo
3. Invia PDF al cliente
4. Cliente accetta
5. Sistema converte in ordine
6. Ordine confermato → decrementa magazzino
```

### 6.2 Gestione Resi

```
1. Cliente richiede reso
2. Crea reso da ordine
2. Ricezione merce
3. Verifica condizioni
4. Rimborso / Credito
```

---

## 7. Stima Sviluppo

| Componente | Tempo |
|------------|-------|
| Modelli DB | 4h |
| API CRUD Quotes | 4h |
| API CRUD Orders | 5h |
| API Deliveries | 3h |
| Calcoli totali | 2h |
| PDF Generation | 3h |
| Conversioni | 2h |
| Testing | 4h |
| **Totale** | **~27h** |

---

## 8. Schema Flusso

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   QUOTE     │────►│   ORDER     │────►│  DELIVERY  │
├─────────────┤     ├─────────────┤     ├─────────────┤
│ draft       │     │ draft       │     │ draft       │
│ sent        │     │ confirmed   │     │ confirmed   │
│ accepted    │────►│ processing  │────►│ shipped     │
│ refused     │     │ shipped     │     │ delivered   │
│ expired     │     │ delivered   │     │             │
│ converted   │     │ cancelled   │     │             │
└─────────────┘     │ returned    │     └─────────────┘
                    └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  INVOICE    │
                    ├─────────────┤
                    │ draft       │
                    │ validated   │
                    │ sent        │
                    │ paid        │
                    │ cancelled   │
                    └─────────────┘
```

---

*Documento generato il 18 Febbraio 2026*
*Progetto: FlaskERP ERPaaS Platform*
*Documento #07 - Modulo Sales*
