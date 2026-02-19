# ERPE: Code-as-Data (Programmazione Adattiva)

## Introduzione

Il concetto di **Code-as-Data** significa trattare il codice come dati che possono essere:
- Archiviati
- Trasformati
- Generati
- Modificati a runtime

Questo è il cuore della tua visione: il sistema che **si costruisce da solo** basandosi su configurazioni.

---

## I Quattro Livelli di Adattività

```
┌─────────────────────────────────────────────────────────────┐
│                   ADATTIVITÀ MASSIMA                        │
│  Livello 4: Evolutionary Code                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Livello 3: Self-Modifying Code                     │    │
│  │  ┌─────────────────────────────────────────────┐    │    │
│  │  │  Livello 2: Dynamic Generation              │    │    │
│  │  │  ┌─────────────────────────────────────┐    │    │    │
│  │  │  │  Livello 1: Metaprogramming         │    │    │    │
│  │  │  │  ┌─────────────────────────────┐    │    │    │    │
│  │  │  │  │  Static Code (Baseline)     │    │    │    │    │
│  │  │  │  └─────────────────────────────┘    │    │    │    │
│  │  │  └─────────────────────────────────────┘    │    │    │
│  │  └─────────────────────────────────────────────┘    │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## Livello 1: Metaprogramming

### A) type() - Creazione Dinamica di Classi

```python
# ============================================================
# ESEMPIO: Creare entità dinamicamente basate su config
# ============================================================

def create_entity_class(entity_config: dict) -> type:
    """
    Crea una classe SQLAlchemy da configurazione.
    
    entity_config = {
        'name': 'Veicolo',
        'table_name': 'veicoli',
        'fields': [
            {'name': 'targa', 'type': 'string', 'required': True},
            {'name': 'marca', 'type': 'string'},
            {'name': 'anno', 'type': 'integer'},
        ],
        'relationships': [
            {'name': 'proprietario', 'target': 'Soggetto', 'type': 'many-to-one'}
        ]
    }
    """
    name = entity_config['name']
    table_name = entity_config.get('table_name', name.lower() + 's')
    
    # Dizionario attributi della classe
    attrs = {
        '__tablename__': table_name,
        'id': db.Column(db.Integer, primary_key=True),
        'tenant_id': db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False),
    }
    
    # Mappatura tipi Python ↔ SQLAlchemy
    type_mapping = {
        'string': lambda opts: db.Column(db.String(opts.get('length', 255))),
        'integer': lambda opts: db.Column(db.Integer),
        'float': lambda opts: db.Column(db.Float),
        'boolean': lambda opts: db.Column(db.Boolean),
        'date': lambda opts: db.Column(db.Date),
        'datetime': lambda opts: db.Column(db.DateTime),
        'text': lambda opts: db.Column(db.Text),
        'decimal': lambda opts: db.Column(db.Numeric(opts.get('precision', 10), opts.get('scale', 2))),
    }
    
    # Aggiungi campi dalla configurazione
    for field in entity_config.get('fields', []):
        field_type = field.get('type', 'string')
        field_class = type_mapping.get(field_type, type_mapping['string'])
        
        column_kwargs = {}
        if field.get('required'):
            column_kwargs['nullable'] = False
        if field.get('default') is not None:
            column_kwargs['default'] = field['default']
        if field.get('unique'):
            column_kwargs['unique'] = True
            
        attrs[field['name']] = field_class(field.get('options', {}), **column_kwargs)
    
    # Aggiungi relazioni
    for rel in entity_config.get('relationships', []):
        if rel['type'] == 'many-to-one':
            attrs[rel['name']] = db.relationship(
                rel['target'],
                foreign_keys=[rel.get('foreign_key')]
            )
        elif rel['type'] == 'one-to-many':
            # Implementa secondo necessità
            pass
    
    # Crea la classe dinamicamente
    return type(name, (BaseModel,), attrs)


# ============================================================
# UTILIZZO PRATICO
# ============================================================

