# FlaskERP - Future Improvements & TODO

## ✅ Completati - Febbraio 2026

### 🧩 Sistema Component Builder + Marketplace (Febbraio 2026)
**Stato**: Implementato.
- ✅ Modelli Backend: Archetype, Component, Block, BlockRelationship
- ✅ Modelli Marketplace: Category, BlockListing, Review, PaymentTransaction, Author
- ✅ API REST complete per Builder e Marketplace
- ✅ Frontend: ArchetypeRegistry, ComponentRenderer, Archetypes (Table, Form, Chart, Kanban, Metric, Grid)
- ✅ Pagine: BlockBuilder, MarketplaceBrowse
- ✅ Sistema Navigazione configurabile da JSON
- ✅ Inizializzazione automatica system archetypes e categorie marketplace

### 🎨 Sistema di Navigazione Unificato (Febbraio 2026)
**Stato**: Implementato.
- Creato componente `AppHeader.jsx` con:
  - Logo FlaskERP con link alla home
  - Breadcrumb dinamico basato su URL
  - Pulsante "Torna indietro" intelligente
  - Dropdown cambio tema (7 colori: chiaro, scuro, blu, verde, viola, rosso, arancione)
  - Selezione lingua
  - Menu utente (Profilo, Impostazioni, Logout)
- Rimosso duplicato "Select Project" dalla sidebar

### 🔍 Ricerca e Ordinamento Tabelle (Febbraio 2026)
**Stato**: Implementato.

### 🎨 Temi e Personalizzazione
**Stato**: Implementato via Ant Design ConfigProvider.

### 🧪 Sistema di Testing Ibrido
**Stato**: Implementato.

### 📊 BI Builder Avanzato (Febbraio 2026)
**Stato**: Implementato.
- ✅ Drag & drop in griglia con `react-grid-layout`
- ✅ Motore filtri dinamici UI
- ✅ Export grafici PDF/PNG
- ✅ Layout salvato nel database

---

# 🚀 ARCHITETTURA COMPLETA: ERP BUILDER + MARKETPLACE

## Visione Sistema

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FLASKERP ECOSYSTEM                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────┐    ┌─────────────────────────────────────────┐ │
│  │   ADMIN / POWER USER    │    │            MARKETPLACE                 │ │
│  │                         │    │                                         │ │
│  │  ┌───────────────────┐  │    │  ┌─────────────────────────────────┐  │ │
│  │  │   ERP BUILDER     │  │    │  │   BLOCK STORE                   │  │ │
│  │  │                   │  │    │  │                                 │  │ │
│  │  │  - Project Setup  │  │    │  │  - Browse Blocks                 │  │ │
│  │  │  - Schema Designer│  │    │  │  - Search (category, author)    │  │ │
│  │  │  - Relationships  │  │    │  │  - Ratings & Reviews             │  │ │
│  │  │  - Business Logic │  │    │  │  - Free / Paid (Payment)        │  │ │
│  │  │  - Permissions    │  │    │  │  - Install / Publish             │  │ │
│  │  │  - Report Designer│  │    │  │  - Certification (Testing)      │  │ │
│  │  └───────────────────┘  │    │  └─────────────────────────────────┘  │ │
│  │                         │    │                                         │ │
│  │  ┌───────────────────┐  │    │  ┌─────────────────────────────────┐  │ │
│  │  │   BLOCK BUILDER   │  │    │  │   BLOCK TESTING ENGINE         │  │ │
│  │  │                   │  │    │  │                                 │  │ │
│  │  │  - Components     │  │    │  │  - Automated Tests              │  │ │
│  │  │  - Collections    │  │    │  │  - Validation                   │  │ │
│  │  │  - Block (API)    │  │    │  │  - Quality Score                 │  │ │
│  │  │  - Workflows      │  │    │  │  - Certification                │  │ │
│  │  └───────────────────┘  │    │  └─────────────────────────────────┘  │ │
│  └─────────────────────────┘    └─────────────────────────────────────────┘ │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                     END USER (COMPANY)                                │   │
│  │                                                                       │   │
│  │  - Login multi-tenant                                                 │   │
│  │  - Use configured ERP (dashboards, forms, reports)                  │   │
│  │  - Manage company users & roles                                       │   │
│  └──────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## CORE CONCEPTS (English)

