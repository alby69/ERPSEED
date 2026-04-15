"""
Block Registry - Registro centrale di tutti i blocchi (mattoncini).

Un Block è l'unità atomica del sistema: un'entità con CRUD, validazione e Hook.
"""
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum


class BlockType(Enum):
    """Tipi di blocco disponibili"""
    ENTITY = "entity"
    VALUE_OBJECT = "value_object"
    AGGREGATE = "aggregate"
    SERVICE = "service"
    PROCESS = "process"


@dataclass
class BlockMetadata:
    """Metadati di un blocco"""
    name: str
    version: str = "1.0.0"
    block_type: BlockType = BlockType.ENTITY
    description: str = ""
    dependencies: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)


class Block:
    """Base class per tutti i blocchi (mattoncini)"""

    metadata: BlockMetadata

    def get_model(self):
        """Restituisce il modello SQLAlchemy associato"""
        return None

    def get_api_routes(self) -> List:
        """Route API esposte dal blocco"""
        return []

    def get_hooks(self) -> Dict[str, Callable]:
        """Hook disponibili (before_create, after_save, etc.)"""
        return {}

    def get_dependencies(self) -> List[str]:
        """Blocchi da cui dipende"""
        return self.metadata.dependencies if self.metadata else []

    def get_config(self) -> Dict[str, Any]:
        """Configurazione del blocco"""
        return self.metadata.config if self.metadata else {}


class BlockRegistry:
    """Registro centrale di tutti i blocchi disponibili"""

    _blocks: Dict[str, Block] = {}
    _metadata: Dict[str, BlockMetadata] = {}

    @classmethod
    def register(cls, block: Block, name: str = None):
        """Registra un blocco nel registry"""
        block_name = name or block.metadata.name
        cls._blocks[block_name] = block
        cls._metadata[block_name] = block.metadata
        print(f"[BlockRegistry] Registrato blocco: {block_name} v{block.metadata.version}")

    @classmethod
    def get(cls, name: str) -> Optional[Block]:
        """Ottiene un blocco per nome"""
        return cls._blocks.get(name)

    @classmethod
    def all(cls) -> List[Block]:
        """Restituisce tutti i blocchi registrati"""
        return list(cls._blocks.values())

    @classmethod
    def all_metadata(cls) -> Dict[str, BlockMetadata]:
        """Restituisce tutti i metadati"""
        return cls._metadata.copy()

    @classmethod
    def exists(cls, name: str) -> bool:
        """Verifica se un blocco esiste"""
        return name in cls._blocks

    @classmethod
    def get_by_type(cls, block_type: BlockType) -> List[Block]:
        """Filtra blocchi per tipo"""
        return [b for b in cls._blocks.values()
                if b.metadata.block_type == block_type]

    @classmethod
    def resolve_dependencies(cls, block_name: str) -> List[str]:
        """Risolve le dipendenze di un blocco (in ordine topologico)"""
        visited = set()
        result = []

        def _visit(name: str):
            if name in visited:
                return
            visited.add(name)

            block = cls.get(name)
            if block:
                for dep in block.get_dependencies():
                    _visit(dep)
                result.append(name)

        _visit(block_name)
        return result

    @classmethod
    def clear(cls):
        """Pulisce il registry (utile per testing)"""
        cls._blocks.clear()
        cls._metadata.clear()


def register_block(name: str = None, block_type: BlockType = BlockType.ENTITY,
                  version: str = "1.0.0", dependencies: List[str] = None):
    """Decorator per registrare automaticamente un blocco"""
    def decorator(cls):
        metadata = BlockMetadata(
            name=name or cls.__name__.lower(),
            version=version,
            block_type=block_type,
            dependencies=dependencies or []
        )
        block_instance = cls()
        block_instance.metadata = metadata
        BlockRegistry.register(block_instance)
        return cls
    return decorator