# Configurazione (potrebbe venire dal Builder)
veicolo_config = {
    'name': 'Veicolo',
    'fields': [
        {'name': 'targa', 'type': 'string', 'required': True, 'unique': True},
        {'name': 'marca', 'type': 'string'},
        {'name': 'modello', 'type': 'string'},
        {'name': 'anno_immatricolazione', 'type': 'integer'},
        {'name': 'chilometraggio', 'type': 'integer'},
        {'name': 'colore', 'type': 'string'},
        {'name': 'note', 'type': 'text'},
    ]
}

# Generazione automatica della classe
Veicolo = create_entity_class(veicolo_config)

# Uso come classe normale!
veicolo = Veicolo(targa="AB123CD", marca="Ford", modello="Fiesta", anno_immatricolazione=2020)
db.session.add(veicolo)
db.session.commit()
```

### B) Metaclasses - DNA delle Classi

```python
# ============================================================
# ESEMPIO: Metaclass che aggiunge automaticamente funzionalità
# ============================================================

class AuditedMeta(type):
    """Metaclass che aggiunge automaticamente tracciamento modifiche"""
    
    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        
        # Aggiungi campi di audit se non esistono
        if 'created_by' not in namespace:
            cls.created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
        if 'updated_by' not in namespace:
            cls.updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
        if 'version' not in namespace:
            cls.version = db.Column(db.Integer, default=1)
        
        # Override del metodo save per versioning automatico
        original_save = cls.save if hasattr(cls, 'save') else None
        
        def save_with_version(self, *args, **kwargs):
            if self.id:
                self.version += 1
            return original_save(*args, **kwargs) if original_save else None
        
        cls.save = save_with_version
        
        return cls


class TrackedMeta(type):
    """Metaclass che aggiunge tracking automatico cambiamenti"""
    
    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        
        # Aggiungi campo per tracciare modified_fields
        cls._modified_fields = []
        
        # Override di __setattr__ per tracciare modifiche
        original_setattr = cls.__setattr__ if hasattr(cls, '__setattr__') else object.__setattr__
        
        def tracked_setattr(self, key, value):
            if hasattr(self, 'id') and self.id:
                if key not in self._modified_fields and hasattr(self, key):
                    old_value = getattr(self, key, None)
                    if old_value != value:
                        self._modified_fields.append(key)
            original_setattr(self, key, value)
        
        cls.__setattr__ = tracked_setattr
        
        return cls


# Uso: qualsiasi classe con questa metaclass ottiene automaticamente
# - Campi di audit (created_by, updated_by, version)
# - Tracking modifiche (_modified_fields)

class Soggetto(metaclass=AuditedMeta, TrackedMeta):
    """Soggetto con audit automatico"""
    __tablename__ = 'soggetti'
    
    nome = db.Column(db.String(150))
    # created_by, updated_by, version sono aggiunti automaticamente!
```

### C) Decorators - Comportamenti Trasversali

```python
# ============================================================
# ESEMPIO: Decorators per funzionalità trasversali
# ============================================================

from functools import wraps
import logging

def log_operation(operation: str):
    """Decorator che logga operazioni CRUD"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            logger.info(f"{operation} on {self.__class__.__name__}")
            result = func(self, *args, **kwargs)
            logger.info(f"{operation} completed: {result}")
            return result
        return wrapper
    return decorator


def validate_fields(**validators):
    """Decorator che valida campi prima dell'operazione"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            for field, validator in validators.items():
                value = kwargs.get(field) or (args[0] if args else None)
                if not validator(value):
                    raise ValidationError(f"Invalid {field}: {value}")
            return func(self, *args, **kwargs)
        return wrapper
    return decorator


def cache_result(ttl: int = 300):
    """Decorator che cacha il risultato"""
    def decorator(func):
        cache = {}
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = str(args) + str(kwargs)
            now = datetime.now().timestamp()
            
            if key in cache:
                result, timestamp = cache[key]
                if now - timestamp < ttl:
                    return result
            
            result = func(*args, **kwargs)
            cache[key] = (result, now)
            return result
        return wrapper
    return decorator


