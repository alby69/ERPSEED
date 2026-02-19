"""
Hot Reload System - Ricarica moduli a runtime.

Permette di ricaricare moduli e componenti senza riavviare
l'applicazione.
"""
import os
import sys
import importlib
import hashlib
import time
import logging
from typing import Dict, Callable, Any, Optional, List
from pathlib import Path
from threading import Thread, Event
from functools import wraps

logger = logging.getLogger(__name__)


class ModuleWatcher:
    """
    Watcher per file e moduli.
    Monitora le modifiche ai file e triggerisce il reload.
    """
    
    def __init__(self, watch_paths: Optional[List[str]] = None):
        self.watch_paths = watch_paths or []
        self.file_mtimes: Dict[str, float] = {}
        self.file_hashes: Dict[str, str] = {}
        self._running = False
        self._stop_event = Event()
        self._watch_thread: Optional[Thread] = None
        self.on_change_callbacks: List[Callable] = []
    
    def add_path(self, path: str):
        """Aggiunge un percorso da monitorare"""
        if path not in self.watch_paths:
            self.watch_paths.append(path)
    
    def remove_path(self, path: str):
        """Rimuove un percorso"""
        if path in self.watch_paths:
            self.watch_paths.remove(path)
    
    def on_change(self, callback: Callable):
        """Registra un callback per le modifiche"""
        self.on_change_callbacks.append(callback)
    
    def start(self, interval: float = 1.0):
        """Avvia il watcher"""
        if self._running:
            return
        
        self._running = True
        self._stop_event.clear()
        self._watch_thread = Thread(target=self._watch_loop, args=(interval,), daemon=True)
        self._watch_thread.start()
        logger.info("[HotReload] Watcher started")
    
    def stop(self):
        """Ferma il watcher"""
        self._running = False
        self._stop_event.set()
        if self._watch_thread:
            self._watch_thread.join(timeout=5)
        logger.info("[HotReload] Watcher stopped")
    
    def _watch_loop(self, interval: float):
        """Loop principale del watcher"""
        while not self._stop_event.is_set():
            try:
                changed_files = self._check_changes()
                if changed_files:
                    for callback in self.on_change_callbacks:
                        try:
                            callback(changed_files)
                        except Exception as e:
                            logger.error(f"[HotReload] Callback error: {e}")
            except Exception as e:
                logger.error(f"[HotReload] Watch error: {e}")
            
            self._stop_event.wait(interval)
    
    def _check_changes(self) -> List[str]:
        """Controlla le modifiche ai file"""
        changed = []
        
        for watch_path in self.watch_paths:
            path = Path(watch_path)
            
            if not path.exists():
                continue
            
            if path.is_file():
                files = [path]
            else:
                files = path.rglob("*.py")
            
            for file_path in files:
                if file_path.name.startswith('_'):
                    continue
                    
                try:
                    mtime = file_path.stat().st_mtime
                    key = str(file_path)
                    
                    if key not in self.file_mtimes:
                        self.file_mtimes[key] = mtime
                        continue
                    
                    if mtime > self.file_mtimes[key]:
                        self.file_mtimes[key] = mtime
                        changed.append(str(file_path))
                        
                except OSError:
                    continue
        
        return changed
    
    def get_watched_files(self) -> List[str]:
        """Restituisce la lista dei file monitorati"""
        return list(self.file_mtimes.keys())


class HotReloader:
    """
    Sistema di hot reload per moduli Python.
    """
    
    _instances: Dict[str, 'HotReloader'] = {}
    _module_cache: Dict[str, Any] = {}
    
    def __init__(self, module_name: str):
        self.module_name = module_name
        self.module = None
        self.last_reload = 0
        self.reload_count = 0
        self._callbacks: Dict[str, List[Callable]] = {
            'before_reload': [],
            'after_reload': [],
            'error': []
        }
    
    @classmethod
    def get_instance(cls, module_name: str) -> 'HotReloader':
        """Ottiene un'istanza per il modulo"""
        if module_name not in cls._instances:
            cls._instances[module_name] = HotReloader(module_name)
        return cls._instances[module_name]
    
    def register_callback(self, event: str, callback: Callable):
        """Registra un callback per eventi di reload"""
        if event in self._callbacks:
            self._callbacks[event].append(callback)
    
    def reload(self, force: bool = False) -> bool:
        """
        Ricarica il modulo.
        
        Args:
            force: Forza il reload anche se non è cambiato
            
        Returns:
            True se il reload è avvenuto con successo
        """
        current_time = time.time()
        
        if not force and current_time - self.last_reload < 1.0:
            logger.debug(f"[HotReload] Skipping reload for {self.module_name} (too soon)")
            return False
        
        for callback in self._callbacks['before_reload']:
            try:
                callback(self.module_name)
            except Exception as e:
                logger.error(f"[HotReload] before_reload callback error: {e}")
        
        try:
            if self.module_name in sys.modules:
                old_module = sys.modules[self.module_name]
                
                for callback in self._callbacks.get('before_unload', []):
                    try:
                        callback(old_module)
                    except Exception:
                        pass
            
            importlib.invalidate_caches()
            self.module = importlib.import_module(self.module_name)
            
            self.last_reload = current_time
            self.reload_count += 1
            
            for callback in self._callbacks['after_reload']:
                try:
                    callback(self.module_name, self.module)
                except Exception as e:
                    logger.error(f"[HotReload] after_reload callback error: {e}")
            
            logger.info(f"[HotReload] Reloaded module: {self.module_name} (count: {self.reload_count})")
            return True
            
        except Exception as e:
            logger.error(f"[HotReload] Error reloading {self.module_name}: {e}")
            
            for callback in self._callbacks['error']:
                try:
                    callback(self.module_name, e)
                except Exception:
                    pass
            
            return False
    
    def get_module(self):
        """Ottiene il modulo corrente"""
        if self.module is None:
            try:
                self.module = importlib.import_module(self.module_name)
            except ImportError as e:
                logger.error(f"[HotReload] Cannot import {self.module_name}: {e}")
        return self.module


