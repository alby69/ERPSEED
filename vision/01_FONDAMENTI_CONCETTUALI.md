# ERPE: Fondamenti Concettuali

## I Quattro Pilastri dell'ERP Evolutivo

Questo documento esplora i quattro concetti fondamentali che guidano l'architettura di ERPE, spiegandoli in modo accessibile e collegandoli al tuo progetto.

---

## 1. Domain-Driven Design (DDD)

### Cos'è
Il DDD è un approccio allo sviluppo software che pone il **dominio del problema** (il business che vuoi gestire) al centro dell'architettura. Invece di pensare "cosa deve fare il database", pensi "quali sono le entità del mio business e come si relazionano".

### Concetti Chiave

#### Entity (Entità)
Un oggetto con un'identità propria che lo distingue da tutti gli altri, anche se ha gli stessi attributi.

```python
# Esempio: Due clienti possono avere lo stesso nome, 
# ma sono entità diverse con ID diverso
class Party:
    id = 1, name = "Mario Rossi"
    id = 2, name = "Mario Rossi"  # Sono persone diverse!
```

#### Value Object
Un oggetto descritto dai suoi attributi, senza identità propria. Due value object con gli stessi attributi sono considerati uguali.

```python
# Esempio: Indirizzo è un Value Object
# Via Roma 1, Milano è lo stesso indirizzo 
# indipendentemente da quale soggetto appartiene
class Address:
    street = "Via Roma"
    city = "Milano"
    # Non ha ID, conta solo il valore
```

#### Aggregate
Un gruppo di oggetti trattati come una singola unità. Un Aggregate Root gestisce l'accesso a tutti gli oggetti interni.

```python
# Esempio: SalesOrder è l'Aggregate Root
# Le linee non possono esistere senza l'ordine
class SalesOrder:
    id = 1
    lines = [SalesOrderLine, SalesOrderLine]  # Accessibili solo tramite Order

class SalesOrderLine:
    # Non ha senso существова da solo
    # Deve sempre appartenere a un Order
```

#### Repository
Un'interfaccia che astrae l'accesso ai dati. Il codice business non sa se i dati vengono da DB, file, o API esterna.

### Come si applica al tuo ERPE

La tua idea dei **mattoncini** è perfettamente allineata al DDD:

```
Domain (Business)
    │
    ├── Soggetto (Entity)      ← Identità, ha ruoli multipli
    ├── Indirizzo (Value Object) ← Solo valori, riutilizzabile
    ├── Testata+Riga (Aggregate) ← Unità transazionale
    └── Modulo (Bounded Context) ← Dominio delimitato
```

**Vantaggio per ERPE**: Il DDD ti permette di modellare il business reale con oggetti che riflettono la realtà, non la struttura del database.

---

## 2. Plugin Architecture

### Cos'è
Un pattern architetturale che permette di aggiungere funzionalità a un sistema **senza modificare il codice esistente**. I plugin sono moduli indipendenti che si "agganciano" al sistema principale attraverso interfacce definite.

### Concetti Chiave

#### Interface/Contract
Un accordo su come un plugin deve comunicare con il sistema. Il plugin deve rispettare il contratto, ma può implementarlo come vuole.

```python
# Esempio: Interfaccia per un plugin ERPE
class PluginInterface:
    def get_name(self) -> str: pass
    def get_version(self) -> str: pass
    def install(self, app): pass
    def uninstall(self): pass
    def get_routes(self) -> list: pass  # API routes che espone

# Il plugin deve rispettare questa interfaccia
class AccountingPlugin(PluginInterface):
    def get_name(self): return "accounting"
    # ... implementazione specifica
```

#### Dependency Injection
Il sistema principale "inietta" le dipendenze (servizi, database, configurazione) nei plugin, invece che i plugin le cerchino.

```python
# Il sistema passa tutto ciò che il plugin potrebbe servire
def install(self, app, db, config):
    self.db = db  # Il plugin riceve il DB
    self.config = config  # Riceve la config
```

#### Service Locator / Registry
Un registro centrale che tiene traccia di tutti i plugin disponibili e permette di trovarli.

```python
# Registry centrale
class PluginRegistry:
    _plugins = {}
    
    @classmethod
    def register(cls, plugin):
        cls._plugins[plugin.get_name()] = plugin
    
    @classmethod
    def get(cls, name):
        return cls._plugins.get(name)
    
    @classmethod
    def all(cls):
        return cls._plugins.values()
```

### Come si applica al tuo ERPE

La tua metafora dei **mattoncini** e **robot** è esattamente la Plugin Architecture:

```
ERPE Core (Sistema Principale)
    │
    ├── PluginRegistry ← Il registro che tiene traccia di tutto
    │
    ├── Plugin: Sales
    │   ├── Blocks: [Order, Customer, Product]
    │   ├── API: /sales/*
    │   └── Hooks: [on_order_created, on_invoice_sent]
    │
    ├── Plugin: Warehouse  
    │   ├── Blocks: [Location, Stock, Movement]
    │   ├── API: /warehouse/*
    │   └── Hooks: [on_stock_low, on_movement_created]
    │
    └── Plugin: Custom (generato dal Builder)
        ├── Blocks: [CustomEntity1, ...]
        ├── API: /custom/*
        └── Hooks: [user_defined]
```

