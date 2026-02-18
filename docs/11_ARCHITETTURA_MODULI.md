# Architettura Moduli/Plugin in FlaskERP

## Ultimo aggiornamento: 18 Febbraio 2026

---

## 1. Panoramica

FlaskERP usa un'architettura plugin per estendere le funzionalità del core. Il sistema attuale fornisce una base solida, ma manca di:
- Configurazione per-tenant dei moduli attivi
- Sistema di moduli a pagamento (license/acquisto)
- Sincronizzazione frontend/backend
- Interfacce formali per integrazione sicura

---

## 2. Stato Attuale

### Struttura Plugin Esistente

```
backend/plugins/
├── base.py          # BasePlugin, PluginMixin
├── registry.py      # PluginRegistry (singleton)
├── __init__.py     # Esportazioni
├── accounting/
│   ├── plugin.py   # AccountingPlugin
│   ├── routes.py
│   └── models.py
├── inventory/
│   ├── plugin.py
│   ├── routes.py
│   └── models.py
└── hr/
    ├── plugin.py
    ├── routes.py
    └── models.py
```

### BasePlugin (backend/plugins/base.py)

```python
class BasePlugin(ABC):
    name: str = "base_plugin"
    version: str = "1.0.0"
    description: str = ""
    dependencies: List[str] = []
    
    @abstractmethod
    def register(self): ...
    
    @abstractmethod
    def init_db(self): ...
```

### PluginRegistry (backend/plugins/registry.py)

- `_plugin_classes`: Plugin registrati (non istanziati)
- `_plugins`: Plugin istanziati
- `_enabled_plugins`: Plugin attivi

---

## 3. Proposta: Architettura Moduli v2.0

### 3.1 Definizioni

- **Modulo**: Componente opzionale che estende FlaskERP
- **Core**: Funzionalità sempre disponibili (Parties, Products, Sales, Purchases, Users)
- **Tenant**: Istanza di ERP di un cliente

### 3.2 Categorie Moduli

| Categoria | Descrizione | Esempi |
|-----------|-------------|---------|
| `core` | Sempre disponibili | Parties, Products, Sales |
| `builtin` | Inclusi nel piano | Accounting, Inventory, HR |
| `premium` | A pagamento | Projects, CRM, Manufacturing |
| `third_party` | Esterni | Pagamenti, Shipping, Email |

### 3.3 Attributi Modulo

```python
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional

class ModuleCategory(str, Enum):
    CORE = "core"
    BUILTIN = "builtin"
    PREMIUM = "premium"
    THIRD_PARTY = "third_party"

@dataclass
class ModuleInfo:
    """Metadata di un modulo."""
    id: str                      # Identificatore univoco
    name: str                    # Nome visualizzato
    description: str             # Descrizione
    category: ModuleCategory     # Categoria
    version: str                 # Versione semver
    
    # Licensing
    is_free: bool = True         # Se gratuito
    price: Optional[float] = None # Prezzo (se premium)
    plan_required: str = "starter" # Piano minimo
    
    # Dipendenze
    dependencies: List[str] = [] # Moduli richiesti
    core_version_min: str = "1.0.0"
    
    # UI
    icon: str = "box"            # Icona
    menu_position: int = 100     # Posizione nel menu
    
    # Funzionalità
    has_api: bool = True
    has_ui: bool = True
    has_widget: bool = False
```

---

## 4. Implementazione Backend

### 4.1 Modello TenantModule

```python
# backend/core/models/tenant_module.py

class TenantModule(BaseModel):
    """
    Modulo attivo per un tenant.
    """
    __tablename__ = 'tenant_modules'
    
    tenant_id = db.Column(
        db.Integer, 
        db.ForeignKey('tenants.id'), 
        nullable=False,
        index=True
    )
    
    module_id = db.Column(
        db.String(50), 
        nullable=False,
        index=True
    )
    
    is_enabled = db.Column(db.Boolean, default=False)
    enabled_at = db.Column(db.DateTime)
    disabled_at = db.Column(db.DateTime)
    
    # Licensing
    license_key = db.Column(db.String(255))
    expires_at = db.Column(db.DateTime)
    
    # Configurazione specifica del tenant
    config = db.Column(db.JSON, default=dict)
    
    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'module_id', name='uix_tenant_module'),
    )
```

