# ERPE: Modello di Composizione

## Introduzione

Il Modello di Composizione definisce **come i mattoncini si aggregano** per formare strutture più complesse. È la traduzione tecnica della tua metafora: api → alveare.

---

## Gerarchia di Composizione

```
┌─────────────────────────────────────────────────────────────────┐
│                     ASTRONAVE (ERP COMPLETO)                    │
│                    Sistema ERP finito e funzionante             │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Interfacce Multiple (API Gateways)                     │    │
│  │  /api/v1/*  │  /external/*  │  /webhook/*  │  /admin/*  │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
           ▲                   ▲                    ▲
           │                   │                    │
    ┌──────┴──────┐     ┌──────┴──────┐      ┌──────┴──────┐
    │   ROBOT     │     │   ROBOT     │      │   ROBOT     │
    │  (Modulo)   │     │  (Modulo)   │      │  (Modulo)   │
    └─────────────┘     └─────────────┘      └─────────────┘
           │                   │                    │
           │    ┌──────────────┼───────────── ─┐    │
           │    │         CONTAINER            │    │
           │    │   (Aggregatore funzionale)   │    │
           │    │   ┌──────┐  ┌──────┐         │    │
           │    │   │MATTON│  │MATTON│         │    │
           │    │   │CINI  │  │CINI  │         │    │
           │    │   └──────┘  └──────┘         │    │
           │    └──────────────────────────────┘    │
           │                    │                   │
           ▼                    ▼                   ▼
    ┌──────────────────────────────────────────────────────────┐
    │              MATTONCINI (Entità Base)                   │
    │  Soggetto │ Indirizzo │ Testata │ Riga │ Valuta │ ...   │
    └──────────────────────────────────────────────────────────┘
```

---

## Definizione Formale

### Livello 1: Mattoncino (Block)

È l'unità atomica - un'entità con CRUD, validazione, e Hook.

```python
class Block(Protocol):
    """Protocollo che ogni mattoncino deve rispettare"""
    
    @property
    def name(self) -> str:
        """Nome identificativo del blocco"""
        ...
    
    @property
    def version(self) -> str:
        """Versione del blocco"""
        ...
    
    def get_model(self) -> type:
        """Restituisce il modello SQLAlchemy"""
        ...
    
    def get_api_routes(self) -> list[Route]:
        """Route API esposte dal blocco"""
        ...
    
    def get_hooks(self) -> dict[str, callable]:
        """Hook disponibili (before_create, after_save, etc.)"""
        ...
    
    def get_dependencies(self) -> list[str]:
        """Blocchi da cui dipende"""
        ...


class BlockRegistry:
    """Registro centrale di tutti i blocchi disponibili"""
    _blocks: dict[str, Block] = {}
    
    @classmethod
    def register(cls, block: Block):
        cls._blocks[block.name] = block
    
    @classmethod
    def get(cls, name: str) -> Block:
        return cls._blocks.get(name)
    
    @classmethod
    def all(cls) -> list[Block]:
        return list(cls._blocks.values())
```

### Livello 2: Container

Un container è un **aggregatore** che raggruppa blocchi correlati e fornisce un'interfaccia unificata.

```python
class Container:
    """Aggregatore di blocchi con interfaccia unificata"""
    
    def __init__(self, name: str, blocks: list[Block]):
        self.name = name
        self.blocks = {b.name: b for b in blocks}
        self._api_prefix = f"/{name}"
    
    @property
    def api_prefix(self) -> str:
        return self._api_prefix
    
    @api_prefix.setter
    def api_prefix(self, value: str):
        self._api_prefix = value
    
    def get_routes(self) -> list[Route]:
        """Raccoglie tutte le route dai blocchi"""
        routes = []
        for block in self.blocks.values():
            routes.extend(block.get_api_routes())
        return routes
    
    def get_hooks(self) -> dict[str, list[callable]]:
        """Raccoglie tutti gli hook dai blocchi"""
        hooks = {}
        for block in self.blocks.values():
            for name, callback in block.get_hooks().items():
                if name not in hooks:
                    hooks[name] = []
                hooks[name].append(callback)
        return hooks
    
    def call_hook(self, hook_name: str, *args, **kwargs):
        """Esegue tutti gli hook di un certo tipo"""
        for callback in self.get_hooks().get(hook_name, []):
            callback(*args, **kwargs)
```

### Livello 3: Robot (Module)

Un robot è un **modulo funzionale completo** con business logic. Può essere:
- Modulo predefinito (Vendite, Magazzino, Contabilità)
- Modulo generato dal Builder