**Vantaggio per ERPE**: 
- Aggiungere funzionalità senza toccare il core
- Sostituire un plugin senza rompere il sistema
- Sviluppo parallelo di moduli indipendenti

---

## 3. Metaprogramming

### Cos'è
La **programmazione che manipola programmi**. Invece di scrivere codice statico, scrivi codice che genera, modifica, o analizza altro codice.

### Tecniche Principali

#### A) type() - Creazione Dinamica di Classi
Puoi creare classi a runtime basandoti su configurazioni.

```python
# Creare una classe "al volo" basata su configurazione
def create_entity_class(config):
    """
    config = {
        'name': 'Vehicle',
        'fields': ['plate', 'brand', 'model']
    }
    """
    attributes = {
        '__tablename__': config['name'].lower() + 's',
        'id': Column(Integer, primary_key=True)
    }
    
    # Aggiungi i campi dinamicamente
    for field in config['fields']:
        attributes[field] = Column(String(100))
    
    # Crea la classe
    return type(config['name'], (Base,), attributes)

# Usage
Vehicle = create_entity_class({
    'name': 'Vehicle',
    'fields': ['plate', 'brand', 'model']
})

# Ora puoi usare Vehicle come una classe normale!
v = Vehicle(plate="AB123CD", brand="Ford", model="Fiesta")
```

#### B) Metaclasses - Il DNA delle Classi
Una metaclass è una classe che definisce come altre classi vengono create.

```python
# Metaclass che aggiunge automaticamente timestamps
class TimestampedMeta(type):
    def __new__(cls, name, bases, attrs):
        # Aggiungi created_at e updated_at a ogni classe
        attrs['created_at'] = Column(DateTime, default=datetime.utcnow)
        attrs['updated_at'] = Column(DateTime, onupdate=datetime.utcnow)
        return super().__new__(cls, name, bases, attrs)

# Uso: tutte le classi con questa metaclass hanno i timestamp
class AnyEntity(metaclass=TimestampedMeta):
    pass  # Ha già created_at e updated_at!

class Party(metaclass=TimestampedMeta):
    name = Column(String)  # Ha già timestamps!
```

#### C) Decorators - Comportamenti Trasversali
Funzioni che modificano altre funzioni o metodi.

```python
# Decorator che aggiunge logging automatico
def log_calls(func):
    def wrapper(*args, **kwargs):
        print(f"Chiamata a {func.__name__}")
        result = func(*args, **kwargs)
        print(f"Completato {func.__name__}")
        return result
    return wrapper

# Applica a un metodo
class OrderService:
    @log_calls
    def create_order(self, data):
        # Il logging è automatico
        pass
```

#### D) exec() / eval() - Esecuzione Codice Dinamico
Esegui stringhe come codice (usare con cautela!).

```python
# Eseguire una formula definita come stringa
formula = "quantity * unit_price * (1 - discount)"

# "Compila" la formula in codice eseguibile
code = compile(formula, '<string>', 'eval')
result = eval(code, {'quantity': 10, 'unit_price': 100, 'discount': 0.2})
# result = 800
```

### Come si applica al tuo ERPE

Il **Builder** che descrivi è pura metaprogrammazione:

```
Configurazione (JSON/YAML)
    │
    ▼
┌─────────────────────────────┐
│   BUILDER ENGINE           │
│   (Meta-programmatore)     │
├─────────────────────────────┤
│ 1. Legge configurazione    │
│ 2. Genera classi Python    │
│ 3. Crea tabelle DB         │
│ 4. Registra routes API    │
│ 5. Genera UI components    │
└─────────────────────────────┘
    │
    ▼
Codice Python eseguibile!
```

**Esempio pratico** - Il tuo Builder riceve:
```json
{
  "entity": "Vehicle",
  "fields": [
    {"name": "plate", "type": "string", "required": true},
    {"name": "driver", "type": "relation", "to": "Party"}
  ]
}
```

**Il Builder genera**:
```python
class Vehicle(BaseModel):
    __tablename__ = 'vehicles'
    
    plate = Column(String, nullable=False)
    driver_id = Column(Integer, ForeignKey('parties.id'))
    driver = relationship('Party')
    
    # Metodi CRUD generati automaticamente!
    def save(self): ...
    def delete(self): ...
```

**Vantaggio per ERPE**: Non scrivi più codice ripetitivo. Definisci cosa vuoi, il sistema genera come ottenerlo.

---

## 4. Self-Modifying Code (Codice Adattivo)

### Cos'è
Codice che può **modificare se stesso** durante l'esecuzione per adattarsi a nuove situazioni. Non è fantascienza: è usato in sistemi moderni.

