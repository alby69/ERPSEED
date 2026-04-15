"""
Composition Module - Sistema di Composizione per ERPE.

Fornisce le classi base per costruire il sistema modulare:
- Block: mattoncino atomico
- Container: aggregatore di blocchi
- Robot: modulo funzionale completo
- EventBus: comunicazione asincrona
- HookSystem: callback per automazione
- ExpressionEngine: valutazione espressioni dinamiche
- HotReloader: ricarica moduli a runtime
- AdaptiveModule: moduli modificabili a runtime
"""

from .registry import Block, BlockRegistry, BlockMetadata, BlockType, register_block
from .container import Container, ContainerConfig
from .robot import Robot, RobotRegistry, RobotConfig
from .events import EventBus, SystemEvents, emit
from .hooks import Hook, HookManager, HookType, hook
from .expression import ExpressionEngine, Formula, FormulaRegistry, formula
from .hot_reload import (
    ModuleWatcher,
    HotReloader,
    AdaptiveModule,
    AdaptiveModuleRegistry,
    hot_reload
)

__all__ = [
    # Block
    'Block',
    'BlockRegistry',
    'BlockMetadata',
    'BlockType',
    'register_block',

    # Container
    'Container',
    'ContainerConfig',

    # Robot
    'Robot',
    'RobotRegistry',
    'RobotConfig',

    # Events
    'EventBus',
    'SystemEvents',
    'emit',

    # Hooks
    'Hook',
    'HookManager',
    'HookType',
    'hook',

    # Expression Engine
    'ExpressionEngine',
    'Formula',
    'FormulaRegistry',
    'formula',

    # Hot Reload
    'ModuleWatcher',
    'HotReloader',
    'AdaptiveModule',
    'AdaptiveModuleRegistry',
    'hot_reload',
]