### 4.2 Modello ModuleDefinition

```python
# backend/core/models/module_definition.py

class ModuleDefinition(BaseModel):
    """
    Definizione di un modulo disponibile nel sistema.
    """
    __tablename__ = 'module_definitions'
    
    module_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    category = db.Column(db.String(20), nullable=False)  # core, builtin, premium
    version = db.Column(db.String(20), default="1.0.0")
    
    is_free = db.Column(db.Boolean, default=True)
    price = db.Column(db.Numeric(10, 2))
    plan_required = db.Column(db.String(50), default="starter")
    
    dependencies = db.Column(db.JSON, default=list)
    core_version_min = db.Column(db.String(20), default="1.0.0")
    
    icon = db.Column(db.String(50), default="box")
    menu_position = db.Column(db.Integer, default=100)
    
    is_active = db.Column(db.Boolean, default=True)  # Se disponibile nel sistema
```

### 4.3 Service Moduli

```python
# backend/core/services/module_service.py

from typing import List, Optional, Dict, Any
from datetime import datetime

class ModuleService:
    """Service per gestire moduli a livello di sistema."""
    
    @staticmethod
    def get_available_modules() -> List[ModuleDefinition]:
        """Restituisce tutti i moduli disponibili."""
        return ModuleDefinition.query.filter_by(is_active=True).all()
    
    @staticmethod
    def get_module_by_id(module_id: str) -> Optional[ModuleDefinition]:
        """Restituisce un modulo per ID."""
        return ModuleDefinition.query.filter_by(module_id=module_id, is_active=True).first()
    
    @staticmethod
    def register_module(info: ModuleInfo) -> ModuleDefinition:
        """Registra un nuovo modulo nel sistema."""
        module = ModuleDefinition(
            module_id=info.id,
            name=info.name,
            description=info.description,
            category=info.category.value,
            version=info.version,
            is_free=info.is_free,
            price=info.price,
            plan_required=info.plan_required,
            dependencies=info.dependencies,
            core_version_min=info.core_version_min,
            icon=info.icon,
            menu_position=info.menu_position,
        )
        db.session.add(module)
        db.session.commit()
        return module


class TenantModuleService:
    """Service per gestire moduli a livello di tenant."""
    
    @staticmethod
    def get_enabled_modules(tenant_id: int) -> List[TenantModule]:
        """Restituisce i moduli attivi per un tenant."""
        return TenantModule.query.filter_by(
            tenant_id=tenant_id, 
            is_enabled=True
        ).all()
    
    @staticmethod
    def is_module_enabled(tenant_id: int, module_id: str) -> bool:
        """Verifica se un modulo è attivo per un tenant."""
        tm = TenantModule.query.filter_by(
            tenant_id=tenant_id,
            module_id=module_id
        ).first()
        return tm and tm.is_enabled
    
    @staticmethod
    def enable_module(
        tenant_id: int, 
        module_id: str,
        license_key: str = None,
        config: dict = None
    ) -> TenantModule:
        """Attiva un modulo per un tenant."""
        # Verifica licensing
        module_def = ModuleService.get_module_by_id(module_id)
        if not module_def:
            raise ValueError(f"Modulo {module_id} non trovato")
        
        # Verifica piano
        tenant = Tenant.query.get(tenant_id)
        if not ModuleService.check_plan_compatibility(tenant.plan, module_def):
            raise ValueError(f"Piano {tenant.plan} non supporta questo modulo")
        
        # Verifica dipendenze
        for dep_id in module_def.dependencies:
            if not TenantModuleService.is_module_enabled(tenant_id, dep_id):
                raise ValueError(f"Modulo richiede {dep_id} attivo")
        
        # Crea o aggiorna
        tm = TenantModule.query.filter_by(
            tenant_id=tenant_id,
            module_id=module_id
        ).first()
        
        if tm:
            tm.is_enabled = True
            tm.enabled_at = datetime.utcnow()
        else:
            tm = TenantModule(
                tenant_id=tenant_id,
                module_id=module_id,
                is_enabled=True,
                enabled_at=datetime.utcnow(),
                license_key=license_key,
                config=config or {}
            )
            db.session.add(tm)
        
        db.session.commit()
        
        # Hook: notifica plugin system
        PluginRegistry.enable(module_id)
        
        return tm
    
    @staticmethod
    def disable_module(tenant_id: int, module_id: str) -> bool:
        """Disattiva un modulo per un tenant."""
        tm = TenantModule.query.filter_by(
            tenant_id=tenant_id,
            module_id=module_id
        ).first()
        
        if not tm or not tm.is_enabled:
            return False
        
        # Verifica che altri moduli non dipendano da questo
        enabled = TenantModuleService.get_enabled_modules(tenant_id)
        for enabled_mod in enabled:
            mod_def = ModuleService.get_module_by_id(enabled_mod.module_id)
            if mod_def and module_id in mod_def.dependencies:
                raise ValueError(
                    f"Impossibile disattivare: {enabled_mod.module_id} dipende da {module_id}"
                )
        
        tm.is_enabled = False
        tm.disabled_at = datetime.utcnow()
        db.session.commit()
        
        # Hook: notifica plugin system
        PluginRegistry.disable(module_id)
        
        return True
    
    @staticmethod
    def get_module_config(tenant_id: int, module_id: str) -> dict:
        """Restituisce la configurazione di un modulo per un tenant."""
        tm = TenantModule.query.filter_by(
            tenant_id=tenant_id,
            module_id=module_id
        ).first()
        return tm.config if tm else {}
    
    @staticmethod
    def update_module_config(tenant_id: int, module_id: str, config: dict) -> dict:
        """Aggiorna la configurazione di un modulo."""
        tm = TenantModule.query.filter_by(
            tenant_id=tenant_id,
            module_id=module_id
        ).first()
        
        if not tm:
            raise ValueError(f"Modulo {module_id} non attivo per questo tenant")
        
        tm.config = config
        db.session.commit()
        return tm.config
```