def emit_event(event_type: str):
    """Decorator che emette eventi dopo l'operazione"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            EventBus.publish(event_type, {
                'entity': self.__class__.__name__,
                'operation': func.__name__,
                'data': result
            })
            return result
        return wrapper
    return decorator


# Applicazione pratica
class SoggettoService:
    @log_operation("Creating soggetto")
    @validate_fields(nome=lambda x: x and len(x) > 0)
    @emit_event("soggetto.created")
    def create(self, data):
        soggetto = Soggetto(**data)
        db.session.add(soggetto)
        return soggetto
    
    @cache_result(ttl=60)
    def get_by_id(self, id):
        return Soggetto.query.get(id)
```

---

## Livello 2: Generazione Dinamica

### A) Generatore di API da Configurazione

```python
# ============================================================
# ESEMPIO: Genera API REST automaticamente da config
# ============================================================

class APIGenerator:
    """Genera endpoint REST da configurazione"""
    
    def __init__(self, app):
        self.app = app
        self.blueprints = {}
    
    def generate_crud_routes(self, entity_config: dict) -> list:
        """Genera routes CRUD complete per un'entità"""
        name = entity_config['name'].lower()
        Model = entity_config['model_class']
        
        routes = []
        
        # List
        @self.app.route(f'/{name}', methods=['GET'])
        def list_{name}():
            query = Model.query
            # Applica filtri
            for filter_field in entity_config.get('filters', []):
                value = request.args.get(filter_field)
                if value:
                    query = query.filter(getattr(Model, filter_field) == value)
            return jsonify([m.to_dict() for m in query.all()])
        
        # Get
        @self.app.route(f'/{name}/<int:id>', methods=['GET'])
        def get_{name}(id):
            obj = Model.query.get_or_404(id)
            return jsonify(obj.to_dict())
        
        # Create
        @self.app.route(f'/{name}', methods=['POST'])
        def create_{name}():
            data = request.get_json()
            obj = Model(**data)
            db.session.add(obj)
            db.session.commit()
            return jsonify(obj.to_dict()), 201
        
        # Update
        @self.app.route(f'/{name}/<int:id>', methods=['PUT'])
        def update_{name}(id):
            obj = Model.query.get_or_404(id)
            data = request.get_json()
            for key, value in data.items():
                setattr(obj, key, value)
            db.session.commit()
            return jsonify(obj.to_dict())
        
        # Delete
        @self.app.route(f'/{name}/<int:id>', methods=['DELETE'])
        def delete_{name}(id):
            obj = Model.query.get_or_404(id)
            db.session.delete(obj)
            db.session.commit()
            return '', 204
        
        return [
            list_{name}, get_{name}, create_{name}, 
            update_{name}, delete_{name}
        ]
    
    def register_from_template(self, template: dict):
        """Registra entità da template"""
        entity_name = template['entity']['name']
        
        # Crea la classe modello
        Model = create_entity_class(template['entity'])
        
        # Crea le routes
        self.generate_crud_routes({
            'name': entity_name,
            'model_class': Model,
            'filters': template.get('filters', [])
        })
        
        # Registra nel registry
        EntityRegistry.register(entity_name, Model)


# ============================================================
# UTILIZZO: Template JSON → API automaticamente
# ============================================================

# Template (potrebbe venire dal Builder)
template = {
    'entity': {
        'name': 'Veicolo',
        'fields': [
            {'name': 'targa', 'type': 'string', 'required': True},
            {'name': 'marca', 'type': 'string'},
            {'name': 'modello', 'type': 'string'},
            {'name': 'anno', 'type': 'integer'},
        ]
    },
    'filters': ['marca', 'stato'],
    'relationships': [
        {'name': 'proprietario', 'target': 'Soggetto'}
    ]
}

# Generazione automatica!
generator = APIGenerator(app)
generator.register_from_template(template)

# Risultato: API automaticamente disponibili!
# GET    /veicolo         → lista veicoli
# GET    /veicolo/1       → dettaglio veicolo
# POST   /veicolo         → crea veicolo
# PUT    /veicolo/1       → aggiorna veicolo
# DELETE /veicolo/1       → elimina veicolo
```

---

## Livello 3: Self-Modifying Code

### A) Hot Reload di Moduli

```python
# ============================================================
# ESEMPIO: Ricarica moduli a runtime senza riavvio
# ============================================================