| Term | Definition |
|------|------------|
| **Component** | Atomic reusable piece (Table, Chart, Form, Metric) |
| **Block** | Aggregated collection of Components with business logic and connections |
| **Collection** | Grouping mechanism for Components within a Block |
| **Archetype** | Base template defining Component behavior and API |
| **Blueprint** | Technical definition (like current SysModel/SysField) |

---

## Backend: Nuovi Modelli

### Phase 1: Builder Foundation Models

```python
# backend/builder/models.py

class Archetype(BaseModel):
    """Component template - base for all components"""
    name = db.Column(db.String(80), unique=True, nullable=False)
    component_type = db.Column(db.String(50))  # 'table', 'form', 'chart', 'kanban', 'metric'
    description = db.Column(db.String(255))
    default_config = db.Column(db.JSON)  # Default configuration
    api_schema = db.Column(db.JSON)  # CRUD operations definition
    is_system = db.Column(db.Boolean, default=False)  # System archetypes (non-deletable)
    icon = db.Column(db.String(50))
    
    # Componenti figli di sistema
    children = db.relationship("Archetype", backref="parent", remote_side=[id])

class Component(BaseModel):
    """Component instance in a project"""
    project_id = db.Column(db.Integer, ForeignKey('projects.id'), nullable=False)
    archetype_id = db.Column(db.Integer, ForeignKey('archetypes.id'), nullable=False)
    
    name = db.Column(db.String(120))
    config = db.Column(db.JSON)  # Instance configuration (column order, filters, etc.)
    
    # Layout positioning (for grid-based views)
    position_x = db.Column(db.Integer, default=0)
    position_y = db.Column(db.Integer, default=0)
    width = db.Column(db.Integer, default=6)
    height = db.Column(db.Integer, default=4)
    order_index = db.Column(db.Integer, default=0)
    
    # Hierarchy
    parent_id = db.Column(db.Integer, ForeignKey('components.id'), nullable=True)
    block_id = db.Column(db.Integer, ForeignKey('blocks.id'), nullable=True)
    
    archetype = db.relationship("Archetype")
    parent = db.relationship("Component", remote_side=[id], backref="children")

class Block(BaseModel):
    """Aggregated Block - collection of components with logic"""
    project_id = db.Column(db.Integer, ForeignKey('projects.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    
    component_ids = db.Column(db.JSON)  # Ordered list of component IDs
    relationships = db.Column(db.JSON)  # Component connections (data flow)
    api_endpoints = db  # Custom API.Column(db.JSON) definitions
    
    version = db.Column(db.String(20), default='1.0.0')
    
    # Testing & Quality
    test_suite_id = db.Column(db.Integer, ForeignKey('test_suites.id'))
    quality_score = db.Column(db.Integer, default=0)
    is_certified = db.Column(db.Boolean, default=False)
    certification_date = db.Column(db.DateTime)
    
    # Status
    status = db.Column(db.String(20))  # 'draft', 'testing', 'published'

class BlockRelationship(BaseModel):
    """Connections between components in a Block"""
    block_id = db.Column(db.Integer, ForeignKey('blocks.id'), nullable=False)
    source_component_id = db.Column(db.Integer, ForeignKey('components.id'))
    target_component_id = db.Column(db.Integer, ForeignKey('components.id'))
    relationship_type = db.Column(db.String(50))  # 'data_flow', 'filter', 'reference'
    config = db.Column(db.JSON)  # Relationship configuration
```

### Phase 2: Marketplace Models

