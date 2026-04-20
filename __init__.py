"""
OpenSpace-OpenHands-Evolution

Self-evolving AI programming assistant with hierarchical agent architecture.
"""

from importlib import import_module as _imp
from typing import TYPE_CHECKING as _TYPE_CHECKING

if _TYPE_CHECKING:
    from .orchestrator import (
        EvolutionOrchestrator as EvolutionOrchestrator,
        TaskRequest as TaskRequest,
        TransferRequest as TransferRequest,
        TaskResult as TaskResult,
        TransferResult as TransferResult,
    )
    from .config_loader import (
        load_config as load_config,
        save_config as save_config,
        create_default_config as create_default_config,
    )

__version__ = "0.1.1"
__author__ = "OpenSpace Team"

__all__ = [
    # Version
    "__version__",
    
    # Main API
    "EvolutionOrchestrator",
    "TaskRequest",
    "TransferRequest",
    "TaskResult",
    "TransferResult",
    
    # Configuration
    "load_config",
    "save_config", 
    "create_default_config",
]

# Map attribute → sub-module that provides it
_attr_to_module = {
    # Main API
    "EvolutionOrchestrator": "openspace_openhands_evolution.orchestrator",
    "TaskRequest": "openspace_openhands_evolution.orchestrator",
    "TransferRequest": "openspace_openhands_evolution.orchestrator",
    "TaskResult": "openspace_openhands_evolution.orchestrator",
    "TransferResult": "openspace_openhands_evolution.orchestrator",
    
    # Configuration
    "load_config": "openspace_openhands_evolution.config_loader",
    "save_config": "openspace_openhands_evolution.config_loader",
    "create_default_config": "openspace_openhands_evolution.config_loader",
}


def __getattr__(name: str):
    """Dynamically import sub-modules on first attribute access.
    
    This keeps the initial package import lightweight and avoids raising
    ModuleNotFoundError for optional dependencies until explicitly used.
    """
    if name not in _attr_to_module:
        raise AttributeError(f"module 'openspace_openhands_evolution' has no attribute '{name}'")
    
    module_name = _attr_to_module[name]
    module = _imp(module_name)
    value = getattr(module, name)
    globals()[name] = value
    return value


def __dir__():
    return sorted(list(globals().keys()) + list(_attr_to_module.keys()))
