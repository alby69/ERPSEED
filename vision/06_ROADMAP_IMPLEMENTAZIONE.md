# ERPE: Roadmap di Implementazione

## Introduzione

Questa roadmap traduce la visione in un **piano di implementazione concreto** e realizzabile. Ogni fase costruisce sulle precedenti, introducendo complessità gradualmente.

---

## Panoramica delle Fasi

```
┌─────────────────────────────────────────────────────────────────────┐
│                         ROADMAP ERPE                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  FASE 1: FONDAMENTA          (Settimane 1-2)                        │
│  ├── Refactoring entità core                                        │
│  ├── Sistema ruoli avanzato                                         │
│  └── Indirizzi geografici                                           │
│                                                                     │
│  FASE 2: COMPOSIZIONE         (Settimane 3-4)                       │
│  ├── Block Registry                                                 │
│  ├── Container System                                               │
│  └── Robot/Module System                                            │
│                                                                     │
│  FASE 3: BUILDER          (Settimane 5-8)                           │
│  ├── Template Parser                                                │
│  ├── Code Generator                                                 │
│  ├── Schema Migrator                                                │
│  └── UI Builder                                                     │
│                                                                     │
│  FASE 4: CODE-AS-DATA       (Settimane 9-12)                        │
│  ├── Expression Engine                                              │
│  ├── Hook System                                                    │
│  ├── Hot Reload                                                     │
│  └── Adaptive Modules                                               │
│                                                                     │
│  FASE 5: EVOLUZIONE          (Settimane 13+)                        │
│  ├── Telemetry                                                      │
│  ├── Auto-optimization                                              │
│  └── Evolutionary Algorithms                                        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Fase 1: Fondamenta

### Obiettivo
Implementare le **tabelle archetipiche** (mattoncini base) che saranno il fondamento di tutto il sistema.

### Deliverable

#### 1.1 Refactoring Soggetto → Soggetto + Ruolo + Indirizzo

**Modelli da creare/modificare:**

```
Soggetto (Party)              → Core entity
  ├── Ruolo (Role)            → Lista ruoli
  │   └── SoggettoRuolo       → Associazione N:N
  ├── Indirizzo (Address)     → Value object geografico
  │   └── SoggettoIndirizzo   → Associazione N:N
  └── Contatto (Contact)      → Canali comunicazione
      └── SoggettoContatto    → Associazione N:N
```

**Codice da implementare:**
- `backend/entities/soggetto.py` - Entity Soggetto
- `backend/entities/ruolo.py` - Entity Ruolo
- `backend/entities/indirizzo.py` - Entity Indirizzo
- `backend/entities/contatto.py` - Entity Contatto
- Relazioni many-to-many

#### 1.2 Sistema Ruoli Avanzato

**Features:**
- Ruoli predefiniti: Cliente, Fornitore, Dipendente, Autista, Consulente
- Ruoli personalizzabili (creazione nuovi ruoli)
- Stati ruoli: attivo, sospeso, terminato
- Parametri specifici per ruolo (JSON)

#### 1.3 Sistema Indirizzi con Geolocalizzazione

**Features:**
- Campi: latitudine, longitudine
- Geocoding automatico (opzionale)
- Tipi: residenza, sede legale, magazzino, etc.
- Indirizzo formattato

### Tempo Stimato
**2 settimane**

---

## Fase 2: Sistema di Composizione

### Obiettivo
Costruire l'infrastruttura che permette ai mattoncini di **aggregarsi** in strutture più grandi.

### Deliverable

#### 2.1 Block Registry

```python
# Sistema di registrazione mattoncini
class BlockRegistry:
    """Registro centrale di tutti i blocchi"""
    _blocks: dict[str, Block] = {}
    
    @classmethod
    def register(cls, block_class: type):
        instance = block_class()
        cls._blocks[instance.name] = instance
    
    @classmethod
    def get(cls, name: str) -> Block:
        return cls._blocks.get(name)
    
    @classmethod
    def all(cls) -> list[Block]:
        return list(cls._blocks.values())
```

#### 2.2 Container System

```python
class Container:
    """Aggregatore di blocchi"""
    name: str
    blocks: list[Block]
    api_prefix: str
    
    def get_routes(self) -> list[Route]: ...
    def get_hooks(self) -> dict[str, callable]: ...
```

#### 2.3 Module/Robot System

```python
class Robot:
    """Modulo funzionale completo"""
    name: str
    containers: list[Container]
    
    def get_all_routes(self) -> list[Route]: ...
    def install(self, app): ...
    def uninstall(self): ...
