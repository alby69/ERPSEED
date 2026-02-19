"""
Evolution Module - Sistema di Evoluzione per ERPE.

Fornisce funzionalità avanzate di auto-ottimizzazione:
- Telemetry: raccolta metriche di utilizzo
- AutoOptimizer: ottimizzazione automatica parametri
- GeneticOptimizer: algoritmi genetici
"""

from .telemetry import Telemetry, Metric, RequestMetric, get_telemetry
from .optimizer import AutoOptimizer, CacheOptimizer, QueryOptimizer, OptimizationResult
from .genetic import GeneticOptimizer, AdaptiveOptimizer, MultiObjectiveOptimizer, Individual

__all__ = [
    # Telemetry
    'Telemetry',
    'Metric',
    'RequestMetric',
    'get_telemetry',
    
    # Optimizer
    'AutoOptimizer',
    'CacheOptimizer',
    'QueryOptimizer',
    'OptimizationResult',
    
    # Genetic
    'GeneticOptimizer',
    'AdaptiveOptimizer',
    'MultiObjectiveOptimizer',
    'Individual',
]
