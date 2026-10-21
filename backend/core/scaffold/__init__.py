"""
Scaffold Engine Module for ERPSEED.
Provides Schema-as-Code domain parsing and CQRS code generation commands.
"""
from backend.core.scaffold.commands import (
    RegisterEntityCommand,
    DefineRelationCommand,
    ScaffoldBackendCommand,
    ScaffoldFrontendCommand,
    GenerateMigrationCommand,
)
from backend.core.scaffold.parser import TemplateParser, ScaffoldParseError

__all__ = [
    "RegisterEntityCommand",
    "DefineRelationCommand",
    "ScaffoldBackendCommand",
    "ScaffoldFrontendCommand",
    "GenerateMigrationCommand",
    "TemplateParser",
    "ScaffoldParseError",
]