```python
# backend/marketplace/models.py

class Category(BaseModel):
    """Block categories"""
    name = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(80), unique=True)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))
    parent_id = db.Column(db.Integer, ForeignKey('categories.id'))
    order_index = db.Column(db.Integer, default=0)

class BlockListing(BaseModel):
    """Published block in marketplace"""
    block_id = db.Column(db.Integer, ForeignKey('blocks.id'), nullable=False)
    author_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    
    title = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(120), unique=True)
    description = db.Column(db.Text)
    long_description = db.Column(db.Text)  # Markdown supported
    category_id = db.Column(db.Integer, ForeignKey('categories.id'))
    
    # Business
    price = db.Column(db.Numeric(10, 2), default=0)  # 0 = free
    currency = db.Column(db.String(3), default='EUR')
    
    # Media
    thumbnail_url = db.Column(db.String(255))
    screenshots = db.Column(db.JSON)  # Array of image URLs
    demo_url = db.Column(db.String(255))  # Live demo link
    
    # Stats
    downloads = db.Column(db.Integer, default=0)
    rating_sum = db.Column(db.Integer, default=0)
    rating_count = db.Column(db.Integer, default=0)
    
    @property
    def rating_avg(self):
        return self.rating_sum / self.rating_count if self.rating_count > 0 else 0
    
    # Status (Hybrid: internal + external with approval)
    status = db.Column(db.String(20))  # 'draft', 'pending_review', 'published', 'rejected'
    rejection_reason = db.Column(db.Text)
    
    # Versioning
    current_version = db.Column(db.String(20))
    changelog = db.Column(db.Text)
    
    author = db.relationship("User")
    category = db.relationship("Category")

class Review(BaseModel):
    """Block ratings and reviews"""
    listing_id = db.Column(db.Integer, ForeignKey('block_listings.id'), nullable=False)
    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer)  # 1-5
    comment = db.Column(db.Text)
    
    user = db.relationship("User")
    listing = db.relationship("BlockListing", backref="reviews")

class PaymentTransaction(BaseModel):
    """Payment processing for paid blocks"""
    listing_id = db.Column(db.Integer, ForeignKey('block_listings.id'), nullable=False)
    buyer_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='EUR')
    status = db.Column(db.String(20))  # 'pending', 'completed', 'failed', 'refunded'
    
    # Payment info
    payment_method = db.Column(db.String(50))  # 'stripe', 'paypal', etc.
    transaction_id = db.Column(db.String(255))  # External transaction ID
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    buyer = db.relationship("User", foreign_keys=[buyer_id])
    listing = db.relationship("BlockListing")
```

---

## Frontend: Struttura Componenti

### Directory Structure

```
frontend/src/
├── components/
│   ├── core/
│   │   ├── ArchetypeRegistry.js   # Component registration
│   │   ├── ComponentRenderer.js    # Dynamic renderer
│   │   ├── BlockRenderer.js       # Block display
│   │   └── index.js
│   │
│   ├── archetypes/                # Component implementations
│   │   ├── TableArchetype.jsx    # Drag & drop table
│   │   ├── FormArchetype.jsx
│   │   ├── ChartArchetype.jsx
│   │   ├── KanbanArchetype.jsx
│   │   ├── MetricArchetype.jsx
│   │   └── index.js
│   │
│   ├── ui/                        # Base UI elements
│   │   ├── Navigation/            # REUSABLE NAVIGATION SYSTEM
│   │   │   ├── AppSidebar.jsx
│   │   │   ├── AppHeader.jsx
│   │   │   ├── Breadcrumb.jsx
│   │   │   ├── MenuBuilder.jsx   # Dynamic menu from config
│   │   │   └── index.js
│   │   ├── DragDrop/
│   │   ├── Sortable/
│   │   └── Resizable/
│   │
│   └── marketplace/
│       ├── BlockCard.jsx
│       ├── BlockDetail.jsx
│       ├── CategoryBrowser.jsx
│       └── ReviewForm.jsx
│
├── pages/
│   ├── Builder/
│   │   ├── BlockBuilder.jsx
│   │   ├── ComponentEditor.jsx
│   │   └── SchemaDesigner.jsx
│   │
│   ├── Marketplace/
│   │   ├── Browse.jsx
│   │   ├── BlockDetail.jsx
│   │   ├── PublishWizard.jsx
│   │   └── MyBlocks.jsx
│   │
│   └── Testing/
│       └── TestRunner.jsx
│
├── hooks/
│   ├── useArchetype.js
│   ├── useBlock.js
│   ├── useCollection.js
│   ├── useMarketplace.js
│   └── useNavigation.js
│
└── services/
    ├── archetypeApi.js
    ├── blockApi.js
    ├── marketplaceApi.js
    └── paymentApi.js
```

---

## Navigation System (Priority 1)

### Concept

