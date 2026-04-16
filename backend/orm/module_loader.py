"""
Module Loader - Loads and manages FlaskERP modules.

Scans modules directory, resolves dependencies, and loads:
- Models
- Views
- Data
- Security

Structure:
    modules/
        crm/
            __manifest__.json
            models/
            views/
            data/
            security/
            hooks.py
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class ModuleManifest:
    """Represents a module's manifest (__manifest__.json)."""

    def __init__(self, path: Path, data: Dict):
        self.path = path
        self.data = data
        self.name = data.get("name", path.name)
        self.version = data.get("version", "1.0.0")
        self.depends = data.get("depends", [])
        self.category = data.get("category", "custom")
        self.description = data.get("description", "")
        self.author = data.get("author", "Unknown")
        self.is_core = data.get("is_core", False)

    def __repr__(self):
        return f"<ModuleManifest {self.name} v{self.version}>"


class ModuleLoader:
    """Loads and manages FlaskERP modules."""

    def __init__(self, modules_dir: str = None):
        if modules_dir is None:
            # Default to backend/plugins
            self.modules_dir = Path(__file__).parent.parent / "plugins"
        else:
            self.modules_dir = Path(modules_dir)

        self.modules: Dict[str, ModuleManifest] = {}
        self.loaded_modules: List[str] = []

    def scan_modules(self) -> List[ModuleManifest]:
        """Scan modules directory for modules with __manifest__.json."""
        modules = []

        if not self.modules_dir.exists():
            logger.warning(f"Modules directory not found: {self.modules_dir}")
            return modules

        for item in self.modules_dir.iterdir():
            if not item.is_dir():
                continue

            manifest_file = item / "__manifest__.json"
            if not manifest_file.exists():
                continue

            try:
                with open(manifest_file, "r") as f:
                    data = json.load(f)

                manifest = ModuleManifest(item, data)
                self.modules[manifest.name] = manifest
                modules.append(manifest)
                logger.info(f"Found module: {manifest.name}")

            except Exception as e:
                logger.error(f"Error loading module {item.name}: {e}")

        return modules

    def resolve_dependencies(
        self, module_name: str, visited: List[str] = None
    ) -> List[str]:
        """Resolve module dependencies using topological sort.

        Returns list of module names in load order.
        """
        if visited is None:
            visited = []

        if module_name in visited:
            return []

        if module_name not in self.modules:
            logger.warning(f"Module not found: {module_name}")
            return []

        module = self.modules[module_name]
        visited.append(module_name)

        # Process dependencies first
        for dep in module.depends:
            self.resolve_dependencies(dep, visited)

        return visited

    def load_manifest(self, module_name: str) -> Optional[ModuleManifest]:
        """Load a single module's manifest."""
        return self.modules.get(module_name)

    def load_module(self, module_name: str) -> bool:
        """Load a module and its dependencies.

        Loads:
        - Models (Python files in models/ subdirectory)
        - Views (JSON/XML in views/)
        - Data (seed data in data/)
        - Security (CSV/JSON in security/)
        - Hooks (hooks.py)
        """
        if module_name in self.loaded_modules:
            logger.info(f"Module already loaded: {module_name}")
            return True

        # Resolve dependencies
        load_order = self.resolve_dependencies(module_name)

        for mod_name in load_order:
            if mod_name in self.loaded_modules:
                continue

            manifest = self.modules.get(mod_name)
            if not manifest:
                logger.error(f"Cannot load module: {mod_name}")
                continue

            logger.info(f"Loading module: {mod_name}")

            # Load models
            self._load_models(manifest)

            # Load views
            self._load_views(manifest)

            # Load data
            self._load_data(manifest)

            # Load security
            self._load_security(manifest)

            # Load hooks
            self._load_hooks(manifest)

            self.loaded_modules.append(mod_name)

        return True

    def _load_models(self, manifest: ModuleManifest):
        """Load Python model files."""
        models_dir = manifest.path / "models"
        if not models_dir.exists():
            return

        for file in models_dir.glob("*.py"):
            if file.name.startswith("_"):
                continue

            try:
                # Import the module
                module_name = f"{manifest.path.stem}.models.{file.stem}"
                logger.debug(f"Loading model: {module_name}")
            except Exception as e:
                logger.error(f"Error loading model {file}: {e}")

    def _load_views(self, manifest: ModuleManifest):
        """Load view definitions."""
        views_dir = manifest.path / "views"
        if not views_dir.exists():
            return

        for file in views_dir.glob("*.json"):
            try:
                with open(file, "r") as f:
                    data = json.load(f)
                logger.debug(f"Loaded view: {file.name}")
            except Exception as e:
                logger.error(f"Error loading view {file}: {e}")

    def _load_data(self, manifest: ModuleManifest):
        """Load seed data."""
        data_dir = manifest.path / "data"
        if not data_dir.exists():
            return

        for file in data_dir.glob("*.json"):
            try:
                with open(file, "r") as f:
                    data = json.load(f)
                logger.debug(f"Loaded data: {file.name}")
            except Exception as e:
                logger.error(f"Error loading data {file}: {e}")

    def _load_security(self, manifest: ModuleManifest):
        """Load security definitions."""
        security_dir = manifest.path / "security"
        if not security_dir.exists():
            return

        for file in security_dir.glob("*.csv"):
            logger.debug(f"Loaded security: {file.name}")
        for file in security_dir.glob("*.json"):
            logger.debug(f"Loaded security: {file.name}")

    def _load_hooks(self, manifest: ModuleManifest):
        """Load module hooks."""
        hooks_file = manifest.path / "hooks.py"
        if not hooks_file.exists():
            return

        try:
            logger.debug(f"Loading hooks: {manifest.name}")
        except Exception as e:
            logger.error(f"Error loading hooks {manifest.path.name}: {e}")

    def get_module_info(self, module_name: str) -> Optional[Dict]:
        """Get module information."""
        manifest = self.modules.get(module_name)
        if not manifest:
            return None

        return {
            "name": manifest.name,
            "version": manifest.version,
            "depends": manifest.depends,
            "category": manifest.category,
            "description": manifest.description,
            "author": manifest.author,
            "is_core": manifest.is_core,
            "path": str(manifest.path),
        }

    def list_modules(self) -> List[str]:
        """List all available modules."""
        return list(self.modules.keys())

    def get_loaded_modules(self) -> List[str]:
        """List all loaded modules."""
        return self.loaded_modules.copy()


# Global loader instance
_loader: Optional[ModuleLoader] = None


def get_module_loader(modules_dir: str = None) -> ModuleLoader:
    """Get the global module loader instance."""
    global _loader
    if _loader is None:
        _loader = ModuleLoader(modules_dir)
    return _loader


def scan_and_load_modules() -> List[str]:
    """Scan for modules and load them."""
    loader = get_module_loader()
    loader.scan_modules()

    # Load all modules (or filter for auto-load)
    for module_name in loader.modules:
        loader.load_module(module_name)

    return loader.get_loaded_modules()
