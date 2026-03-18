import pytest
from unittest.mock import Mock, MagicMock
from pathlib import Path

from .manager import PluginManager
from .interfaces import Plugin

# --- Fixtures e Mocks ---

@pytest.fixture
def mock_app():
    """Un'app Flask mockata."""
    app = MagicMock()
    app.blueprints = {}
    def register_blueprint(bp, url_prefix=None):
        app.blueprints[bp.name] = {"bp": bp, "url_prefix": url_prefix}
    app.register_blueprint = register_blueprint
    return app

@pytest.fixture
def mock_container():
    """Un ServiceContainer mockato."""
    container = MagicMock()
    container.services = {}
    def register(name, provider, singleton=False):
        container.services[name] = {"provider": provider, "singleton": singleton}
    container.register = register
    return container

@pytest.fixture
def plugin_dir(tmp_path: Path) -> Path:
    """Crea una struttura di directory temporanea per i plugin."""
    base_dir = tmp_path / "backend"
    plugins_path = base_dir / "plugins"
    plugins_path.mkdir(parents=True)
    (plugins_path / "__init__.py").touch()
    (base_dir / "__init__.py").touch()
    return plugins_path

# --- Implementazioni di Plugin di Test ---

def create_valid_plugin(plugin_dir: Path):
    """Crea un plugin valido per il test."""
    plugin_path = plugin_dir / "valid_plugin"
    plugin_path.mkdir()
    (plugin_path / "__init__.py").touch()
    (plugin_path / "plugin.py").write_text(
        """
from unittest.mock import Mock
from backend.plugin_system.interfaces import Plugin

class ValidPlugin(Plugin):
    @property
    def name(self):
        return "Valid Test Plugin"

    @property
    def version(self):
        return "1.0.0"

    def register(self, app, container):
        mock_bp = Mock()
        mock_bp.name = "valid_plugin_bp"
        app.register_blueprint(mock_bp)
        container.register("valid_service", lambda: "service_instance")

    def unregister(self, app):
        pass
"""
    )

def create_plugin_with_import_error(plugin_dir: Path):
    """Crea un plugin con un errore di sintassi."""
    plugin_path = plugin_dir / "import_error_plugin"
    plugin_path.mkdir()
    (plugin_path / "__init__.py").touch()
    (plugin_path / "plugin.py").write_text("import non_existent_module")

def create_plugin_without_plugin_class(plugin_dir: Path):
    """Crea una directory di plugin che non ha una sottoclasse di Plugin."""
    plugin_path = plugin_dir / "no_class_plugin"
    plugin_path.mkdir()
    (plugin_path / "__init__.py").touch()
    (plugin_path / "plugin.py").write_text("class NotAPlugin: pass")

def create_plugin_with_register_error(plugin_dir: Path):
    """Crea un plugin che solleva un errore durante la registrazione."""
    plugin_path = plugin_dir / "register_error_plugin"
    plugin_path.mkdir()
    (plugin_path / "__init__.py").touch()
    (plugin_path / "plugin.py").write_text(
        """
from backend.plugin_system.interfaces import Plugin

class RegisterErrorPlugin(Plugin):
    @property
    def name(self): return "Register Error Plugin"
    @property
    def version(self): return "1.0"
    def register(self, app, container):
        raise ValueError("Qualcosa è andato storto durante la registrazione")
    def unregister(self, app): pass
"""
    )

# --- Casi di Test ---

def test_plugin_manager_initialization(mock_app, mock_container, plugin_dir):
    """Testa che il PluginManager si inizializzi correttamente."""
    manager = PluginManager(mock_app, mock_container, plugin_folder=str(plugin_dir))
    assert manager.app is mock_app
    assert manager.container is mock_container
    assert manager.plugin_folder == plugin_dir
    assert manager.plugins == []

def test_discover_and_load_valid_plugin(mock_app, mock_container, plugin_dir):
    """Testa che un plugin valido venga scoperto, caricato e registrato."""
    create_valid_plugin(plugin_dir)
    manager = PluginManager(mock_app, mock_container, plugin_folder=str(plugin_dir))

    manager.load_and_register_plugins()

    assert len(manager.plugins) == 1
    plugin = manager.plugins[0]
    assert plugin.name == "Valid Test Plugin"
    assert plugin.version == "1.0.0"

    assert "valid_plugin_bp" in mock_app.blueprints
    assert "valid_service" in mock_container.services

def test_discover_multiple_plugins(mock_app, mock_container, plugin_dir):
    """Testa la scoperta di più plugin, inclusi quelli non validi."""
    create_valid_plugin(plugin_dir)
    create_plugin_with_import_error(plugin_dir)
    create_plugin_without_plugin_class(plugin_dir)

    manager = PluginManager(mock_app, mock_container, plugin_folder=str(plugin_dir))
    manager.load_and_register_plugins()

    assert len(manager.plugins) == 1
    assert manager.plugins[0].name == "Valid Test Plugin"

def test_handle_plugin_with_import_error(mock_app, mock_container, plugin_dir, caplog):
    """Testa che un errore di import in un plugin sia gestito correttamente."""
    create_plugin_with_import_error(plugin_dir)
    manager = PluginManager(mock_app, mock_container, plugin_folder=str(plugin_dir))
    manager.load_and_register_plugins()
    assert len(manager.plugins) == 0
    assert "Impossibile importare il plugin 'import_error_plugin'" in caplog.text

def test_handle_plugin_without_plugin_class(mock_app, mock_container, plugin_dir, caplog):
    """Testa che un plugin senza una sottoclasse di Plugin sia gestito."""
    create_plugin_without_plugin_class(plugin_dir)
    manager = PluginManager(mock_app, mock_container, plugin_folder=str(plugin_dir))
    manager.load_and_register_plugins()
    assert len(manager.plugins) == 0
    assert "Nessuna classe Plugin trovata" in caplog.text

def test_handle_plugin_with_registration_error(mock_app, mock_container, plugin_dir, caplog):
    """Testa che un errore durante il metodo register() del plugin venga catturato."""
    create_plugin_with_register_error(plugin_dir)
    manager = PluginManager(mock_app, mock_container, plugin_folder=str(plugin_dir))
    manager.load_and_register_plugins()
    assert len(manager.plugins) == 0
    assert "Errore durante la registrazione del plugin 'Register Error Plugin'" in caplog.text
    assert "Qualcosa è andato storto durante la registrazione" in caplog.text

def test_unregister_all_plugins(mock_app, mock_container, plugin_dir):
    """Testa che il metodo unregister venga chiamato per tutti i plugin caricati."""
    create_valid_plugin(plugin_dir)
    manager = PluginManager(mock_app, mock_container, plugin_folder=str(plugin_dir))
    manager.load_and_register_plugins()
    assert len(manager.plugins) == 1
    manager.plugins[0].unregister = Mock()
    manager.unregister_all_plugins()
    assert len(manager.plugins) == 0
    manager.plugins[0].unregister.assert_called_once_with(mock_app)