"""
Esempio pratico: come creare un Block, Container e Robot

Questo file mostra come utilizzare il sistema di composizione.
"""
from composition import (
    Block, BlockRegistry, BlockMetadata, BlockType,
    Container, Robot, RobotRegistry,
    EventBus, SystemEvents, HookManager, hook
)


# ============================================================
# ESEMPIO 1: Creare un Block personalizzato
# ============================================================

class SoggettoBlock(Block):
    """Block per la gestione dei Soggetti"""
    
    def __init__(self):
        self.metadata = BlockMetadata(
            name="soggetto",
            version="1.0.0",
            block_type=BlockType.ENTITY,
            description="Gestione anagrafica soggetti",
            dependencies=[]
        )
    
    def get_hooks(self):
        """Restituisce gli hook del blocco"""
        return {
            'soggetto.before_create': self.before_create,
            'soggetto.after_create': self.after_create,
        }
    
    def before_create(self, data):
        """Hook eseguito prima della creazione"""
        print(f"[SoggettoBlock] Prima della creazione: {data}")
        # Logica personalizzata (es. validazione, calcolo campi)
        return data
    
    def after_create(self, entity):
        """Hook eseguito dopo la creazione"""
        print(f"[SoggettoBlock] Dopo la creazione: {entity}")
        # Logica post-creazione (es. invio notifica)


class IndirizzoBlock(Block):
    """Block per la gestione degli Indirizzi"""
    
    def __init__(self):
        self.metadata = BlockMetadata(
            name="indirizzo",
            version="1.0.0",
            block_type=BlockType.VALUE_OBJECT,
            description="Gestione indirizzi geografici",
            dependencies=[]
        )


# ============================================================
# ESEMPIO 2: Creare un Container
# ============================================================

def create_anagrafica_container():
    """Crea il container per l'anagrafica"""
    
    # Crea i blocchi
    soggetto_block = SoggettoBlock()
    indirizzo_block = IndirizzoBlock()
    
    # Crea il container
    container = Container(
        name="anagrafica",
        description="Gestione anagrafica clienti/fornitori",
        api_prefix="/api/v1/anagrafica"
    )
    
    # Aggiungi blocchi
    container.add_block(soggetto_block)
    container.add_block(indirizzo_block)
    
    return container


# ============================================================
# ESEMPIO 3: Creare un Robot
# ============================================================

def create_crm_robot():
    """Crea il robot CRM completo"""
    
    # Crea i container
    anagrafica = create_anagrafica_container()
    
    # Crea il robot
    robot = Robot(
        name="crm",
        version="1.0.0",
        description="Modulo CRM completo"
    )
    
    # Aggiungi container
    robot.add_container(anagrafica)
    
    return robot


# ============================================================
# ESEMPIO 4: Utilizzare Eventi
# ============================================================

def setup_event_handlers():
    """Configura gli handler per gli eventi"""
    
    def on_entity_created(event_data):
        print(f"[EventHandler] Entità creata: {event_data}")
    
    # Iscrivi handler
    EventBus.subscribe(SystemEvents.ENTITY_CREATED, on_entity_created)
    
    # Pubblica evento
    EventBus.publish(SystemEvents.ENTITY_CREATED, {
        'entity_type': 'Soggetto',
        'entity_id': 123
    })


# ============================================================
# ESEMPIO 5: Utilizzare Hook
# ============================================================

@hook("soggetto.before_create", priority=10, description="Valida dati soggetto")
def valida_soggetto(data):
    """Valida i dati del soggetto prima della creazione"""
    if not data.get('nome'):
        raise ValueError("Il nome è obbligatorio")
    return data


@hook("soggetto.after_create", priority=5, description="Invia notifica")
def notifica_nuovo_soggetto(entity):
    """Invia notifica dopo creazione"""
    print(f"[Notifica] Nuovo soggetto creato: {entity}")


# ============================================================
# ESEMPIO 6: Init completo del sistema
# ============================================================

def initialize_composition_system():
    """Inizializza il sistema di composizione"""
    
    # 1. Registra i blocchi
    BlockRegistry.register(SoggettoBlock())
    BlockRegistry.register(IndirizzoBlock())
    
    # 2. Crea e registra i container
    anagrafica = create_anagrafica_container()
    
    # 3. Crea e registra i robot
    crm = create_crm_robot()
    RobotRegistry.register(crm)
    
    # 4. Configura eventi
    setup_event_handlers()
    
    print("\n=== Sistema di Composizione Inizializzato ===")
    print(f"Blocchi registrati: {len(BlockRegistry.all())}")
    print(f"Robot registrati: {len(RobotRegistry.all())}")
    
    return crm


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    # Inizializza il sistema
    crm = initialize_composition_system()
    
    # Testa gli hook
    print("\n=== Test Hooks ===")
    HookManager.trigger("soggetto.before_create", {"nome": "Mario", "cognome": "Rossi"})
    HookManager.trigger("soggetto.after_create", {"id": 1, "nome": "Mario"})
    
    # Testa gli eventi
    print("\n=== Test Eventi ===")
    EventBus.publish(SystemEvents.ENTITY_CREATED, {"tipo": "soggetto"})
