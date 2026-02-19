"""
Robot/Module - Modulo funzionale completo.

Un Robot è un modulo funzionale che orchestra più container
e fornisce un'interfaccia unificata.
"""
from typing import List, Dict, Callable, Any, Optional
from dataclasses import dataclass, field


@dataclass
class RobotConfig:
    """Configurazione del robot"""
    name: str
    version: str = "1.0.0"
    description: str = ""
    config: Dict[str, Any] = field(default_factory=dict)


class Robot:
    """Modulo funzionale completo
    
    Un Robot aggrega container e gestisce il ciclo di vita
    di un modulo funzionale completo (es. Vendite, Magazzino).
    """
    
    def __init__(self, name: str, containers: List[Any] = None, 
                 version: str = "1.0.0", description: str = ""):
        self.name = name
        self.version = version
        self.description = description
        self.containers: Dict[str, Any] = {}
        self._is_active = True
        
        if containers:
            for container in containers:
                self.add_container(container)
    
    def add_container(self, container: Any):
        """Aggiunge un container al robot"""
        self.containers[container.name] = container
    
    def remove_container(self, name: str):
        """Rimuove un container dal robot"""
        if name in self.containers:
            del self.containers[name]
    
    def get_container(self, name: str) -> Optional[Any]:
        """Ottiene un container per nome"""
        return self.containers.get(name)
    
    def get_all_containers(self) -> List[Any]:
        """Restituisce tutti i container"""
        return list(self.containers.values())
    
    def get_all_blocks(self) -> List[Any]:
        """Raccoglie tutti i blocchi da tutti i container"""
        blocks = []
        for container in self.containers.values():
            blocks.extend(container.get_all_blocks())
        return blocks
    
    def get_all_routes(self) -> List:
        """Tutte le route di tutti i container"""
        routes = []
        for container in self.containers.values():
            routes.extend(container.get_routes())
        return routes
    
    def get_all_hooks(self) -> Dict[str, List[Callable]]:
        """Tutti gli hook di tutti i container"""
        hooks: Dict[str, List[Callable]] = {}
        
        for container in self.containers.values():
            container_hooks = container.get_hooks()
            for name, callbacks in container_hooks.items():
                if name not in hooks:
                    hooks[name] = []
                if isinstance(callbacks, list):
                    hooks[name].extend(callbacks)
                else:
                    hooks[name].append(callbacks)
        
        return hooks
    
    def call_hook(self, hook_name: str, *args, **kwargs):
        """Esegue un hook su tutti i container"""
        for container in self.containers.values():
            container.call_hook(hook_name, *args, **kwargs)
    
    def get_dependencies(self) -> List[str]:
        """Raccoglie tutte le dipendenze"""
        deps = set()
        for container in self.containers.values():
            deps.update(container.get_dependencies())
        return list(deps)
    
    @property
    def is_active(self) -> bool:
        """Stato del robot"""
        return self._is_active
    
    def activate(self):
        """Attiva il robot"""
        self._is_active = True
    
    def deactivate(self):
        """Disattiva il robot"""
        self._is_active = False
    
    def install(self, app):
        """Registra il robot nell'applicazione Flask"""
        from flask import Flask
        
        if not isinstance(app, Flask):
            raise ValueError("app deve essere un'istanza Flask")
        
        for route in self.get_all_routes():
            try:
                app.register_blueprint(route)
                print(f"[Robot] Registrato blueprint: {route.name}")
            except Exception as e:
                print(f"[Robot] Errore registrando {route}: {e}")
    
    def uninstall(self):
        """Rimuove il robot dall'applicazione"""
        self._is_active = False
    
    def __repr__(self):
        return f"<Robot {self.name} v{self.version}: {len(self.containers)} container>"


class RobotRegistry:
    """Registro centrale di tutti i robot disponibili"""
    
    _robots: Dict[str, Robot] = {}
    
    @classmethod
    def register(cls, robot: Robot):
        """Registra un robot"""
        cls._robots[robot.name] = robot
        print(f"[RobotRegistry] Registrato robot: {robot.name} v{robot.version}")
    
    @classmethod
    def get(cls, name: str) -> Optional[Robot]:
        """Ottiene un robot per nome"""
        return cls._robots.get(name)
    
    @classmethod
    def all(cls) -> List[Robot]:
        """Restituisce tutti i robot"""
        return list(cls._robots.values())
    
    @classmethod
    def active(cls) -> List[Robot]:
        """Restituisce i robot attivi"""
        return [r for r in cls._robots.values() if r.is_active]
    
    @classmethod
    def clear(cls):
        """Pulisce il registro"""
        cls._robots.clear()
