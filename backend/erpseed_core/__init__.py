"""
ERPSEED Core - Backend-only Builder System

A powerful backend builder that generates ERP systems via JSON files, CLI, and AI.
Handles models, blocks, modules, workflows, and business rules.
"""

__version__ = "1.0.0"
__author__ = "ERPSEED Team"

from .builder import ModelBuilder, BlockBuilder, WorkflowBuilder, BusinessRuleBuilder

__all__ = [
    "ModelBuilder",
    "BlockBuilder", 
    "WorkflowBuilder",
    "BusinessRuleBuilder",
]
