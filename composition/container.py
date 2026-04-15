"""
Container - Aggregatore di blocchi.

Un Container raggruppa blocchi correlati e fornisce un'interfaccia unificata.
"""
from typing import List, Dict, Callable, Any, Optional
from dataclasses import dataclass, field


@dataclass
class ContainerConfig:
    """Configurazione del container"""
    name: str
    description: str = ""
    api_prefix: str = ""
    version: str = "1.0.0"
    config: Dict[str, Any] = field(default_factory=dict)


class Container:
    """Aggregatore di blocchi con interfaccia unificata"""

    def __init__(self, name: str, blocks: List[Any] = None,
                 api_prefix: str = "", description: str = ""):
        self.name = name
        self.api_prefix = api_prefix
        self.description = description
        self.blocks: Dict[str, Any] = {}

        if blocks:
            for block in blocks:
                self.add_block(block)

    def add_block(self, block: Any):
        """Aggiunge un blocco al container"""
        block_name = block.metadata.name if hasattr(block, 'metadata') else block.__class__.__name__
        self.blocks[block_name] = block

    def remove_block(self, name: str):
        """Rimuove un blocco dal container"""
        if name in self.blocks:
            del self.blocks[name]

    def get_block(self, name: str) -> Optional[Any]:
        """Ottiene un blocco per nome"""
        return self.blocks.get(name)

    def get_all_blocks(self) -> List[Any]:
        """Restituisce tutti i blocchi"""
        return list(self.blocks.values())

    def get_routes(self) -> List:
        """Raccoglie tutte le route dai blocchi"""
        routes = []
        for block in self.blocks.values():
            try:
                block_routes = block.get_api_routes()
                if block_routes:
                    routes.extend(block_routes)
            except AttributeError:
                pass
        return routes

    def get_hooks(self) -> Dict[str, List[Callable]]:
        """Raccoglie tutti gli hook dai blocchi"""
        hooks: Dict[str, List[Callable]] = {}

        for block in self.blocks.values():
            try:
                block_hooks = block.get_hooks()
                for name, callback in block_hooks.items():
                    if name not in hooks:
                        hooks[name] = []
                    if isinstance(callback, list):
                        hooks[name].extend(callback)
                    else:
                        hooks[name].append(callback)
            except AttributeError:
                pass

        return hooks

    def call_hook(self, hook_name: str, *args, **kwargs):
        """Esegue tutti gli hook di un certo tipo"""
        hooks = self.get_hooks()
        for callback in hooks.get(hook_name, []):
            try:
                callback(*args, **kwargs)
            except Exception as e:
                print(f"[Container] Errore nell'hook {hook_name}: {e}")

    def get_dependencies(self) -> List[str]:
        """Raccoglie tutte le dipendenze"""
        deps = set()
        for block in self.blocks.values():
            try:
                block_deps = block.get_dependencies()
                deps.update(block_deps)
            except AttributeError:
                pass
        return list(deps)

    def __repr__(self):
        return f"<Container {self.name}: {len(self.blocks)} blocchi>"