### 4.4 API Moduli

```python
# backend/core/api/modules.py

from flask import request
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity, jwt_required
from flask_smorest import Blueprint, abort

blp = Blueprint('modules', __name__, url_prefix='/api/v1/modules')

@blp.route('/')
class ModuleList(MethodView):
    @blp.response(200)
    @jwt_required()
    def get(self):
        """Lista moduli disponibili nel sistema."""
        modules = ModuleService.get_available_modules()
        return [m.to_dict() for m in modules]

@blp.route('/enabled')
class TenantModules(MethodView):
    @blp.response(200)
    @jwt_required()
    def get(self):
        """Lista moduli attivi per il tenant corrente."""
        user = User.query.get(get_jwt_identity())
        tenant_id = user.tenant_id
        
        enabled = TenantModuleService.get_enabled_modules(tenant_id)
        return [tm.to_dict() for tm in enabled]
    
    @blp.arguments(ModuleEnableSchema)
    @blp.response(200)
    @jwt_required()
    def post(self, args):
        """Attiva un modulo."""
        user = User.query.get(get_jwt_identity())
        
        # Solo admin può attivare moduli
        if user.role != 'admin':
            abort(403, message="Solo gli admin possono gestire i moduli")
        
        module_id = args['module_id']
        license_key = args.get('license_key')
        config = args.get('config', {})
        
        try:
            tm = TenantModuleService.enable_module(
                user.tenant_id, 
                module_id,
                license_key,
                config
            )
            return tm.to_dict()
        except ValueError as e:
            abort(400, message=str(e))

@blp.route('/<string:module_id>')
class ModuleDetail(MethodView):
    @blp.response(200)
    @jwt_required()
    def get(self, module_id):
        """Dettagli modulo."""
        module = ModuleService.get_module_by_id(module_id)
        if not module:
            abort(404, message="Modulo non trovato")
        
        user = User.query.get(get_jwt_identity())
        is_enabled = TenantModuleService.is_module_enabled(user.tenant_id, module_id)
        
        result = module.to_dict()
        result['is_enabled'] = is_enabled
        return result
    
    @blp.response(204)
    @jwt_required()
    def delete(self, module_id):
        """Disattiva un modulo."""
        user = User.query.get(get_jwt_identity())
        
        if user.role != 'admin':
            abort(403, message="Solo gli admin possono gestire i moduli")
        
        try:
            TenantModuleService.disable_module(user.tenant_id, module_id)
        except ValueError as e:
            abort(400, message=str(e))

@blp.route('/<string:module_id>/config')
class ModuleConfig(MethodView):
    @blp.response(200)
    @jwt_required()
    def get(self, module_id):
        """Configurazione del modulo."""
        user = User.query.get(get_jwt_identity())
        config = TenantModuleService.get_module_config(user.tenant_id, module_id)
        return {'config': config}
    
    @blp.arguments(ModuleConfigSchema)
    @blp.response(200)
    @jwt_required()
    def put(self, args, module_id):
        """Aggiorna configurazione del modulo."""
        user = User.query.get(get_jwt_identity())
        
        config = TenantModuleService.update_module_config(
            user.tenant_id, 
            module_id, 
            args['config']
        )
        return {'config': config}
```

