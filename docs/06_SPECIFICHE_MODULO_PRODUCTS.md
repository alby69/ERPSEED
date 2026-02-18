# ERPaaS - Specifiche Modulo Products (Prodotti)

## Documento #06 - Modulo Prodotti e Servizi

---

## 1. Panoramica Modulo

### 1.1 Descrizione

Il modulo **Products** gestisce il catalogo prodotti e servizi:
- Prodotti finiti
- Servizi
- Materie prime
- Kit/Bundle

### 1.2 Entità

| Entità | Descrizione |
|--------|-------------|
| **Product** | Prodotto/Servizio principale |
| **ProductCategory** | Categorie gerarchiche |
| **ProductImage** | Immagini prodotto |
| **ProductPrice** | Listini multipli |
| **ProductVariant** | Varianti (taglia, colore) |
| **ProductSupplier** | Fornitori per prodotto |

---

## 2. Modelli Database

### 2.1 Product

```python
class Product(BaseModel):
    """Prodotto o servizio."""
    __tablename__ = 'products'
    
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
    # Identificazione
    name = db.Column(db.String(150), nullable=False, index=True)
    code = db.Column(db.String(50), unique=True, index=True)  # Codice articolo
    barcode = db.Column(db.String(50), index=True)  # Codice a barre
    ean = db.Column(db.String(13))  # EAN13
    
    # Tipo
    product_type = db.Column(
        db.String(20), 
        nullable=False, 
        default='goods'
    )  # goods, service, kit
    
    # Descrizione
    description = db.Column(db.Text)
    description_short = db.Column(db.String(255))
    
    # Categoria
    category_id = db.Column(db.Integer, db.ForeignKey('product_categories.id'))
    
    # Unità di misura
    unit_of_measure = db.Column(db.String(10), default='pc')  # pz, kg, lt, mt
    unit_of_measure_precision = db.Column(db.Integer, default=0)
    
    # Prezzo
    list_price = db.Column(db.Float, default=0)  # Prezzo di listino
    cost_price = db.Column(db.Float, default=0)  # Costo acquisto
    
    # IVA
    tax_category_id = db.Column(db.Integer, db.ForeignKey('tax_categories.id'))
    
    # Inventario
    track_inventory = db.Column(db.Boolean, default=False)
    min_stock = db.Column(db.Float, default=0)
    max_stock = db.Column(db.Float, default=0)
    
    # Peso e dimensioni
    weight = db.Column(db.Float)  # kg
    weight_uom = db.Column(db.String(10))
    dimensions = db.Column(db.String(50))  # LxHxP
    
    # Stato
    is_active = db.Column(db.Boolean, default=True)
    is_sellable = db.Column(db.Boolean, default=True)
    is_purchasable = db.Column(db.Boolean, default=True)
    
    # Immagini
    image_url = db.Column(db.String(500))
    
    # Relazioni
    category = db.relationship('ProductCategory', back_populates='products')
    images = db.relationship('ProductImage', back_populates='product', cascade='all, delete-orphan')
    variants = db.relationship('ProductVariant', back_populates='product', cascade='all, delete-orphan')
    prices = db.relationship('ProductPrice', back_populates='product', cascade='all, delete-orphan')
    suppliers = db.relationship('ProductSupplier', back_populates='product', cascade='all, delete-orphan')
    
    __table_args__ = (
        db.Index('ix_product_tenant_code', 'tenant_id', 'code'),
        db.Index('ix_product_tenant_name', 'tenant_id', 'name'),
    )
```

### 2.2 ProductCategory

```python
class ProductCategory(BaseModel):
    """Categoria prodotti gerarchica."""
    __tablename__ = 'product_categories'
    
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    code = db.Column(db.String(20))
    
    # Gerarchia
    parent_id = db.Column(db.Integer, db.ForeignKey('product_categories.id'))
    level = db.Column(db.Integer, default=0)
    
    # Layout
    image_url = db.Column(db.String(500))
    color = db.Column(db.String(7))
    
    # Stato
    is_active = db.Column(db.Boolean, default=True)
    sequence = db.Column(db.Integer, default=0)
    
    # Relazioni
    parent = db.relationship('ProductCategory', remote_side=[id], backref='children')
    products = db.relationship('Product', back_populates='category')
    
    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'name', name='uix_tenant_category_name'),
    )
```

### 2.3 ProductVariant

```python
class ProductVariant(BaseModel):
    """Variante prodotto (taglia, colore)."""
    __tablename__ = 'product_variants'
    
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    name = db.Column(db.String(100), nullable=False)  # "Taglia: M, Colore: Rosso"
    code = db.Column(db.String(50))  # Codice variante
    
    # Attributi
    attributes = db.Column(db.Text)  # JSON: {"size": "M", "color": "Red"}
    
    # Prezzo e costo specifico
    list_price = db.Column(db.Float)
    cost_price = db.Column(db.Float)
    
    # Inventario
    sku = db.Column(db.String(50), index=True)
    barcode = db.Column(db.String(50))
    
    # Immagine
    image_url = db.Column(db.String(500))
    
    is_active = db.Column(db.Boolean, default=True)
    
    product = db.relationship('Product', back_populates='variants')
    
    __table_args__ = (
        db.UniqueConstraint('product_id', 'code', name='uix_product_variant_code'),
    )
```