```python
class Robot:
    """Modulo funzionale completo"""
    
    def __init__(self, name: str, containers: list[Container]):
        self.name = name
        self.containers = {c.name: c for c in containers}
        self._is_active = True
    
    def get_all_routes(self) -> list[Route]:
        """Tutte le route di tutti i container"""
        routes = []
        for container in self.containers.values():
            routes.extend(container.get_routes())
        return routes
    
    def get_all_hooks(self) -> dict[str, list[callable]]:
        """Tutti gli hook di tutti i container"""
        hooks = {}
        for container in self.containers.values():
            container_hooks = container.get_hooks()
            for name, callbacks in container_hooks.items():
                if name not in hooks:
                    hooks[name] = []
                hooks[name].extend(callbacks)
        return hooks
    
    def install(self, app):
        """Registra il robot nell'applicazione"""
        for route in self.get_all_routes():
            app.register_route(route)
    
    def uninstall(self):
        """Rimuove il robot dall'applicazione"""
        self._is_active = False
```

### Livello 4: Astronave (ERP)

L'astronave è l'**aggregatore finale** che orchestra tutti i robot.

```python
class Spaceship:
    """L'ERP completo - orchestratore di robot"""
    
    def __init__(self):
        self.robots: dict[str, Robot] = {}
        self.gateways: dict[str, APIGateway] = {}
    
    def register_robot(self, robot: Robot):
        """Registra un robot"""
        self.robots[robot.name] = robot
    
    def get_robot(self, name: str) -> Robot:
        """Ottiene un robot per nome"""
        return self.robots.get(name)
    
    def create_gateway(self, name: str, routes: list[Route]) -> APIGateway:
        """Crea un gateway API"""
        gateway = APIGateway(name, routes)
        self.gateways[name] = gateway
        return gateway
    
    def call_global_hook(self, hook_name: str, *args, **kwargs):
        """Esegue un hook su tutti i robot"""
        for robot in self.robots.values():
            robot.call_hook(hook_name, *args, **kwargs)
```

---

## Esempio Pratico: Ordini di Vendita

Vediamo come un ordine di vendita si costruisce dai mattoncini:

```
ROBOT: Sales (Vendite)
│
├─ CONTAINER: Orders (Gestione Ordini)
│  ├─ MATTONCINO: Soggetto (anagrafica cliente)
│  ├─ MATTONCINO: Prodotto (articoli)
│  ├─ MATTONCINO: Testata (testata ordine)
│  ├─ MATTONCINO: Riga (righe ordine)
│  └─ MATTONCINO: Valuta (prezzi in valuta)
│
├─ CONTAINER: Pricing (Listini)
│  ├─ MATTONCINO: Listino
│  └─ MATTONCINO: Sconto
│
└─ CONTAINER: Workflow (Processi)
   ├─ MATTONCINO: Stato
   └─ MATTONCINO: Transizione
```

### Implementazione dell'Esempio

```python
# Definizione dei mattoncini
class SoggettoBlock:
    name = "soggetto"
    version = "1.0.0"
    
    def get_model(self):
        return Soggetto
    
    def get_api_routes(self):
        return [
            Route('/soggetti', 'GET', self.list),
            Route('/soggetti', 'POST', self.create),
            Route('/soggetti/<id>', 'GET', self.get),
            Route('/soggetti/<id>', 'PUT', self.update),
            Route('/soggetti/<id>', 'DELETE', self.delete),
        ]
    
    def get_hooks(self):
        return {
            'after_create': self._after_create,
            'before_delete': self._before_delete,
        }
    
    def get_dependencies(self):
        return []  # Nessuna dipendenza


class TestataBlock:
    name = "testata"
    version = "1.0.0"
    
    def get_model(self):
        return Testata
    
    def get_dependencies(self):
        return ['soggetto']  # Dipende da Soggetto


# Composizione del Container
orders_container = Container(
    name="orders",
    blocks=[
        SoggettoBlock(),
        TestataBlock(),
        RigaBlock(),
        ProdottoBlock(),
    ]
)

# Composizione del Robot
sales_robot = Robot(
    name="sales",
    containers=[
        orders_container,
        pricing_container,
        workflow_container,
    ]
)

# Registrazione nell'Astronave
spaceship = Spaceship()
spaceship.register_robot(sales_robot)
```

---

## Sistema di Interfacce (API)

Ogni livello espone **due tipi di interfacce**:

### Interfaccia Interna
Per la comunicazione tra componenti dello stesso robot/container.

```python
# Esempio: Il container Orders chiama il container Pricing
class OrdersContainer(Container):
    def calculate_price(self, product_id, quantity, list_id):
        # Chiama il container Pricing internamente
        pricing = self.robot.get_container('pricing')
        return pricing.calculate(product_id, quantity, list_id)
```

### Interfaccia Esterna
Per la comunicazione tra robot diversi o con l'esterno.

```python
# Route esposta esternamente
@router.post('/api/v1/orders')
def create_order(data: OrderCreate):
    # Il robot sales gestisce la richiesta
    return sales_robot.handle('orders.create', data)
```

---

## Hook System (Punti di Aggancio)

Gli hook permettono ai componenti di **reagire agli eventi** senza accoppiamento diretto.

```python
# Definizione hook disponibili
HOOK_TYPES = {
    # Entity hooks
    'before_create': 'Prima della creazione',
    'after_create': 'Dopo la creazione',
    'before_update': 'Prima dell\'aggiornamento',
    'after_update': 'Dopo l\'aggiornamento',
    'before_delete': 'Prima della cancellazione',
    'after_delete': 'Dopo la cancellazione',
    
    # Container hooks
    'on_init': 'All\'inizializzazione',
    'on_destroy': 'Alla distruzione',
    
    # Robot hooks
    'on_install': 'All\'installazione',
    'on_uninstall': 'Alla disinstallazione',
}

# Esempio: Hook per gestione magazzino
class InventoryHook:
    """Hook che aggiorna il magazzino quando viene creato un ordine"""
    
    def after_create(self, order):
        """Dopo la creazione dell'ordine, scarica il magazzino"""
        for line in order.lines:
            inventory.decrement(line.product_id, line.quantity)
```

---

## Event Bus (Comunicazione Asincrona)

Per comunicazione più complessa tra robot:

```python
class EventBus:
    """Bus eventi per comunicazione asincrona tra componenti"""
    
    _handlers: dict[str, list[callable]] = {}
    
    @classmethod
    def subscribe(cls, event_type: str, handler: callable):
        if event_type not in cls._handlers:
            cls._handlers[event_type] = []
        cls._handlers[event_type].append(handler)
    
    @classmethod
    def publish(cls, event_type: str, data: dict):
        for handler in cls._handlers.get(event_type, []):
            handler(data)


# Uso
EventBus.subscribe('order.created', notify_sales_team)
EventBus.subscribe('order.created', update_inventory)
EventBus.subscribe('order.created', create_accounting_entry)

# Pubblicazione evento
EventBus.publish('order.created', {'order_id': 123, 'customer_id': 456})
```

---

## Configurazione del Sistema

La configurazione può essere definita in YAML/JSON:

```yaml
# config/erp_config.yml
spaceship:
  name: "ERPE Production"
  
  robots:
    - name: sales
      containers:
        - name: orders
          blocks:
            - soggetto
            - testata
            - riga
            - prodotto
          api_prefix: /api/v1/orders
          
        - name: pricing
          blocks:
            - listino
            - sconto
          api_prefix: /api/v1/pricing
          
    - name: warehouse
      containers:
        - name: stock
          blocks:
            - location
            - inventory
          api_prefix: /api/v1/warehouse
    
    - name: accounting
      containers:
        - name: general_ledger
          blocks:
            - conto
            - movcon
          api_prefix: /api/v1/accounting
  
  gateways:
    - name: external
      routes: /api/v1/*
      auth: api_key
      
    - name: internal
      routes: /internal/*
      auth: service_account
      
    - name: webhook
      routes: /webhook/*
      auth: hmac
```

---

## Vantaggi del Modello

| Aspetto | Benefici |
|---------|----------|
| **Composizione** | Mattoncini riutilizzabili in più contesti |
| **Isolamento** | Un container non conosce i dettagli degli altri |
| **Estensibilità** | Aggiungi container senza modificare esistenti |
| **Sostituibilità** | Sostituisci un container con versione diversa |
| **Testabilità** | Testa ogni livello in isolamento |
| **Parallelismo** | Sviluppo parallelo di container/robot |

---

## Prossimi Passi

1. Implementare il `BlockRegistry` e il sistema di container
2. Definire la classe base `Block` con i metodi richiesti
3. Creare il sistema di Event Bus
4. Implementare il sistema di Hook
5. Creare la configurazione YAML per la composizione
6. Testare la composizione di un robot di esempio