---

## 5. Interfacce Plugin Estese

### 5.1 Plugin con Supporto Multi-Tenant

```python
# backend/plugins/base.py (esteso)

class BasePlugin(ABC):
    """Plugin con supporto multi-tenant e licensing."""
    
    # Metadata
    name: str = "base_plugin"
    version: str = "1.0.0"
    description: str = ""
    icon: str = "box"
    
    # Licensing
    is_free: bool = True
    price: Optional[float] = None
    plan_required: str = "starter"
    
    # Dipendenze
    dependencies: List[str] = []
    
    def __init__(self, app=None, db=None, api=None):
        self.app = app
        self.db = db
        self.api = api
        self._enabled = False
    
    @property
    def enabled(self) -> bool:
        return self._enabled
    
    # === Metodi Obbligatori ===
    
    @abstractmethod
    def register(self):
        """Registra risorse (blueprint, menu, etc)."""
        pass
    
    @abstractmethod
    def init_db(self):
        """Inizializza tabelle database."""
        pass
    
    # === Hook Opzionali ===
    
    def before_request(self, tenant_id: int):
        """Hook pre-request con contesto tenant."""
        pass
    
    def after_request(self, response, tenant_id: int):
        """Hook post-request."""
        return response
    
    def on_enable(self, tenant_id: int, config: dict):
        """Called when tenant enables module."""
        pass
    
    def on_disable(self, tenant_id: int):
        """Called when tenant disables module."""
        pass
    
    def get_menu_items(self, tenant_id: int) -> List[dict]:
        """Restituisce voci di menu per il modulo."""
        return []
    
    def get_widgets(self, tenant_id: int) -> List[dict]:
        """Restituisce widget per la dashboard."""
        return []
    
    def get_api_routes(self) -> List[str]:
        """Restituisce rotte API esposte."""
        return []
    
    def validate_license(self, license_key: str, tenant_id: int) -> bool:
        """Valida licenza (per moduli premium)."""
        return True
```

### 5.2 Esempio Plugin Esteso

```python
# backend/plugins/accounting/plugin.py

from backend.plugins.base import BasePlugin, register_plugin

class AccountingPlugin(BasePlugin):
    """Double-entry accounting plugin."""
    
    name = "accounting"
    version = "1.0.0"
    description = "Contabilità con partita doppia"
    icon = "calculator"
    
    # Licensing
    is_free = True  # Built-in
    plan_required = "starter"
    
    dependencies = []
    
    def register(self):
        """Registra blueprint e menu."""
        if self.api:
            self.api.register_blueprint(blp)
    
    def init_db(self):
        """Crea tabelle contabili."""
        # Già gestito da SQLAlchemy
        pass
    
    def get_menu_items(self, tenant_id: int) -> List[dict]:
        """Voci menu contabilità."""
        return [
            {
                'id': 'accounting',
                'label': 'Contabilità',
                'icon': 'calculator',
                'children': [
                    {'id': 'chart_of_accounts', 'label': 'Piano dei Conti', 'path': '/coa'},
                    {'id': 'journal', 'label': 'Giornale', 'path': '/journal'},
                    {'id': 'invoices', 'label': 'Fatture', 'path': '/invoices'},
                    {'id': 'trial_balance', 'label': 'Bilancio di Verifica', 'path': '/trial-balance'},
                ]
            }
        ]
    
    def get_widgets(self, tenant_id: int) -> List[dict]:
        """Widget dashboard."""
        return [
            {
                'id': 'accounting_summary',
                'type': 'chart',
                'title': 'Situazione Contabile',
                'size': 'large',
                'config': {'chart_type': 'line'}
            }
        ]


# Funzione richiesta dal registry
def get_plugin():
    return AccountingPlugin


register_plugin(AccountingPlugin)
```