### 2.4 ProductPrice

```python
class ProductPrice(unittest):
    """Listino prezzi multipli."""
    __tablename__ = 'product_prices'
    
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    variant_id = db.Column(db.Integer, db.ForeignKey('product_variants.id'))
    
    # Listino
    price_list_id = db.Column(db.Integer, db.ForeignKey('price_lists.id'))
    
    # Prezzo
    price = db.Column(db.Float, nullable=False)
    min_quantity = db.Column(db.Float, default=1)  # Prezzo per quantità
    
    # Validità
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    
    product = db.relationship('Product', back_populates='prices')
    price_list = db.relationship('PriceList')
    variant = db.relationship('ProductVariant')
    
    tenant = db.relationship('Tenant')
    
    __table_args__ = (
        db.UniqueConstraint(
            'tenant_id', 'product_id', 'price_list_id', 'min_quantity',
            name='uix_tenant_product_price_list'
        ),
    )
```

### 2.5 PriceList

```python
class PriceList(BaseModel):
    """Listino prezzi (es. "Listino 2026", "Vendita al pubblico")."""
    __tablename__ = 'price_lists'
    
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20))
    description = db.Column(db.Text)
    
    # Calcolo
    currency = db.Column(db.String(3), default='EUR')
    discount_policy = db.Column(db.String(20))  # fixed, percentage
    
    # Validità
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    
    is_default = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    
    tenant = db.relationship('Tenant')
    
    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'name', name='uix_tenant_price_list_name'),
    )
```

---

## 3. API Endpoints

### 3.1 Product CRUD

| Method | Endpoint | Descrizione |
|--------|----------|-------------|
| GET | `/api/v1/products` | Lista prodotti |
| POST | `/api/v1/products` | Crea prodotto |
| GET | `/api/v1/products/{id}` | Dettaglio prodotto |
| PUT | `/api/v1/products/{id}` | Aggiorna prodotto |
| DELETE | `/api/v1/products/{id}` | Elimina prodotto |
| POST | `/api/v1/products/{id}/images` | Carica immagine |
| GET | `/api/v1/products/{id}/prices` | Lista prezzi |
| POST | `/api/v1/products/{id}/prices` | Aggiungi prezzo |

### 3.2 Categorie

| Method | Endpoint | Descrizione |
|--------|----------|-------------|
| GET | `/api/v1/product-categories` | Lista categorie (albero) |
| POST | `/api/v1/product-categories` | Crea categoria |
| PUT | `/api/v1/product-categories/{id}` | Aggiorna categoria |
| DELETE | `/api/v1/product-categories/{id}` | Elimina categoria |

### 3.3 Listini

| Method | Endpoint | Descrizione |
|--------|----------|-------------|
| GET | `/api/v1/price-lists` | Lista listini |
| GET | `/api/v1/price-lists/{id}/products` | Prodotti del listino |

---

## 4. Funzionalità Business

### 4.1 Ricerca e Filtri

```python
# Query parameters
?search=telefono           # Ricerca nome/codice/barcode
?category_id=5             # Filtro categoria
?product_type=goods        # Filtro tipo
?is_sellable=true          # Solo vendibili
?is_active=true            # Solo attivi
?price_min=10&price_max=50 # Filtro prezzo
?has_stock=true            # Solo con giacenza
?page=1&per_page=20
```

### 4.2 Calcolo Prezzo

```
Prezzo finale = 
  (list_price * (1 - sconto_percentuale/100)) 
  + (IVA %)
```

### 4.3 Codici a Barre

Supporto formati:
- EAN-13
- EAN-8
- UPC-A
- Code 128
- QR Code

---

## 5. Dipendenze

| Modulo | Dipendenza |
|--------|------------|
| Core | Obbligatorio |
| Inventory | Richiede per tracking stock |
| Sales | Richiede per ordini |
| Purchases | Richiede per acquisti |
| POS | Richiede per punto vendita |

---

## 6. Stima Sviluppo

| Componente | Tempo |
|------------|-------|
| Modelli DB | 3h |
| Migration | 1h |
| API CRUD | 6h |
| Categorie gerarchiche | 2h |
| Listini multipli | 3h |
| Varianti | 3h |
| Barcode | 2h |
| Testing | 3h |
| **Totale** | **~23h** |

---

## 7. Schema ER

```
┌─────────────────┐       ┌──────────────────────┐
│ ProductCategory │       │     Product          │
├─────────────────┤       ├──────────────────────┤
│ id              │◄──┐   │ id                   │
│ name            │   │   │ name                 │
│ parent_id ──────┼───┘   │ code                 │
│ level           │       │ category_id ──────┐  │
└─────────────────┘       │ list_price         │  │
                          └─────────┬──────────┘  │
                                    │            │
                          ┌─────────▼──────────┐  │
                          │  ProductVariant    │  │
                          ├────────────────────┤  │
                          │ id                 │  │
                          │ product_id ────────┘  │
                          │ attributes (JSON)     │
                          │ list_price           │
                          └──────────────────────┘
```

---

*Documento generato il 18 Febbraio 2026*
*Progetto: FlaskERP ERPaaS Platform*
*Documento #06 - Modulo Products*