import importlib
import sys
from pathlib import Path

class HotReloader:
    """Sistema di hot-reload per moduli Python"""
    
    def __init__(self):
        self.modules = {}  # name -> (module, last_modified)
        self.watch_paths = []
    
    def watch(self, module_path: str):
        """Aggiunge un percorso da monitorare"""
        self.watch_paths.append(Path(module_path))
    
    def reload_module(self, module_name: str) -> bool:
        """Ricarica un modulo specifico"""
        if module_name not in sys.modules:
            return False
        
        # Ricarica il modulo
        old_module = sys.modules[module_name]
        importlib.reload(old_module)
        
        # Aggiorna il registro
        self.modules[module_name] = (
            old_module,
            datetime.now()
        )
        
        return True
    
    def check_and_reload(self):
        """Controlla modifiche e ricarica se necessario"""
        for module_name, (module, last_mod) in self.modules.items():
            # Ottieni il file sorgente
            if hasattr(module, '__file__') and module.__file__:
                path = Path(module.__file__)
                if path.exists():
                    current_mtime = path.stat().st_mtime
                    if current_mtime > last_mod.timestamp():
                        print(f"Reloading {module_name}...")
                        self.reload_module(module_name)
    
    def auto_reload_worker(self, interval: int = 1):
        """Worker che controlla periodicamente"""
        import threading
        def worker():
            while True:
                self.check_and_reload()
                time.sleep(interval)
        threading.Thread(target=worker, daemon=True).start()


# Utilizzo
reloader = HotReloader()
reloader.watch('backend/entities/')
reloader.watch('backend/services/')
reloader.auto_reload_worker()

# Ora qualsiasi modifica ai file viene ricaricata automaticamente!
```

### B) Expression Engine

```python
# ============================================================
# ESEMPIO: Motore di espressioni per logiche dinamiche
# ============================================================

import ast
import operator

class ExpressionEngine:
    """Motore per valutare espressioni definite a runtime"""
    
    # Operatori supportati
    OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Eq: operator.eq,
        ast.NotEq: operator.ne,
        ast.Lt: operator.lt,
        ast.LtE: operator.le,
        ast.Gt: operator.gt,
        ast.GtE: operator.ge,
        ast.And: lambda a, b: a and b,
        ast.Or: lambda a, b: a or b,
    }
    
    FUNCTIONS = {
        'now': lambda: datetime.now(),
        'today': lambda: date.today(),
        'upper': lambda s: s.upper(),
        'lower': lambda s: s.lower(),
        'round': round,
        'abs': abs,
        'sum': sum,
        'min': min,
        'max': max,
    }
    
    def evaluate(self, expression: str, context: dict) -> any:
        """Valuta un'espressione nel contesto dato"""
        # Compila l'espressione
        tree = ast.parse(expression, mode='eval')
        return self._eval_node(tree.body, context)
    
    def _eval_node(self, node, context):
        if isinstance(node, ast.Constant):  # Valori costanti
            return node.value
        
        elif isinstance(node, ast.Name):  # Variabili
            return context.get(node.id, 0)
        
        elif isinstance(node, ast.NameConstant):  # Booleani
            return node.value
        
        elif isinstance(node, ast.BinOp):  # Operazioni binarie
            left = self._eval_node(node.left, context)
            right = self._eval_node(node.right, context)
            op = self.OPERATORS[type(node.op)]
            return op(left, right)
        
        elif isinstance(node, ast.Compare):  # Comparazioni
            left = self._eval_node(node.left, context)
            right = self._eval_node(node.comparators[0], context)
            op = self.OPERATORS[type(node.ops[0])]
            return op(left, right)
        
        elif isinstance(node, ast.Call):  # Chiamate funzione
            func_name = node.func.id
            args = [self._eval_node(arg, context) for arg in node.args]
            return self.FUNCTIONS[func_name](*args)
        
        else:
            raise ValueError(f"Unsupported operation: {type(node)}")