---

## 6. Configurazione Backend

### 6.1 Configurazione Centrale

```yaml
# config/modules.yml

# Definizione centralizzata moduli
modules:
  # CORE - Sempre disponibili
  parties:
    name: "Anagrafiche"
    category: "core"
    icon: "users"
    menu_position: 10
    builtin: true
  
  products:
    name: "Prodotti"
    category: "core"
    icon: "package"
    menu_position: 20
    builtin: true
  
  sales:
    name: "Vendite"
    category: "core"
    icon: "shopping-cart"
    menu_position: 30
    builtin: true
  
  purchases:
    name: "Acquisti"
    category: "core"
    icon: "truck"
    menu_position: 40
    builtin: true

  # BUILTIN - Inclusi nel piano
  accounting:
    name: "Contabilità"
    category: "builtin"
    icon: "calculator"
    menu_position: 50
    is_free: true
    dependencies: []
  
  inventory:
    name: "Magazzino"
    category: "builtin"
    icon: "warehouse"
    menu_position: 60
    is_free: true
    dependencies: ["products"]
  
  hr:
    name: "Risorse Umane"
    category: "builtin"
    icon: "users"
    menu_position: 70
    is_free: true
    dependencies: []

  # PREMIUM - A pagamento
  projects:
    name: "Progetti"
    category: "premium"
    icon: "folder"
    menu_position: 80
    is_free: false
    price: 99.00
    plan_required: "professional"
    dependencies: []
  
  crm:
    name: "CRM"
    category: "premium"
    icon: "heart"
    menu_position: 90
    is_free: false
    price: 149.00
    plan_required: "professional"
    dependencies: []
  
  manufacturing:
    name: "Produzione"
    category: "premium"
    icon: "factory"
    menu_position: 100
    is_free: false
    price: 199.00
    plan_required: "enterprise"
    dependencies: ["inventory"]

# Default per piano
plans:
  starter:
    modules:
      - parties
      - products
      - sales
      - purchases
      - accounting
      - inventory
  
  professional:
    modules:
      - parties
      - products
      - sales
      - purchases
      - accounting
      - inventory
      - hr
      - projects
      - crm
  
  enterprise:
    modules: "*"  # Tutti i moduli
```

### 6.2 Caricamento Configurazione

```python
# backend/core/config.py

import yaml
from pathlib import Path
from typing import Dict, List, Any

class ModuleConfig:
    """Gestisce configurazione moduli da file YAML."""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def load(self, config_path: str = None):
        """Carica configurazione da file."""
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / 'config' / 'modules.yml'
        
        with open(config_path, 'r') as f:
            self._config = yaml.safe_load(f)
        
        return self._config
    
    @property
    def modules(self) -> Dict[str, Any]:
        if self._config is None:
            self.load()
        return self._config.get('modules', {})
    
    @property
    def plans(self) -> Dict[str, Any]:
        if self._config is None:
            self.load()
        return self._config.get('plans', {})
    
    def get_module(self, module_id: str) -> Dict[str, Any]:
        """Restituisce configurazione modulo."""
        return self.modules.get(module_id)
    
    def get_plan_modules(self, plan: str) -> List[str]:
        """Restituisce moduli inclusi in un piano."""
        plan_config = self.plans.get(plan, {})
        modules = plan_config.get('modules', [])
        
        if modules == "*":
            # Tutti i moduli
            return list(self.modules.keys())
        
        return modules


# Istanza globale
module_config = ModuleConfig()
```

---

## 7. Sincronizzazione Frontend/Backend

### 7.1 Endpoint Informazioni Moduli