### Pattern Principali

#### A) Hot Module Replacement (HMR)
Sostituisci parti del codice senza riavviare l'applicazione.

```python
# Sistema di hot-reload per ERPE
class ModuleReloader:
    def __init__(self):
        self.modules = {}
    
    def reload_module(self, module_name, new_code):
        """Ricarica un modulo con nuovo codice"""
        # 1. Compila il nuovo codice
        new_module = compile(new_code, module_name, 'exec')
        
        # 2. Esegui nel contesto del modulo esistente
        old_module = self.modules.get(module_name)
        if old_module:
            exec(new_module, old_module.__dict__)
        
        print(f"Modulo {module_name} ricaricato!")
```

#### B) Rule Engine
Sistema che valuta regole definite a runtime.

```python
# Regola definita in configurazione
rule = {
    "condition": "order.total > 1000",
    "action": "apply_discount",
    "params": {"discount": 0.10}
}

# Il motore valuta la regola
def evaluate_rule(rule, context):
    # "order.total > 1000" → codice eseguibile
    condition = compile(rule["condition"], '<rule>', 'eval')
    return eval(condition, context)

# Usage
context = {'order': Order(total=1500)}
if evaluate_rule(rule, context):
    apply_discount(0.10)  # Sconto applicato!
```

#### C) Plugin Hot-Loading
Carica e scarica plugin a runtime.

```python
class PluginLoader:
    def load_plugin(self, plugin_path):
        """Carica un plugin da file Python"""
        import importlib.util
        
        spec = importlib.util.spec_from_file_location("plugin", plugin_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # Carica!
        
        return module.Plugin()  # Istanzia
    
    def unload_plugin(self, plugin_name):
        """Scarica il plugin"""
        if plugin_name in sys.modules:
            del sys.modules[plugin_name]  # Rimuovi!
```

#### D) Schema Auto-Migration
Il database si adatta automaticamente allo schema.

```python
class AutoMigrator:
    def migrate_if_needed(self, model_class):
        """Aggiorna la tabella se il modello è cambiato"""
        current_columns = self.get_db_columns(model_class)
        model_columns = self.get_model_columns(model_class)
        
        # Trova colonne nuove
        new_columns = set(model_columns) - set(current_columns)
        
        for col in new_columns:
            self.add_column(model_class, col)
        
        # Trova colonne rimosse
        removed = set(current_columns) - set(model_columns)
        for col in removed:
            self.remove_column(model_class, col)
```

### Come si applica al tuo ERPE

La tua visione di **api che si evolvono** come l'alveare:

```
Situazione: Nuovo cliente chiede "Voglio gestire i miei mezzi"

Vecchio sistema: Sviluppatore scrive codice per 2 settimane

Sistema ERPE:
┌─────────────────────────────────────────┐
│ 1. Definisci template (5 minuti)        │
│    - Vehicle: targa, marca, modello...  │
│    - Driver: nome, licenza...           │
│    - Relationship: Vehicle→Driver        │
└─────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│ 2. Builder genera modulo (automatico)   │
│    - Classe Python creata               │
│    - Tabella DB creata                  │
│    - API registrata                    │
│    - UI generata                        │
└─────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│ 3. Il modulo è LIVE! (minuti)          │
│    - Usa subito il nuovo modulo         │
│    - Nessun riavvio server              │
│    - Nessun deployment                  │
└─────────────────────────────────────────┘
```

**Vantaggio per ERPE**: 
- Risposta immediata alle esigenze del business
- Nessun " ciclo di sviluppo lungo"
- Il sistema impara e si adatta

---

## Sintesi: Come si Integrano

```
                    ┌──────────────────────┐
                    │   ERPE (Astronave)   │
                    └──────────────────────┘
           ┌─────────────────┼─────────────────┐
           │                 │                 │
           ▼                 ▼                 ▼
    ┌────────────┐    ┌────────────┐    ┌────────────┐
    │    DDD     │    │  Plugin    │    │   Meta     │
    │ (Struttura)│◄──►│ (Mattoncini)│◄──►│(Costruttore)│
    └────────────┘    └────────────┘    └────────────┘
           │                 │                 │
           └─────────────────┼─────────────────┘
                             │
                             ▼
                    ┌──────────────────────┐
                    │   Self-Modifying      │
                    │   (Adattamento)      │
                    └──────────────────────┘
```

1. **DDD** ti dice *cosa* modellare (i concetti del business)
2. **Plugin Architecture** ti dice *come* organizzare* (moduli indipendenti)
3. **Metaprogramming** ti dice *come generare* (Builder automatico)
4. **Self-Modifying** ti dice *come evolvere* (adattamento runtime)

---

## Prossimi Passi

Vuoi che approfondisca uno specifico concetto con:
- Maggiori esempi di codice?
- Diagrammi architetturali?
- Un prototipo funzionante di una parte specifica?

O preferisci procedere a creare i documenti tecnici di implementazione basati su questa visione?