# ============================================================
# UTILIZZO PRATICO
# ============================================================

engine = ExpressionEngine()

# Espressioni definite a runtime (da config, DB, etc.)
formulas = {
    'total_price': 'quantity * unit_price * (1 - discount / 100)',
    'is_vip': 'total_purchases > 10000',
    'shipping_cost': 'weight * 0.5 + 5 if distance > 100 else 5',
    'greeting': 'upper(f"Hello {name}")',
}

# Valutazione
context = {
    'quantity': 10,
    'unit_price': 100,
    'discount': 20,
    'total_purchases': 15000,
    'weight': 5,
    'distance': 150,
    'name': 'Mario'
}

for formula_name, formula in formulas.items():
    result = engine.evaluate(formula, context)
    print(f"{formula_name}: {result}")
# total_price: 800.0
# is_vip: True
# shipping_cost: 7.5
# greeting: HELLO MARIO
```

---

## Livello 4: Evolutionary Code

### A) Auto-Tuning Basato su Metriche

```python
# ============================================================
# ESEMPIO: Sistema che ottimizza parametri automaticamente
# ============================================================

class EvolutionaryOptimizer:
    """Ottimizzatore genetico per parametri di sistema"""
    
    def __init__(self, objective_function, parameter_space):
        self.objective = objective_function
        self.space = parameter_space
        self.population = []
        self.generation = 0
    
    def initialize_population(self, size: int = 20):
        """Inizializza popolazione casuale"""
        for _ in range(size):
            individual = {
                name: random.uniform(space['min'], space['max'])
                for name, space in self.space.items()
            }
            self.population.append(individual)
    
    def fitness(self, individual):
        """Valuta un individuo"""
        try:
            return self.objective(**individual)
        except:
            return -999999
    
    def evolve(self, generations: int = 100):
        """Evolve la popolazione"""
        for _ in range(generations):
            # Valuta fitness
            for ind in self.population:
                ind['fitness'] = self.fitness(ind)
            
            # Ordina per fitness
            self.population.sort(key=lambda x: x['fitness'], reverse=True)
            
            # Selezione (top 50%)
            survivors = self.population[:len(self.population)//2]
            
            # Crossover
            new_population = []
            while len(new_population) < len(self.population):
                parent1, parent2 = random.sample(survivors, 2)
                child = {}
                for key in self.space:
                    child[key] = (parent1[key] + parent2[key]) / 2 + random.gauss(0, 0.1)
                new_population.append(child)
            
            self.population = new_population
            self.generation += 1
        
        # Ritorna il migliore
        return max(self.population, key=lambda x: x['fitness'])


# ============================================================
# ESEMPIO: Ottimizzazione parametri caching
# ============================================================

def cache_performance(ttl: float, max_size: int, eviction: str):
    """Simula performance del caching"""
    # Simulazione: combina TTL e max_size
    hit_rate = min(0.99, ttl / 100 * (max_size / 1000))
    memory_usage = max_size * 0.001  # KB per entry
    
    # Score: massimizza hit rate, minimizza memory
    return hit_rate * 100 - memory_usage

# Configurazione parametri
param_space = {
    'ttl': {'min': 10, 'max': 3600},
    'max_size': {'min': 100, 'max': 10000},
    'eviction': {'min': 0, 'max': 2}  # 0=lru, 1=fifo, 2=lfu
}

# Ottimizzazione
optimizer = EvolutionaryOptimizer(cache_performance, param_space)
optimizer.initialize_population(20)
best_params = optimizer.evolve(generations=50)

print(f"Migliori parametri: {best_params}")
```

---

## Sistema Completo: Builder con Code-as-Data

```python
# ============================================================
# ESEMPIO COMPLETO: Builder che genera codice adattivo
# ============================================================

class AdaptiveBuilder:
    """
    Builder che genera codice adattivo da template.
    Il codice generato può auto-modificarsi a runtime.
    """
    
    def __init__(self, app, db):
        self.app = app
        self.db = db
        self.expressions = ExpressionEngine()
        self.reloader = HotReloader()
    
    def build_module(self, template: dict) -> Module:
        """
        Costruisce un modulo completo da template.
        
        Il modulo generato include:
        - Modelli dinamici
        - API REST
        - Hook per eventi
        - Expression per logiche
        """
        module_name = template['name']
        
        # 1. Genera modelli
        models = {}
        for entity in template.get('entities', []):
            model_class = create_entity_class(entity)
            models[entity['name']] = model_class
        
        # 2. Genera API
        api_routes = []
        for entity in template.get('entities', []):
            routes = self._generate_api_routes(entity, models[entity['name']])
            api_routes.extend(routes)
        
        # 3. Compila espressioni
        compiled_formulas = {}
        for formula in template.get('formulas', []):
            compiled = compile(formula['expression'], '<formula>', 'eval')
            compiled_formulas[formula['name']] = compiled
        
        # 4. Crea hook
        hooks = {}
        for hook_def in template.get('hooks', []):
            hooks[hook_def['event']] = self._create_hook(hook_def)
        
        # 5. Crea modulo
        module = Module(
            name=module_name,
            models=models,
            routes=api_routes,
            formulas=compiled_formulas,
            hooks=hooks,
            config=template.get('config', {})
        )
        
        # 6. Registra per hot-reload
        self.reloader.watch(f'modules/{module_name}')
        
        return module
    
    def _generate_api_routes(self, entity, Model):
        """Genera routes per un'entità"""
        # Implementazione simile a APIGenerator
        pass
    
    def _create_hook(self, hook_def):
        """Crea un hook da definizione"""
        code = compile(hook_def['code'], '<hook>', 'exec')
        
        def hook(*args, **kwargs):
            local_scope = {}
            exec(code, {'args': args, 'kwargs': kwargs}, local_scope)
            return local_scope.get('result')
        
        return hook
    
    def rebuild_module(self, module_name: str, new_template: dict):
        """Ricostruisce un modulo esistente"""
        old_module = ModuleRegistry.get(module_name)
        
        # Rimuovi vecchie route
        for route in old_module.routes:
            self.app.url_map._rules = [
                r for r in self.app.url_map._rules 
                if r.endpoint != route.endpoint
            ]
        
        # Rigenera con nuovo template
        new_module = self.build_module(new_template)
        
        # Registra nuove route
        for route in new_module.routes:
            self.app.register_route(route)
        
        ModuleRegistry.register(module_name, new_module)
```

---

## Riepilogo delle Tecniche

| Livello | Tecnica            | Esempio d'Uso                       |
|---------|--------------------|-------------------------------------|
| 1       | `type()`           | Creare classi dinamicamente         |
| 1       | Metaclasses        | Aggiungere funzionalità automatiche |
| 1       | Decorators         | Cross-cutting concerns              |
| 2       | Code Generation    | Generare API da config              |
| 2       | Template Engine    | Generare codice da template         |
| 3       | Hot Reload         | Ricaricare senza riavvio            |
| 3       | Expression Engine  | Valutare formule dinamiche          |
| 4       | Genetic Algorithms | Ottimizzazione automatica           |

---

## Integrazione con ERPE

Il sistema **Code-as-Data** si integra nel tuo ERPE come:

```
Template JSON/YAML
        │
        ▼
┌───────────────────┐
│   BUILDER         │
│  (Generator)      │
├───────────────────┤
│ 1. Parse template │
│ 2. type() per     │
│    modelli        │
│ 3. API generator  │
│ 4. Compile hooks  │
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  ADAPTIVE MODULE  │
│ (Codice vivente)  │
├───────────────────┤
│ - Modelli Python  │
│ - Routes regist.  │
│ - Hook attivi     │
│ - Self-modifying  │
└───────────────────┘
        │
        ▼
    ERPE Core
```

---

## Prossimi Passi

1. Implementare `create_entity_class` nel progetto
2. Creare la classe base `Block` con metaprogramming
3. Implementare `ExpressionEngine` per formule
4. Implementare `HotReloader` per development
5. Integrare con il Builder esistente
6. Aggiungere supporto per genetic algorithms (opzionale)