```

### Tempo Stimato
**2 settimane**

---

## Fase 3: Builder Engine

### Obiettivo
Creare il sistema che genera **codice automaticamente** da template JSON/YAML.

### Deliverable

#### 3.1 Template Parser

```python
class TemplateParser:
    def parse(self, template_data: dict) -> ModuleTemplate: ...
    def validate(self, template: ModuleTemplate) -> list[str]: ...
```

#### 3.2 Code Generator

```python
class CodeGenerator:
    def generate_model(self, entity: EntityDefinition) -> str: ...
    def generate_api(self, entity: EntityDefinition) -> str: ...
    def generate_module(self, template: ModuleTemplate) -> Module: ...
```

#### 3.3 Schema Migrator

```python
class SchemaMigrator:
    def create_table(self, entity: EntityDefinition): ...
    def migrate_table(self, entity: EntityDefinition): ...
```

#### 3.4 Module Registrar

```python
class ModuleRegistrar:
    def register(self, module: Module): ...
    def unregister(self, module_name: str): ...
```

#### 3.5 Builder UI

Estensione dell'interfaccia attuale per permettere:
- Creazione guidata entità
- Definizione relazioni
- Configurazione container
- Definizione hook

### Tempo Stimato
**4 settimane**

---

## Fase 4: Code-as-Data (Programmazione Adattiva)

### Obiettivo
Implementare le funzionalità che permettono al codice di **adattarsi dinamicamente**.

### Deliverable

#### 4.1 Expression Engine

```python
class ExpressionEngine:
    def evaluate(self, expression: str, context: dict) -> any: ...
    
# Usage
engine = ExpressionEngine()
result = engine.evaluate("quantity * price * (1 - discount)", 
                         {'quantity': 10, 'price': 100, 'discount': 0.2})
# result = 800
```

#### 4.2 Hook System

```python
# Sistema di eventi/hook
class HookManager:
    def register(self, event: str, callback: callable): ...
    def trigger(self, event: str, *args, **kwargs): ...
    
# Hook disponibili
# - entity:before_create
# - entity:after_create
# - entity:before_update
# - entity:after_update
# - entity:before_delete
# - entity:after_delete
```

#### 4.3 Hot Reload

```python
class HotReloader:
    def watch(self, module_path: str): ...
    def reload(self, module_name: str): ...
    def auto_reload(self): ...
```

#### 4.4 Adaptive Modules

Moduli che possono essere modificati a runtime senza riavvio.

### Tempo Stimato
**4 settimane**

---

## Fase 5: Evoluzione (Opzionale)

### Obiettivo
Implementare funzionalità avanzate di auto-ottimizzazione.

### Deliverable

#### 5.1 Telemetry

```python
class Telemetry:
    """Raccoglie metriche di utilizzo"""
    def track(self, event: str, data: dict): ...
    def get_stats(self) -> dict: ...
    
# Metriche:
# - Tempo risposta API
# - Utilizzo risorse
# - Errori
# - Pattern di utilizzo
```

#### 5.2 Auto-Optimization

```python
class AutoOptimizer:
    """Ottimizza parametri automaticamente"""
    def analyze(self): ...
    def optimize(self): ...
    
# Ottimizzazioni:
# - Cache TTL
# - Query parameters
# - Connection pooling
```

#### 5.3 Evolutionary Algorithms

```python
class GeneticOptimizer:
    """Algoritmi genetici per ottimizzazione"""
    def evolve(self, objective: callable, generations: int): ...
```

### Tempo Stimato
**4+ settimane** (opzionale)

---

## Dipendenze tra Fasi

```
FASE 1 (Fondamenta)
    │
    └──────► FASE 2 (Composizione)
                │
                └──────► FASE 3 (Builder)
                            │
                            └──────► FASE 4 (Code-as-Data)
                                            │
                                            └──────► FASE 5 (Evoluzione)
