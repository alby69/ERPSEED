# FlaskERP - Architettura

## Gerarchia di Composizione

Il modello di composizione descrive come i mattoncini base si aggregano:

```
┌─────────────────────────────────────────────────────────────┐
│                      ASTRONAVE (ERP)                        │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                   ROBOT (Modulo)                    │   │
│   │   ┌───────────────────────────────────────────┐    │   │
│   │   │              CONTAINER                     │    │   │
│   │   │   ┌────────┐  ┌────────┐  ┌────────┐   │    │   │
│   │   │   │ MATTON │  │ MATTON │  │ MATTON │   │    │   │
│   │   │   └────────┘  └────────┘  └────────┘   │    │   │
│   │   └───────────────────────────────────────────┘    │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                    BUILDER                          │   │
│   │   Template ──► Parser ──► Generator ──► Module    │   │
│   └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Livello 1: Block (Mattoncino)

Unità atomica - corrisponde alle tabelle archetipiche.

```python
class Block:
    name: str
    version: str
    
    def get_model(self) -> db.Model: ...
    def get_schema(self) -> ma.Schema: ...
    def get_routes(self) -> list[Route]: ...
    def install(self): ...
    def uninstall(self): ...
```

---

## Livello 2: Container

Aggrega block correlati con API unificata.

```python
class Container:
    name: str
    blocks: list[Block]
    api_prefix: str
    
    def add_block(self, block: Block): ...
    def get_routes(self) -> list[Route]: ...
    def get_hooks(self) -> dict[str, callable]: ...
```

---

## Livello 3: Robot (Modulo Funzionale)

Modulo completo con funzionalità di business.

```python
class Robot:
    name: str
    containers: list[Container]
    
    def install(self, app, db): ...
    def uninstall(self): ...
    def get_all_routes(self) -> list[Route]: ...
    def get_blueprint(self) -> Blueprint: ...
```

---

## Livello 4: Spaceship (ERP Orchestrator)

Coordina tutti i moduli.

```python
class Spaceship:
    robots: dict[str, Robot]
    event_bus: EventBus
    
    def register_robot(self, robot: Robot): ...
    def publish_event(self, event: Event): ...
```

---

## Pattern di Comunicazione

### Event Bus

```
Robot A (Sales) ──► order.created ──► Robot B (Accounting)
                                      └──► Robot C (Inventory)
```

### Hook System

```python
@hook('order.before_create')
def validate_order_availability(order_data):
    # Controlla disponibilità magazzino
    pass

@hook('order.after_create')
def notify_sales_manager(order):
    # Invia notifica
    pass
```

---

## Code-as-Data: Programmazione Adattiva

### Livello 1: Metaprogramming

```python
# Creazione dinamica classi
def create_entity_class(config):
    attrs = {
        '__tablename__': config['table'],
        'id': db.Column(db.Integer, primary_key=True),
    }
    for field in config['fields']:
        attrs[field['name']] = db.Column(...)
    return type(config['name'], (BaseModel,), attrs)

# Metaclass per audit automatico
class AuditedMeta(type):
    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        if 'created_by' not in namespace:
            cls.created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
        return cls

# Decorators per cross-cutting concerns
@log_operation
@validate_fields
@emit_event("entity.created")
def save(self): ...
```

### Livello 2: Generazione Dinamica API

```python
class APIGenerator:
    def generate_crud_routes(self, entity_config):
        @self.app.route(f'/{name}', methods=['GET'])
        def list_{name}():
            return jsonify(Model.query.all())
        
        @self.app.route(f'/{name}', methods=['POST'])
        def create_{name}():
            obj = Model(request.get_json())
            db.session.add(obj)
            return jsonify(obj), 201
```

### Livello 3: Self-Modifying Code

```python
# Hot Reload
class HotReloader:
    def reload_module(self, module_name):
        importlib.reload(sys.modules[module_name])