class AdaptiveModule:
    """
    Modulo adattivo che può essere modificato a runtime.
    """
    
    def __init__(self, name: str, module_path: str):
        self.name = name
        self.module_path = module_path
        self.reloader = HotReloader.get_instance(module_path)
        self._enabled = False
        self._config: Dict[str, Any] = {}
    
    def enable(self):
        """Abilita il modulo"""
        self._enabled = True
        logger.info(f"[AdaptiveModule] Enabled: {self.name}")
    
    def disable(self):
        """Disabilita il modulo"""
        self._enabled = False
        logger.info(f"[AdaptiveModule] Disabled: {self.name}")
    
    def is_enabled(self) -> bool:
        """Verifica se il modulo è abilitato"""
        return self._enabled
    
    def reload(self) -> bool:
        """Ricarica il modulo"""
        if not self._enabled:
            logger.warning(f"[AdaptiveModule] Cannot reload disabled module: {self.name}")
            return False
        return self.reloader.reload()
    
    def get_module(self):
        """Ottiene il modulo corrente"""
        return self.reloader.get_module()
    
    def update_config(self, **config):
        """Aggiorna la configurazione"""
        self._config.update(config)
    
    def get_config(self) -> Dict[str, Any]:
        """Ottiene la configurazione"""
        return self._config.copy()


class AdaptiveModuleRegistry:
    """
    Registry per moduli adattivi.
    """
    
    _modules: Dict[str, AdaptiveModule] = {}
    _global_watcher: Optional[ModuleWatcher] = None
    
    @classmethod
    def register(cls, module: AdaptiveModule):
        cls._modules[module.name] = module
        logger.info(f"[AdaptiveModuleRegistry] Registered: {module.name}")
    
    @classmethod
    def unregister(cls, name: str):
        module = cls._modules.pop(name, None)
        if module:
            module.disable()
            logger.info(f"[AdaptiveModuleRegistry] Unregistered: {name}")
    
    @classmethod
    def get(cls, name: str) -> Optional[AdaptiveModule]:
        return cls._modules.get(name)
    
    @classmethod
    def list_all(cls) -> Dict[str, AdaptiveModule]:
        return cls._modules.copy()
    
    @classmethod
    def reload_all(cls) -> Dict[str, bool]:
        """Ricarica tutti i moduli"""
        results = {}
        for name, module in cls._modules.items():
            results[name] = module.reload()
        return results
    
    @classmethod
    def enable_all(cls):
        """Abilita tutti i moduli"""
        for module in cls._modules.values():
            module.enable()
    
    @classmethod
    def disable_all(cls):
        """Disabilita tutti i moduli"""
        for module in cls._modules.values():
            module.disable()
    
    @classmethod
    def start_auto_reload(cls, paths: List[str], interval: float = 1.0):
        """Avvia il reload automatico"""
        if cls._global_watcher is None:
            cls._global_watcher = ModuleWatcher(paths)
        
        def on_files_changed(files: List[str]):
            modules_to_reload = set()
            
            for path in files:
                for name, module in cls._modules.items():
                    if module.module_path in path or path.startswith(module.module_path.replace('.', '/')):
                        modules_to_reload.add(name)
            
            for name in modules_to_reload:
                module = cls._modules.get(name)
                if module and module.is_enabled():
                    module.reload()
        
        cls._global_watcher.on_change(on_files_changed)
        cls._global_watcher.start(interval)
    
    @classmethod
    def stop_auto_reload(cls):
        """Ferma il reload automatico"""
        if cls._global_watcher:
            cls._global_watcher.stop()


def hot_reload(module_name: str):
    """
    Decorator per abilitare hot reload su un modulo.
    
    Usage:
        @hot_reload('backend.plugins.my_plugin')
        class MyPlugin:
            ...
    """
    def decorator(cls):
        reloader = HotReloader.get_instance(module_name)
        
        @wraps(cls)
        def wrapper(*args, **kwargs):
            if not reloader.reload():
                module = reloader.get_module()
                if module:
                    return getattr(module, cls.__name__, cls)
            return cls(*args, **kwargs)
        
        wrapper._reloader = reloader
        return wrapper
    
    return decorator
