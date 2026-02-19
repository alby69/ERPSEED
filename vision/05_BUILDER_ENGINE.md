# ERPE: Builder Engine

## Introduzione

Il **Builder** è il cuore della tua visione:
un sistema che riceve **template** (descrizioni di cosa vuoi) e genera **codice eseguibile** (moduli pronti all'uso).

È come un impianto di produzione:
- **Input**: Disegni tecnici (template JSON/YAML)
- **Output**: Prodotti finiti (moduli Python funzionanti)

---

## Architettura del Builder

```
┌─────────────────────────────────────────────────────────────────┐
│                         BUILDER ENGINE                          │
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │   TEMPLATE   │───▶│  PARSER      │───▶│  VALIDATOR   │       │
│  │  (Input)     │    │  (Analizza)  │    │  (Verifica)  │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│                                                   │             │
│  ┌──────────────┐    ┌──────────────┐             │             │
│  │   OUTPUT     │◀───│  GENERATOR   │◀────────────┘             │
│  │  (Modulo)    │    │  (Produce)   │                           │
│  └──────────────┘    └──────────────┘                           │
│         │                   │                                   │
│         │     ┌─────────────┴─────────────┐                     │
│         │     │      MIGRATOR             │                     │
│         │     │  (Schema DB)              │                     │
│         │     └───────────────────────────┘                     │
│         │                   │                                   │
│         │     ┌─────────────┴─────────────┐                     │
│         │     │    REGISTRAR              │                     │
│         │     │  (Registra in ERPE)       │                     │
│         │     └───────────────────────────┘                     │
│         ▼                                                       ▼
│  ┌──────────────┐                                    ┌──────────┐
│  │   MODULO     │                                    │  API     │
│  │  PRONTO!     │                                    │  PRONTE! │
│  └──────────────┘                                    └──────────┘
└─────────────────────────────────────────────────────────────────┘
```

---

## Formato Template

### Struttura Principale

```yaml
# Esempio: Template per Gestione Flotte
module:
  name: fleet_management
  version: 1.0.0
  description: Gestione mezzi aziendali e autisti
  
# Entità (mattoncini)
entities:
  - name: Veicolo
    table: veicoli
    fields:
      - name: targa
        type: string
        required: true
        unique: true
        
      - name: marca
        type: string
        required: true
        
      - name: modello
        type: string
        
      - name: anno_immatricolazione
        type: integer
        
      - name: chilometraggio
        type: integer
        default: 0
        
      - name: stato
        type: select
        options: [attivo, manutenzione, dismissione]
        default: attivo
        
    relationships:
      - name: proprietario
        type: many-to-one
        target: Soggetto
        required: true
        
      - name: autisti
        type: many-to-many
        target: Soggetto
        through: VeicoloAutista
        
  - name: Viaggio
    fields:
      - name: veicolo_id
        type: integer
        
      - name: autista_id
        type: integer
        
      - name: data_partenza
        type: datetime
        
      - name: data_arrivo
        type: datetime
        
      - name: km_percorsi
        type: integer
        
      - name: origine
        type: string
        
      - name: destinazione
        type: string
        
# Container (aggregatori)
containers:
  - name: fleet_operations
    description: Operazioni di flotta
    entities: [Veicolo, Viaggio]
    api_prefix: /api/v1/fleet
    
  - name: vehicle_management
    description: Gestione veicoli
    entities: [Veicolo]
    api_prefix: /api/v1/vehicles

# Formule (logiche di business)
formulas:
  - name: costo_km
    entity: Viaggio
    expression: totale_spese / km_percorsi
    type: computed
    
  - name: stato_manutenzione
    entity: Veicolo
    expression: "attivo" if chilometraggio < 100000 else "manutenzione"
    type: conditional

# Hook (automazioni)
hooks:
  - event: Veicolo.before_create
    code: |
      if not args[0].targa:
          args[0].targa = generate_plate()
      
  - event: Viaggio.after_create
    code: |
      veicolo = Viaggio.veicolo
      veicolo.chilometraggio += Viaggio.km_percorsi
      db.session.commit()

# Permessi
permissions:
  - role: admin
    grants: [create, read, update, delete, *]
    
  - role: autista
    grants: 
      - entity: Viaggio
        actions: [create, read]
      - entity: Veicolo
        actions: [read]

# UI (configurazione interfaccia)
ui:
  Veicolo:
    list_view:
      columns: [targa, marca, modello, stato]
      search: [targa, marca]
      
    form_view:
      layout: [targa, marca, modello], [stato, chilometraggio]
      
  Viaggio:
    list_view:
      columns: [data_partenza, origine, destinazione, km_percorsi]
      
    kanban_view:
      status_field: stato
      columns: [programmato, in_corso, completato]
```

---

## Il Parser

```python
# ============================================================
# PARSER: Traduce YAML/JSON in strutture Python
# ============================================================

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict
from enum import Enum

class FieldType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    TEXT = "text"
    SELECT = "select"
    FILE = "file"
    RELATION = "relation"

class FieldDefinition(BaseModel):
    name: str
    type: FieldType
    required: bool = False
    unique: bool = False
    default: Optional[Any] = None
    options: Optional[List[str]] = None  # Per select
    relation: Optional[Dict] = None  # Per relazioni
    
class RelationshipDefinition(BaseModel):
    name: str
    type: str  # one-to-many, many-to-one, many-to-many
    target: str
    through: Optional[str] = None  # Per many-to-many

class EntityDefinition(BaseModel):
    name: str
    table: Optional[str] = None
    fields: List[FieldDefinition]
    relationships: List[RelationshipDefinition] = []
    
    @validator('table', always=True)
    def set_table_name(cls, v, values):
        return v or values.get('name', '').lower() + 's'

class ContainerDefinition(BaseModel):
    name: str
    description: Optional[str] = None
    entities: List[str]
    api_prefix: str

class FormulaDefinition(BaseModel):
    name: str
    entity: str
    expression: str
    type: str = "computed"  # computed, conditional, aggregate

class HookDefinition(BaseModel):
    event: str  # Entity.before_create, etc.
    code: str

class ModuleTemplate(BaseModel):
    name: str
    version: str = "1.0.0"
    description: Optional[str] = None
    entities: List[EntityDefinition]
    containers: List[ContainerDefinition] = []
    formulas: List[FormulaDefinition] = []
    hooks: List[HookDefinition] = []
    permissions: List[Dict] = []
    ui: Dict = {}

class TemplateParser:
    """Parser che traduce template in oggetti Python"""
    
    def parse(self, template_data: dict) -> ModuleTemplate:
        """Parse un template YAML/JSON in ModuleTemplate"""
        return ModuleTemplate(**template_data)
    
    def validate(self, template: ModuleTemplate) -> List[str]:
        """Valida il template e ritorna errori"""
        errors = []
        
        # Verifica che gli entity target esistano
        entity_names = {e.name for e in template.entities}
        
        for entity in template.entities:
            for rel in entity.relationships:
                if rel.target not in entity_names:
                    errors.append(
                        f"Relazione '{rel.name}' in {entity.name} "
                        f"referenzia '{rel.target}' che non esiste"
                    )
        
        # Verifica che le formule referenzino entity esistenti
        for formula in template.formulas:
            if formula.entity not in entity_names:
                errors.append(
                    f"Formula '{formula.name}' referenzia "
                    f"entity '{formula.entity}' che non esiste"
                )
        
        return errors
```

---

## Il Generatore

```python
# ============================================================
# GENERATOR: Produce codice Python dai template
# ============================================================

class CodeGenerator:
    """Genera codice Python da ModuleTemplate"""
    
    def __init__(self):
        self.type_mapping = {
            'string': 'db.Column(db.String(255))',
            'integer': 'db.Column(db.Integer)',
            'float': 'db.Column(db.Float)',
            'boolean': 'db.Column(db.Boolean)',
            'date': 'db.Column(db.Date)',
            'datetime': 'db.Column(db.DateTime)',
            'text': 'db.Column(db.Text)',
            'select': 'db.Column(db.String(50))',
        }
    
    def generate_model(self, entity: EntityDefinition) -> str:
        """Genera codice SQLAlchemy per un'entità"""
        
        lines = [
            f"class {entity.name}(BaseModel):",
            f'    __tablename__ = "{entity.table}"',
            "",
            "    # Campi",
        ]
        
        for field in entity.fields:
            col_def = self._generate_field(field)
            lines.append(f"    {field.name} = {col_def}")
        
        # Relazioni
        if entity.relationships:
            lines.append("")
            lines.append("    # Relazioni")
            
            for rel in entity.relationships:
                rel_def = self._generate_relationship(rel, entity.name)
                lines.append(f"    {rel_def}")
        
        # Metodo to_dict
        lines.extend([
            "",
            "    def to_dict(self):",
            "        return {",
            f"            '{entity.name.lower()}': self.__dict__",
            "        }",
        ])
        
        return "\n".join(lines)
    
    def _generate_field(self, field: FieldDefinition) -> str:
        """Genera definizione colonna"""
        col_type = self.type_mapping.get(field.type.value, 'db.Column(db.String(255))')
        
        opts = []
        if field.required:
            opts.append('nullable=False')
        if field.unique:
            opts.append('unique=True')
        if field.default is not None:
            default = field.default
            if isinstance(default, str):
                default = f"'{default}'"
            opts.append(f'default={default}')
        
        if opts:
            return f"{col_type}, {', '.join(opts)}"
        return col_type
    
    def _generate_relationship(self, rel: RelationshipDefinition, source: str) -> str:
        """Genera definizione relazione"""
        if rel.type == 'many-to-one':
            return f"{rel.name} = db.relationship('{rel.target}')"
        elif rel.type == 'one-to-many':
            return f"{rel.name}s = db.relationship('{rel.target}', back_populates='{source.lower()}')"
        elif rel.type == 'many-to-many':
            return f"{rel.name} = db.relationship('{rel.target}', secondary='{rel.through}')"
        return ""
    
    def generate_api(self, entity: EntityDefinition) -> str:
        """Genera codice API REST per un'entità"""
        
        name = entity.name.lower()
        
        return f'''
@{bp.route('/{name}', methods=['GET'])
def list_{name}():
    items = {entity.name}.query.all()
    return jsonify([i.to_dict() for i in items])

@{bp.route('/{name}', methods=['POST'])
def create_{name}():
    data = request.get_json()
    item = {entity.name}(**data)
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201

@{bp.route('/{name}/<int:id>', methods=['GET'])
def get_{name}(id):
    item = {entity.name}.query.get_or_404(id)
    return jsonify(item.to_dict())

@{bp.route('/{name}/<int:id>', methods=['PUT'])
def update_{name}(id):
    item = {entity.name}.query.get_or_404(id)
    data = request.get_json()
    for key, value in data.items():
        setattr(item, key, value)
    db.session.commit()
    return jsonify(item.to_dict())

@{bp.route('/{name}/<int:id>', methods=['DELETE'])
def delete_{name}(id):
    item = {entity.name}.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return '', 204
'''
    
    def generate_module(self, template: ModuleTemplate) -> Module:
        """Genera un modulo completo"""
        
        models_code = []
        api_code = []
        
        for entity in template.entities:
            models_code.append(self.generate_model(entity))
            api_code.append(self.generate_api(entity))
        
        return Module(
            name=template.name,
            version=template.version,
            models="\n\n".join(models_code),
            api="\n\n".join(api_code),
            containers=template.containers,
            formulas=template.formulas,
            hooks=template.hooks,
        )
```

---

## Il Migrator

```python
# ============================================================
# MIGRATOR: Gestisce lo schema del database
# ============================================================

class SchemaMigrator:
    """Gestisce migrazioni automatiche dello schema"""
    
    def __init__(self, db):
        self.db = db
    
    def create_table(self, entity: EntityDefinition):
        """Crea una tabella da definizione entity"""
        
        table_name = entity.table
        
        # Costruisci colonna
        columns = []
        for field in entity.fields:
            col = self._field_to_column(field)
            columns.append(col)
        
        # Crea la tabella
        if not self.db.engine.has_table(table_name):
            table = Table(table_name, *columns)
            table.create(self.db.engine)
            print(f"Creata tabella: {table_name}")
        else:
            self._migrate_table(entity)
    
    def _field_to_column(self, field: FieldDefinition) -> Column:
        """Converte FieldDefinition in Column SQLAlchemy"""
        
        type_map = {
            'string': String(255),
            'integer': Integer,
            'float': Float,
            'boolean': Boolean,
            'date': Date,
            'datetime': DateTime,
            'text': Text,
        }
        
        col_type = type_map.get(field.type.value, String(255))
        
        return Column(
            field.name,
            col_type,
            nullable=not field.required,
            unique=field.unique,
            default=field.default,
        )
    
    def _migrate_table(self, entity: EntityDefinition):
        """Migra tabella esistente (aggiunge colonne mancanti)"""
        
        table_name = entity.table
        inspector = inspect(self.db.engine)
        
        existing_columns = [c['name'] for c in inspector.get_columns(table_name)]
        entity_fields = {f.name for f in entity.fields}
        
        # Trova nuove colonne
        new_columns = entity_fields - set(existing_columns)
        
        for field_name in new_columns:
            field = next(f for f in entity.fields if f.name == field_name)
            col = self._field_to_column(field)
            
            # Aggiungi colonna
            with self.db.engine.begin() as conn:
                conn.execute(
                    text(f"ALTER TABLE {table_name} ADD COLUMN {field_name} ...")
                )
            
            print(f"Aggiunta colonna {field_name} a {table_name}")
    
    def migrate_all(self, template: ModuleTemplate):
        """Migra tutte le entità di un template"""
        
        for entity in template.entities:
            self.create_table(entity)
```

---

## Il Registrar

```python
# ============================================================
# REGISTRAR: Registra il modulo generato nel sistema ERPE
# ============================================================

class ModuleRegistrar:
    """Registra moduli generati nel sistema ERPE"""
    
    def __init__(self, app, module_registry):
        self.app = app
        self.module_registry = module_registry
    
    def register(self, module: Module, module_code: str):
        """Registra un modulo nel sistema"""
        
        # 1. Aggiungi modelli al DB
        for model_class in module.get_model_classes():
            self.module_registry.add_model(model_class)
        
        # 2. Registra routes API
        for route in module.get_routes():
            self.app.register_blueprint(route)
        
        # 3. Registra hook
        for hook in module.hooks:
            self.module_registry.add_hook(hook.event, hook.callback)
        
        # 4. Registra nel catalogo moduli
        self.module_registry.register(
            name=module.name,
            version=module.version,
            entities=module.entity_names,
            containers=module.container_names,
            config=module.config,
        )
        
        # 5. Crea tabelle DB
        self._create_database_tables(module)
        
        print(f"Modulo '{module.name}' registrato con successo!")
    
    def unregister(self, module_name: str):
        """Rimuove un modulo dal sistema"""
        
        module = self.module_registry.get(module_name)
        
        # 1. Rimuovi routes
        for route in module.get_routes():
            self.app.unregister_blueprint(route)
        
        # 2. Rimuovi hook
        self.module_registry.remove_hooks(module_name)
        
        # 3. Rimuovi dal catalogo
        self.module_registry.unregister(module_name)
        
        print(f"Modulo '{module_name}' rimosso!")
    
    def _create_database_tables(self, module: Module):
        """Crea tabelle DB per il modulo"""
        
        for model_class in module.get_model_classes():
            if not self.db.engine.has_table(model_class.__tablename__):
                model_class.__table__.create(self.db.engine)
```

---

## Interfaccia CLI

```bash
# ============================================================
# COMANDI CLI PER IL BUILDER
# ============================================================

# Build da file template
erpe build --template templates/fleet.yaml --output modules/fleet

# Build da template inline
erpe build --name "nuovo_modulo" --entities "Cliente,Ordine" --output modules/nuovo

# Lista moduli installati
erpe modules list

# Info modulo
erpe modules info fleet_management

# Aggiorna modulo esistente
erpe modules update fleet_management --template templates/fleet_v2.yaml

# Rimuovi modulo
erpe modules remove fleet_management

# Esporta modulo
erpe modules export fleet_management --output fleet_template.yaml

# Valida template senza build
erpe validate templates/fleet.yaml
```

---

## Interfaccia Web (Builder UI)

```
┌─────────────────────────────────────────────────────────────────┐
│                     BUILDER UI                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ 1. DEFINISCI ENTITÀ                                     │    │
│  │ ┌─────────────────────────────────────────────────────┐ │    │
│  │ │ Nome: [Veicolo]  Tabella: [veicoli]                 │ │    │
│  │ │                                                     │ │    │
│  │ │ CAMPI                                               │ │    │
│  │ │ ┌─────────┬──────────┬─────────┬─────────┐          │ │    │
│  │ │ │ targa   │ string   │  [x]    │ [x]     │ +        │ │    │
│  │ │ │ marca   │ string   │  [ ]    │ [ ]     │ +        │ │    │
│  │ │ │ stato   │ select   │  [ ]    │ [ ]     │ +        │ │    │
│  │ │ └─────────┴──────────┴─────────┴─────────┘          │ │    │
│  │ └─────────────────────────────────────────────────────┘ │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ 2. RELAZIONI                                            │    │
│  │ ┌─────────────────────────────────────────────────────┐ │    │
│  │ │ Veicolo ──► Soggetto (proprietario)    many-to-one  │ │    │
│  │ │ Viaggio ──► Veicolo                      many-to-one│ │    │
│  │ │ Veicolo ──► Soggetto (autisti)          many-to-many│ │    │
│  │ └─────────────────────────────────────────────────────┘ │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ 3. CONTAINER                                            │    │
│  │ ┌─────────────────────────────────────────────────────┐ │    │
│  │ │ Container: fleet_ops                                │ │    │
│  │ │ Entità: [Veicolo ✓] [Viaggio ✓]                     │ │    │
│  │ │ API: /api/v1/fleet                                  │ │    │
│  │ └─────────────────────────────────────────────────────┘ │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ 4. LOGICA (Opzionale)                                   │    │
│  │ ┌─────────────────────────────────────────────────────┐ │    │
│  │ │ Formule:                                            │ │    │
│  │ │   costo_km = totale_spese / km                      │ │    │
│  │ │                                                     │ │    │
│  │ │ Hook:                                               │ │    │
│  │ │   Veicolo.before_create → genera_targa()            │ │    │
│  │ │   Viaggio.after_create → aggiorna_km()              │ │    │
│  │ └─────────────────────────────────────────────────────┘ │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│              [VALIDA]  [ANTEPRIMA]  [BUILD]                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Flusso Completo

```
1. CARICAMENTO TEMPLATE
   File YAML → TemplateParser → ModuleTemplate validato

2. GENERAZIONE CODICE
   ModuleTemplate → CodeGenerator → Module (codice Python)

3. MIGRAZIONE DATABASE
   Module → SchemaMigrator → Tabelle create/aggiornate

4. REGISTRAZIONE
   Module → ModuleRegistrar → Modulo attivo in ERPE

5. UTILIZZO
   - API disponibili: GET/POST/PUT/DELETE /api/v1/fleet/*
   - Modelli accessibili: Veicolo, Viaggio
   - Hook attivi: before_create, after_create, etc.
```

---

## Esempio Completo di Utilizzo

```python
# ============================================================
# UTILIZZO COMPLETO DEL BUILDER
# ============================================================

from backend.builder import AdaptiveBuilder
from backend.extensions import db

# Inizializza il builder
builder = AdaptiveBuilder(app, db)

# Template (potrebbe venire da file o API)
template = {
    'name': 'fleet_management',
    'version': '1.0.0',
    'entities': [
        {
            'name': 'Veicolo',
            'fields': [
                {'name': 'targa', 'type': 'string', 'required': True},
                {'name': 'marca', 'type': 'string'},
                {'name': 'modello', 'type': 'string'},
                {'name': 'stato', 'type': 'select', 
                 'options': ['attivo', 'manutenzione', 'dismissione']}
            ],
            'relationships': [
                {'name': 'proprietario', 'type': 'many-to-one', 
                 'target': 'Soggetto'}
            ]
        },
        {
            'name': 'Viaggio',
            'fields': [
                {'name': 'data_partenza', 'type': 'datetime'},
                {'name': 'km_percorsi', 'type': 'integer'},
            ]
        }
    ],
    'containers': [
        {
            'name': 'fleet',
            'entities': ['Veicolo', 'Viaggio'],
            'api_prefix': '/api/v1/fleet'
        }
    ]
}

# Build del modulo
module = builder.build_module(template)

# Il modulo è pronto all'uso!
# - Tabelle create nel DB
# - API registrate
# - Hook attivi
# - Modelli disponibili

# Test delle API generate
response = client.get('/api/v1/fleet/veicoli')
print(response.json)  # Lista veicoli

# Creazione veicolo
response = client.post('/api/v1/fleet/veicoli', json={
    'targa': 'AB123CD',
    'marca': 'Ford',
    'modello': 'Fiesta',
    'stato': 'attivo'
})
print(response.json)  # Veicolo creato
```

---

## Prossimi Passi

1. Implementare `TemplateParser` con validazione
2. Implementare `CodeGenerator` per modelli
3. Implementare `SchemaMigrator` 
4. Implementare `ModuleRegistrar`
5. Creare CLI per il Builder
6. Creare UI per il Builder (estendere GenericCrudPage)
7. Integrare con sistema di permessi
8. Aggiungere supporto per formule
9. Implementare hot-reload dei moduli