```

**Nota:** Ogni fase dipende dalla precedente. Non puoi costruire il Builder senza le entità base.

---

## Criteri di Successo

### Fase 1 - Fondamenta
- [x] Soggetto con ruoli multipli funzionante
- [x] Indirizzo con geolocalizzazione
- [x] Query che sfruttano le nuove relazioni

### Fase 2 - Composizione
- [x] Block Registry funzionante
- [x] Container che aggrega blocchi
- [x] Robot che espone API unificate

### Fase 3 - Builder
- [x] Parser che valida template
- [x] Generatore che produce codice
- [x] Migrator che crea tabelle
- [x] UI per creazione template

### Fase 4 - Code-as-Data
- [x] Expression Engine funzionante
- [x] Hook che rispondono a eventi
- [x] Hot reload moduli
- [x] Moduli adattivi

### Fase 5 - Evoluzione
- [x] Telemetry raccoglie dati
- [x] Auto-optimizer modifica parametri
- [x] Genetic algorithms ottimizzano

---

## Stato Implementazione (19 Febbraio 2026)

### Completato ✅
| Fase | Descrizione | File |
|------|-------------|------|
| 1 | Entity Soggetto | `backend/entities/soggetto.py` |
| 1 | Entity Ruolo | `backend/entities/ruolo.py` |
| 1 | Entity Indirizzo | `backend/entities/indirizzo.py` |
| 1 | Entity Contatto | `backend/entities/contatto.py` |
| 1 | API REST per entità | `backend/entities/routes.py` |
| 2 | Block Registry | `backend/composition/registry.py` |
| 2 | Container System | `backend/composition/container.py` |
| 2 | Robot/Module | `backend/composition/robot.py` |
| 3 | Builder Engine | `backend/builder/__init__.py` |
| 3 | Code Generator | `backend/builder/generator.py` |
| 4 | Expression Engine | `backend/composition/expression.py` |
| 4 | Hook System | `backend/composition/hooks.py` |
| 4 | Hot Reload | `backend/composition/hot_reload.py` |
| 5 | Telemetry | `backend/evolution/telemetry.py` |
| 5 | Optimizer | `backend/evolution/optimizer.py` |
| 5 | Genetic | `backend/evolution/genetic.py` |

### Frontend - Pagine Create
| Pagina | Route | File |
|--------|-------|------|
| SoggettiPage | `/anagrafiche` | `frontend/src/pages/SoggettiPage.jsx` |
| RuoliPage | `/ruoli` | `frontend/src/pages/RuoliPage.jsx` |
| IndirizziPage | `/indirizzi` | `frontend/src/pages/IndirizziPage.jsx` |
| ContattiPage | `/contatti` | `frontend/src/pages/ContattiPage.jsx` |

### Sistema Preservato
- Parties, Products, Sales, Purchases (esistenti)
- Projects, Builder (esistenti)
- Multi-tenant (funzionante)

### Prossime Attività
1. Testare le nuove pagine frontend
2. Integrare TenantMember (nuovo modello User-Tenant)
3. Eliminare gradualmente codice vecchio (Parties → Soggetto)

---

## Suggerimenti Implementativi

### 1. Integra con l'Esistente

Non riscrivere tutto. Utilizza il codice esistente:

```python
# Il tuo Party attuale può diventare Soggetto
from backend.models import Party as Soggetto

# Aggiungi i nuovi campi
class Soggetto(Party):
    # Nuovi campi e relazioni
    ruoli = relationship(...)
```

### 2. Testa Ogni Fase

```bash
# Test Fase 1
pytest tests/entities/test_soggetto.py
pytest tests/entities/test_ruolo.py
pytest tests/entities/test_indirizzo.py

# Test Fase 2  
pytest tests/composition/test_registry.py
pytest tests/composition/test_container.py

# Test Fase 3
pytest tests/builder/test_parser.py
pytest tests/builder/test_generator.py
```

### 3. Documenta Man Mano

Ogni deliverable dovrebbe includere:
- Docstring dei moduli
- README della feature
- Esempi di utilizzo

### 4. Versiona i Template

I template sono codice! Versionali con Git.

```
templates/
├── fleet/
│   ├── v1.0.0.yaml
│   ├── v1.1.0.yaml
│   └── v2.0.0.yaml
├── crm/
│   └── v1.0.0.yaml
└── warehouse/
    └── v1.0.0.yaml
```

---

## Risorse Necessarie

### Conoscenze
- SQLAlchemy (deep)
- Flask/Blueprint
- Design Patterns (Factory, Registry, Plugin)
- Metaprogramming Python
- PostgreSQL

### Strumenti
- PostgreSQL
- Redis (per caching/telemetry)
- Docker
- CI/CD

---

## Conclusione

Questa roadmap ti porta da:
- **Oggi**: Sistema ERP con entità base
- **A 12 settimane**: Sistema ERP completamente modulare con Builder

Il risultato finale sarà un sistema dove:
1. Aggiungi nuove funzionalità senza toccare il core
2. Generi interi moduli da template JSON
3. Il codice si adatta alle esigenze dinamicamente
4. Ogni componente è testabile e sostituibile

---

## Prossimi Passi Immediati

1. **Scegliere il primo blocco da implementare** (Soggetto, Indirizzo, Ruolo)
2. **Creare i primi test** per validare il design
3. **Implementare Fase 1** (2 settimane)
4. **Verificare** che tutto funziona
5. **Procedere a Fase 2**

---

*Questa roadmap è living document - verrà aggiornata man mano che procediamo con l'implementazione.*
