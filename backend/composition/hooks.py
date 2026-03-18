"""
Hook System - Sistema di callback per automazione.

Fornisce punti di aggancio per eseguire logica personalizzata
in momenti specifici del ciclo di vita delle entità.
"""
from typing import Dict, List, Callable, Any, Optional
from enum import Enum
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class HookType(Enum):
    """Tipi di hook disponibili"""
    # Entity lifecycle
    BEFORE_CREATE = "before_create"
    AFTER_CREATE = "after_create"
    BEFORE_UPDATE = "before_update"
    AFTER_UPDATE = "after_update"
    BEFORE_DELETE = "before_delete"
    AFTER_DELETE = "after_delete"
    
    # Validation
    BEFORE_VALIDATE = "before_validate"
    AFTER_VALIDATE = "after_validate"
    
    # Custom
    BEFORE_SAVE = "before_save"
    AFTER_SAVE = "after_save"


# Mappatura alias per compatibilità
HOOK_ALIASES = {
    'on_create': HookType.BEFORE_CREATE,
    'after_create': HookType.AFTER_CREATE,
    'on_update': HookType.BEFORE_UPDATE,
    'after_update': HookType.AFTER_UPDATE,
    'on_delete': HookType.BEFORE_DELETE,
    'after_delete': HookType.AFTER_DELETE,
    'before_create': HookType.BEFORE_CREATE,
    'before_update': HookType.BEFORE_UPDATE,
    'before_delete': HookType.BEFORE_DELETE,
}


def resolve_hook_type(hook_name: str) -> HookType:
    """Risolve il nome dell'hook nel tipo corrispondente"""
    if hook_name in HOOK_ALIASES:
        return HOOK_ALIASES[hook_name]
    try:
        return HookType(hook_name)
    except ValueError:
        raise ValueError(f"Hook sconosciuto: {hook_name}")


class Hook:
    """Wrapper per un singolo hook"""
    
    def __init__(self, name: str, callback: Callable, priority: int = 0, 
                 enabled: bool = True, description: str = ""):
        self.name = name
        self.callback = callback
        self.priority = priority
        self.enabled = enabled
        self.description = description
    
    def execute(self, *args, **kwargs) -> Any:
        """Esegue l'hook"""
        if not self.enabled:
            return None
        
        try:
            return self.callback(*args, **kwargs)
        except Exception as e:
            logger.error(f"[Hook] Errore eseguendo {self.name}: {e}")
            raise
    
    def __repr__(self):
        return f"<Hook {self.name} priority={self.priority} enabled={self.enabled}>"


class HookManager:
    """Gestore centrale degli hook"""
    
    _hooks: Dict[str, List[Hook]] = defaultdict(list)
    
    @classmethod
    def register(cls, event: str, callback: Callable, 
                 priority: int = 0, description: str = ""):
        """Registra un hook"""
        hook = Hook(event, callback, priority, description=description)
        cls._hooks[event].append(hook)
        # Ordina per priorità (più alta = eseguita prima)
        cls._hooks[event].sort(key=lambda h: h.priority, reverse=True)
        logger.debug(f"[HookManager] Registrato hook: {event}")
    
    @classmethod
    def unregister(cls, event: str, callback: Callable):
        """Rimuove un hook"""
        if event in cls._hooks:
            cls._hooks[event] = [h for h in cls._hooks[event] 
                                 if h.callback != callback]
    
    @classmethod
    def enable(cls, event: str, callback: Callable = None):
        """Abilita un hook"""
        if callback:
            for hook in cls._hooks.get(event, []):
                if hook.callback == callback:
                    hook.enabled = True
        else:
            for hook in cls._hooks.get(event, []):
                hook.enabled = True
    
    @classmethod
    def disable(cls, event: str, callback: Callable = None):
        """Disabilita un hook"""
        if callback:
            for hook in cls._hooks.get(event, []):
                if hook.callback == callback:
                    hook.enabled = False
        else:
            for hook in cls._hooks.get(event, []):
                hook.enabled = False
    
    @classmethod
    def trigger(cls, event: str, *args, **kwargs) -> List[Any]:
        """Esegue tutti gli hook per un evento"""
        results = []
        for hook in cls._hooks.get(event, []):
            if hook.enabled:
                try:
                    result = hook.execute(*args, **kwargs)
                    results.append({
                        'hook': hook.name,
                        'result': result,
                        'success': True
                    })
                except Exception as e:
                    results.append({
                        'hook': hook.name,
                        'error': str(e),
                        'success': False
                    })
        return results
    
    @classmethod
    def has_hooks(cls, event: str) -> bool:
        """Verifica se ci sono hook per un evento"""
        return any(h.enabled for h in cls._hooks.get(event, []))
    
    @classmethod
    def get_hooks(cls, event: str) -> List[Hook]:
        """Ottiene tutti gli hook per un evento"""
        return cls._hooks.get(event, [])
    
    @classmethod
    def clear(cls, event: str = None):
        """Pulisce gli hook"""
        if event:
            cls._hooks.pop(event, None)
        else:
            cls._hooks.clear()


def hook(event: str, priority: int = 0, description: str = ""):
    """Decorator per registrare automaticamente un hook"""
    def decorator(func: Callable) -> Callable:
        HookManager.register(event, func, priority, description)
        return func
    return decorator


# Hook comuni predefiniti
def create_standard_hooks(entity_name: str) -> Dict[str, Callable]:
    """Crea hook standard per un'entità"""
    return {
        f"{entity_name}.before_create": lambda *args, **kwargs: None,
        f"{entity_name}.after_create": lambda *args, **kwargs: None,
        f"{entity_name}.before_update": lambda *args, **kwargs: None,
        f"{entity_name}.after_update": lambda *args, **kwargs: None,
        f"{entity_name}.before_delete": lambda *args, **kwargs: None,
        f"{entity_name}.after_delete": lambda *args, **kwargs: None,
    }