```python
# backend/core/api/system.py

@blp.route('/system/modules-info')
class SystemModulesInfo(MethodView):
    @blp.response(200)
    @jwt_required()
    def get(self):
        """
        Restituisce informazioni completo moduli per UI.
        Include stato, menu, widget per il tenant corrente.
        """
        user = User.query.get(get_jwt_identity())
        tenant_id = user.tenant_id
        
        # Carica configurazione
        config = module_config
        
        # Moduli abilitati per tenant
        enabled_modules = TenantModuleService.get_enabled_modules(tenant_id)
        enabled_ids = {tm.module_id for tm in enabled_modules}
        
        result = {
            'available_modules': [],
            'enabled_modules': list(enabled_ids),
            'menu': [],
            'widgets': []
        }
        
        # Costruisci menu da moduli attivi
        menu_items = []
        widgets = []
        
        for module_id, mod_def in config.modules.items():
            module_info = {
                'id': module_id,
                'name': mod_def.get('name'),
                'description': mod_def.get('description'),
                'category': mod_def.get('category'),
                'icon': mod_def.get('icon'),
                'is_enabled': module_id in enabled_ids,
                'is_free': mod_def.get('is_free', True),
                'price': mod_def.get('price'),
                'plan_required': mod_def.get('plan_required'),
            }
            result['available_modules'].append(module_info)
            
            # Se abilitato, aggiungi al menu
            if module_id in enabled_ids:
                # Get plugin menu items
                plugin = PluginRegistry.get(module_id)
                if plugin and hasattr(plugin, 'get_menu_items'):
                    items = plugin.get_menu_items(tenant_id)
                    menu_items.extend(items)
                
                # Get plugin widgets
                if plugin and hasattr(plugin, 'get_widgets'):
                    w = plugin.get_widgets(tenant_id)
                    widgets.extend(w)
        
        result['menu'] = menu_items
        result['widgets'] = widgets
        
        return result
```

### 7.2 Hook Frontend per Sidebar

```jsx
// frontend/src/hooks/useModules.js

import { useState, useEffect } from 'react';
import { api } from '../components/api';

export function useModules() {
  const [modules, setModules] = useState({
    available: [],
    enabled: [],
    menu: [],
    widgets: [],
    loading: true,
    error: null
  });
  
  useEffect(() => {
    fetchModulesInfo();
  }, []);
  
  const fetchModulesInfo = async () => {
    try {
      const response = await api.get('/system/modules-info');
      setModules({
        available: response.data.available_modules,
        enabled: response.data.enabled_modules,
        menu: response.data.menu,
        widgets: response.data.widgets,
        loading: false,
        error: null
      });
    } catch (error) {
      setModules(prev => ({
        ...prev,
        loading: false,
        error: error.message
      }));
    }
  };
  
  const enableModule = async (moduleId, config = {}) => {
    await api.post('/modules/enabled', { module_id: moduleId, config });
    await fetchModulesInfo();
  };
  
  const disableModule = async (moduleId) => {
    await api.delete(`/modules/${moduleId}`);
    await fetchModulesInfo();
  };
  
  return {
    ...modules,
    enableModule,
    disableModule,
    refresh: fetchModulesInfo
  };
}
```

### 7.2 Componente Sidebar Modulare

```jsx
// frontend/src/components/ModuleSidebar.jsx

import { useModules } from '../hooks/useModules';

export function ModuleSidebar() {
  const { menu, loading } = useModules();
  
  if (loading) return <div>Caricamento menu...</div>;
  
  return (
    <nav className="sidebar">
      {menu.map(section => (
        <div key={section.id} className="menu-section">
          <h3>{section.label}</h3>
          <ul>
            {section.children?.map(child => (
              <li key={child.id}>
                <Link to={child.path}>
                  <i className={`icon-${child.icon || section.icon}`} />
                  {child.label}
                </Link>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </nav>
  );
}
```

---

## 8. Middleware Protezione Moduli

```python
# backend/core/middleware/module_middleware.py

from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

class ModuleMiddleware:
    """Middleware per verificare accesso ai moduli."""
    
    @staticmethod
    def require_module(module_id):
        """
        Decorator per proteggere endpoint con modulo richiesto.
        
        Usage:
            @require_module('accounting')
            def my_endpoint():
                ...
        """
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # Verifica JWT
                verify_jwt_in_request()
                user_id = get_jwt_identity()
                
                user = User.query.get(user_id)
                tenant_id = user.tenant_id
                
                # Verifica modulo abilitato
                if not TenantModuleService.is_module_enabled(tenant_id, module_id):
                    return jsonify({
                        'error': 'MODULE_NOT_ENABLED',
                        'message': f"Modulo {module_id} non abilitato"
                    }), 403
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    @staticmethod
    def get_enabled_modules_middleware():
        """
        Middleware per aggiungere lista moduli abilitati a ogni richiesta.
        """
        def middleware():
            try:
                verify_jwt_in_request(optional=True)
                user_id = get_jwt_identity()
                
                if user_id:
                    user = User.query.get(user_id)
                    enabled = TenantModuleService.get_enabled_modules(user.tenant_id)
                    g.enabled_modules = [tm.module_id for tm in enabled]
                else:
                    g.enabled_modules = []
            except:
                g.enabled_modules = []
        
        return middleware
```