# Expression Engine
class ExpressionEngine:
    def evaluate(self, expression, context):
        # Valuta "quantity * price * (1 - discount/100)"
        tree = ast.parse(expression)
        return eval(compile(tree, '<expr>', 'eval'), context)
```

### Livello 4: Evolutionary Code

```python
class EvolutionaryOptimizer:
    def evolve(self, generations=50):
        # Algoritmi genetici per ottimizzazione parametri
        # Es: TTL cache ottimale, dimensioni pool connessioni
        pass
```

---

## Builder Engine

Il Builder genera automaticamente moduli da template YAML/JSON.

### Flusso

```
Template YAML ──► Parser ──► Validator ──► Generator ──► Migrator ──► Module
                                              └─► Registrar
```

### Esempio Template

```yaml
name: Sales
version: 1.0.0

entities:
  - name: SalesOrder
    fields:
      - name: codice
        type: string
        required: true
      - name: totale
        type: decimal
      - name: stato
        type: select
        options: [bozza, confermato, evaso]

api:
  prefix: /sales
  pagination: true

hooks:
  - event: order.before_create
    action: validate_stock
```

### Componenti

| Componente | Funzione |
|-----------|----------|
| **TemplateParser** | Valida e parse template YAML/JSON |
| **SchemaMigrator** | Crea/modifica tabelle DB |
| **CodeGenerator** | Genera classi Python, API, schemi |
| **ModuleRegistrar** | Registra moduli nel sistema |

---

## Stack Tecnologico

| Componente | Tecnologia |
|------------|------------|
| Framework | Flask 2.x / 3.x |
| API | Flask-smorest |
| ORM | SQLAlchemy |
| Database | PostgreSQL 14+ |
| Auth | Flask-JWT-Extended |
| Cache | Redis |
| Frontend | React 19 + Ant Design |
| Testing Core | Vitest + RTL |
| Testing Moduli | Playwright |
| Personalizzazione | Ant Design ConfigProvider |

### Struttura Directory

```
flaskERP/
├── app/                    # Configurazione Flask
├── backend/
│   ├── entities/          # Entità core
│   ├── composition/       # Block, Container, Robot
│   ├── builder/           # Builder Engine
│   ├── core/              # Testing Engine, Auth
│   ├── services/          # Business Logic
│   └── plugins/           # Plugin sistema
├── frontend/              # React SPA
│   ├── src/
│   │   ├── components/    # Componenti atomici e generici
│   │   ├── context/       # Auth e Theme Context
│   │   ├── pages/         # Pagine principali
│   │   └── utils.js       # API fetcher e utility centralizzate
├── migrations/            # DB migrations
└── docs/                  # Documentazione
```

---

## Sistema di Personalizzazione (Theming)

FlaskERP utilizza un approccio **Design-Driven** per permettere la personalizzazione visuale per-progetto.

1. **Persistenza**: Le impostazioni estetiche (`primary_color`, `border_radius`, `theme_mode`) sono salvate nel database nel modello `Project`.
2. **Distribuzione**: Il `ThemeContext` React carica queste impostazioni tramite API all'avvio o al cambio progetto.
3. **Applicazione**: Utilizzando il `ConfigProvider` di Ant Design, i token di stile vengono iniettati globalmente nel DOM, aggiornando istantaneamente l'interfaccia senza ricaricare la pagina.

---

## Qualità e Strategia di Test

Il sistema adotta una **Piramide dei Test** adattata ad un ambiente low-code:

- **Base (Unit Tests)**: Vitest verifica le funzioni pure, le utility e i componenti UI standard nel frontend.
- **Centro (Integration)**: Test API Flask verificano la correttezza dei controller e dell'isolamento tenant.
- **Cima (E2E/Module)**: Playwright esegue test funzionali completi sui moduli generati dal Builder, simulando l'interazione utente reale e catturando screenshot per i report.

---

*Documento aggiornato: Febbraio 2026*