The Navigation System is a **reusable, configurable menu** that:
- Can be defined via JSON/API
- Supports nested menus
- Integrates with permissions
- Works across all pages
- Has consistent styling

### Interface

```javascript
// Navigation configuration (from API or local)
const navigationConfig = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: 'DashboardOutlined',
    path: '/dashboard',
    permission: null  // visible to all
  },
  {
    id: 'builder',
    label: 'Builder',
    icon: 'BuildOutlined',
    permission: 'admin',
    children: [
      { id: 'blocks', label: 'Blocks', path: '/builder/blocks' },
      { id: 'components', label: 'Components', path: '/builder/components' },
      { id: 'schema', label: 'Schema Designer', path: '/builder/schema' }
    ]
  },
  {
    id: 'marketplace',
    label: 'Marketplace',
    icon: 'ShopOutlined',
    children: [
      { id: 'browse', label: 'Browse', path: '/marketplace' },
      { id: 'publish', label: 'Publish Block', path: '/marketplace/publish' },
      { id: 'my-blocks', label: 'My Blocks', path: '/marketplace/my-blocks' }
    ]
  }
];
```

---

## API Specification

### Components API

```
GET    /api/archetypes                    # List system archetypes
GET    /api/archetypes/:id                # Get archetype details
GET    /api/archetypes/:id/schema         # Get component API schema

GET    /api/projects/:id/components       # List project components
POST   /api/projects/:id/components       # Create component
GET    /api/components/:id                # Get component
PUT    /api/components/:id                # Update component
DELETE /api/components/:id                # Delete component
PUT    /api/components/:id/position       # Update position (x,y,w,h)
PUT    /api/components/:id/order          # Update order index
GET    /api/components/:id/children       # Get child components
POST   /api/components/:id/children       # Add child component
```

### Blocks API

```
GET    /api/projects/:id/blocks           # List project blocks
POST   /api/projects/:id/blocks           # Create block
GET    /api/blocks/:id                   # Get block details
PUT    /api/blocks/:id                   # Update block
DELETE /api/blocks/:id                   # Delete block
GET    /api/blocks/:id/components        # Get block components
PUT    /api/blocks/:id/components        # Update block components
POST   /api/blocks/:id/test              # Run block tests
```

### Marketplace API

```
GET    /api/marketplace/blocks            # Browse blocks
GET    /api/marketplace/blocks/:id       # Block details
GET    /api/marketplace/search            # Search blocks
GET    /api/marketplace/categories        # List categories

POST   /api/marketplace/blocks/:id/reviews
GET    /api/marketplace/blocks/:id/reviews

POST   /api/marketplace/publish           # Submit block for review
POST   /api/marketplace/blocks/:id/install
POST   /api/marketplace/blocks/:id/uninstall

POST   /api/marketplace/payments         # Process payment
GET    /api/marketplace/payments/:id     # Get payment status
```

---

## Implementation Phases

### Phase 1: Navigation System ✅
- [x] Create reusable Navigation components
- [x] Create MenuBuilder from config
- [x] Integrate with AppSidebar
- [x] Add permission filtering

### Phase 2: Backend Foundation ✅
- [x] Create Archetype, Component, Block models
- [x] Create CRUD API
- [x] Create Block API

### Phase 3: Frontend Core ✅
- [x] Create ArchetypeRegistry
- [x] Create ComponentRenderer
- [x] Create BlockBuilder page

### Phase 4: Table Drag & Drop ✅
- [x] Implement TableArchetype with sortable columns
- [x] Add resize handles
- [x] Persist column order

### Phase 5: Marketplace ✅
- [x] Create Marketplace models
- [x] Create marketplace API
- [x] Create Browse pages
- [x] Add payment processing

### Phase 6: Testing Integration ⏳
- [ ] Connect TestRunner to Blocks
- [ ] Add quality scoring
- [ ] Add certification workflow

---

## 🐳 Docker Commands Reference

```bash
# Migrazioni Database
docker compose exec backend flask db migrate -m "description"
docker compose exec backend flask db upgrade

# Reset completo database
docker compose exec backend python -c "from backend.seed_initial import init_db; init_db()"

# Build
docker compose build
docker compose up -d
```

---

*Documento aggiornato: Febbraio 2026*