---

## 9. Gestione Errori e Hook

### 9.1 Errori Comuni

```python
# Errori standard per gestione moduli

class ModuleNotFoundError(ValueError):
    """Modulo non trovato nel sistema."""
    pass

class ModuleNotEnabledError(ValueError):
    """Modulo non abilitato per il tenant."""
    pass

class ModuleDependencyError(ValueError):
    """Dipendenza non soddisfatta."""
    pass

class PlanNotCompatibleError(ValueError):
    """Piano corrente non supporta il modulo."""
    pass

class LicenseInvalidError(ValueError):
    """Licenza non valida."""
    pass
```

### 9.2 Hook Lifecycle

```python
# Nel PluginRegistry, aggiungere hook per lifecycle

class PluginRegistry:
    # ... metodi esistenti ...
    
    @staticmethod
    def on_module_enabled(tenant_id: int, module_id: str):
        """Chiamato dopo attivazione modulo."""
        plugin = cls._plugins.get(module_id)
        if plugin and hasattr(plugin, 'on_enable'):
            plugin.on_enable(tenant_id, {})
    
    @staticmethod
    def on_module_disabled(tenant_id: int, module_id: str):
        """Chiamato dopo disattivazione modulo."""
        plugin = cls._plugins.get(module_id)
        if plugin and hasattr(plugin, 'on_disable'):
            plugin.on_disable(tenant_id)
```

---

## 10. Installazione Iniziale Moduli

### 10.1 Seed Database

```python
# backend/core/seed_modules.py

def seed_modules():
    """Inizializza moduli nel database."""
    
    config = module_config
    
    for module_id, mod_def in config.modules.items():
        existing = ModuleDefinition.query.filter_by(module_id=module_id).first()
        
        if not existing:
            module = ModuleDefinition(
                module_id=module_id,
                name=mod_def['name'],
                description=mod_def.get('description', ''),
                category=mod_def['category'],
                version=mod_def.get('version', '1.0.0'),
                is_free=mod_def.get('is_free', True),
                price=mod_def.get('price'),
                plan_required=mod_def.get('plan_required', 'starter'),
                dependencies=mod_def.get('dependencies', []),
                icon=mod_def.get('icon', 'box'),
                menu_position=mod_def.get('menu_position', 100),
                is_active=True
            )
            db.session.add(module)
    
    db.session.commit()

# Chiamare in init_db() dell'app
```

---

## 11. Prossimi Passi Implementativi

### Priorità 1: Core
- [ ] Aggiungere modelli TenantModule e ModuleDefinition
- [ ] Creare ModuleService e TenantModuleService
- [ ] Implementare API moduli
- [ ] Creare config/modules.yml

### Priorità 2: Plugin System
- [ ] Estendere BasePlugin con nuove interfacce
- [ ] Aggiornare PluginRegistry per supportare per-tenant
- [ ] Implementare middleware protezione

### Priorità 3: Frontend
- [ ] Creare hook useModules
- [ ] Modificare Sidebar per usare menu dinamico
- [ ] Creare pagina gestione moduli (admin)

### Priorità 4: Licensing
- [ ] Implementare validazione license_key
- [ ] Aggiungere verifica piano
- [ ] Integrare con sistema pagamenti (futuro)

---

## 12. Considerazioni Sicurezza

1. **Isolamento dati**: Ogni modulo deve rispettare il TenantContext
2. **Protezione API**: middleware `@require_module()` per endpoint sensibili
3. **Validazione licenze**: mai fidarsi solo del client
4. **Audit log**: tracciare attivazione/disattivazione moduli

---

*Documento tecnico per implementazione sistema moduli FlaskERP*
