import importlib
import inspect
import logging
from pathlib import Path
from typing import List, TYPE_CHECKING

from .interfaces import Plugin

if TYPE_CHECKING:
    from flask import Flask
    from backend.container import ServiceContainer

logger = logging.getLogger(__name__)

class PluginManager:
    """
    Scopre, carica e gestisce il ciclo di vita dei plugin.
    """

    def __init__(self, app: 'Flask', container: 'ServiceContainer', plugin_folder: str = "backend/plugins"):
        self.app = app
        self.container = container
        self.plugin_folder = Path(plugin_folder)
        self.plugins: List[Plugin] = []

    def discover_plugins(self):
        """
        Trova potenziali pacchetti di plugin nella cartella dei plugin.
        Un plugin è una directory con un file __init__.py.
        """
        if not self.plugin_folder.is_dir():
            logger.warning(f"Cartella dei plugin '{self.plugin_folder}' non trovata.")
            return

        for item in self.plugin_folder.iterdir():
            if item.is_dir() and (item / "__init__.py").exists():
                self.load_plugin(item.name)

    def load_plugin(self, plugin_name: str):
        """
        Carica un singolo plugin per nome, lo istanzia e lo registra.
        """
        try:
            module_path = f"{self.plugin_folder.name}.{plugin_name}.plugin"
            plugin_module = importlib.import_module(module_path)

            for _, obj in inspect.getmembers(plugin_module, inspect.isclass):
                if issubclass(obj, Plugin) and obj is not Plugin:
                    plugin_instance = obj()
                    self.register_plugin(plugin_instance)
                    return
            logger.warning(f"Nessuna classe Plugin trovata in '{module_path}'.")

        except ImportError as e:
            logger.error(f"Impossibile importare il plugin '{plugin_name}': {e}")
        except Exception as e:
            logger.error(f"Errore durante il caricamento del plugin '{plugin_name}': {e}", exc_info=True)

    def register_plugin(self, plugin: Plugin):
        """
        Registra un'istanza del plugin e chiama il suo metodo register.
        """
        if plugin in self.plugins:
            logger.warning(f"Il plugin '{plugin.name}' è già registrato.")
            return

        logger.info(f"Registrazione del plugin: {plugin.name} v{plugin.version}")
        try:
            plugin.register(self.app, self.container)
            self.plugins.append(plugin)
        except Exception as e:
            logger.error(f"Errore durante la registrazione del plugin '{plugin.name}': {e}", exc_info=True)

    def unregister_all_plugins(self):
        """Rimuove la registrazione di tutti i plugin caricati."""
        for plugin in reversed(self.plugins):
            logger.info(f"Rimozione registrazione del plugin: {plugin.name}")
            try:
                plugin.unregister(self.app)
            except Exception as e:
                logger.error(f"Errore durante la rimozione della registrazione del plugin '{plugin.name}': {e}", exc_info=True)
        self.plugins = []

    def load_and_register_plugins(self):
        """Metodo di comodo per scoprire e registrare tutti i plugin."""
        logger.info(f"Caricamento dei plugin da '{self.plugin_folder}'...")
        self.discover_plugins()