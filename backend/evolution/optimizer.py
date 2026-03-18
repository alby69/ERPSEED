"""
Auto-Optimizer - Ottimizzazione automatica parametri.

Ottimizza:
- Cache TTL
- Query parameters
- Connection pooling
"""
import time
import random
from typing import Dict, Any, Callable, Optional, List
from dataclasses import dataclass
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class OptimizationResult:
    """Risultato di un'ottimizzazione"""
    parameter: str
    old_value: Any
    new_value: Any
    improvement_percent: float
    timestamp: float


class AutoOptimizer:
    """
    Ottimizza automaticamente i parametri di sistema.
    
    Usage:
        optimizer = AutoOptimizer()
        optimizer.optimize('cache_ttl', range=(60, 3600), objective=score_function)
    """
    
    def __init__(self):
        self.parameters: Dict[str, Dict[str, Any]] = {}
        self.history: List[OptimizationResult] = []
        self._enabled = False
    
    def register_parameter(self, name: str, current_value: Any, 
                          range: tuple = None, choices: List = None):
        """Registra un parametro da ottimizzare"""
        self.parameters[name] = {
            'current': current_value,
            'range': range,
            'choices': choices,
        }
    
    def set_parameter(self, name: str, value: Any):
        """Imposta un parametro"""
        if name in self.parameters:
            self.parameters[name]['current'] = value
    
    def get_parameter(self, name: str) -> Any:
        """Ottiene un parametro"""
        return self.parameters.get(name, {}).get('current')
    
    def optimize(self, parameter: str, objective: Callable[[Any], float],
                 iterations: int = 10) -> Optional[OptimizationResult]:
        """
        Ottimizza un parametro.
        
        Args:
            parameter: Nome del parametro
            objective: Funzione che ritorna uno score (maggiore = meglio)
            iterations: Numero di iterazioni
            
        Returns:
            OptimizationResult con il miglior valore trovato
        """
        if parameter not in self.parameters:
            logger.warning(f"Parameter {parameter} not registered")
            return None
        
        param = self.parameters[parameter]
        current_value = param['current']
        best_value = current_value
        best_score = objective(current_value)
        
        for _ in range(iterations):
            if param['range']:
                min_val, max_val = param['range']
                if isinstance(min_val, int):
                    candidate = random.randint(min_val, max_val)
                else:
                    candidate = random.uniform(min_val, max_val)
            elif param['choices']:
                candidate = random.choice(param['choices'])
            else:
                break
            
            score = objective(candidate)
            
            if score > best_score:
                best_score = score
                best_value = candidate
        
        old_value = param['current']
        improvement = ((best_score - objective(old_value)) / objective(old_value) * 100 
                      if objective(old_value) > 0 else 0)
        
        result = OptimizationResult(
            parameter=parameter,
            old_value=old_value,
            new_value=best_value,
            improvement_percent=improvement,
            timestamp=time.time()
        )
        
        self.history.append(result)
        param['current'] = best_value
        
        logger.info(f"Optimized {parameter}: {old_value} -> {best_value} ({improvement:.1f}%)")
        
        return result
    
    def optimize_all(self, objectives: Dict[str, Callable], 
                     iterations: int = 10) -> List[OptimizationResult]:
        """Ottimizza tutti i parametri"""
        results = []
        for param_name, objective in objectives.items():
            result = self.optimize(param_name, objective, iterations)
            if result:
                results.append(result)
        return results
    
    def get_all_parameters(self) -> Dict[str, Any]:
        """Ottiene tutti i parametri"""
        return {name: param['current'] for name, param in self.parameters.items()}
    
    def get_history(self) -> List[OptimizationResult]:
        """Ottiene la cronologia"""
        return self.history
    
    def reset(self):
        """Resetta lo stato"""
        self.history.clear()


class CacheOptimizer(AutoOptimizer):
    """Ottimizzatore specifico per cache."""
    
    def __init__(self):
        super().__init__()
        self.register_parameter('cache_ttl', 300, range=(60, 3600))
        self.register_parameter('cache_max_size', 1000, range=(100, 10000))
        self.register_parameter('cache_strategy', 'lru', choices=['lru', 'lfu', 'fifo'])
    
    def optimize_from_metrics(self, metrics: Dict[str, Any], iterations: int = 20):
        """Ottimizza basandosi sulle metriche di telemetria"""
        
        def hit_rate_score(ttl: int) -> float:
            hit_rate = metrics.get('cache_hit_rate', 0.5)
            memory_usage = metrics.get('memory_usage', 0.5)
            return hit_rate * 100 - memory_usage * ttl / 100
        
        def size_score(size: int) -> float:
            hit_rate = metrics.get('cache_hit_rate', 0.5)
            return hit_rate * 100 - size / 100
        
        self.optimize('cache_ttl', hit_rate_score, iterations)
        self.optimize('cache_max_size', size_score, iterations)


class QueryOptimizer:
    """Ottimizzatore per query del database."""
    
    def __init__(self):
        self.query_history: List[Dict[str, Any]] = []
        self.slow_query_threshold_ms = 1000
    
    def analyze_query(self, query: str, duration_ms: float, 
                      explain_result: Dict = None) -> Dict[str, Any]:
        """Analizza una query"""
        analysis = {
            'query': query[:100],
            'duration_ms': duration_ms,
            'is_slow': duration_ms > self.slow_query_threshold_ms,
            'recommendations': []
        }
        
        if explain_result:
            if explain_result.get('type') == 'seq_scan':
                analysis['recommendations'].append('Consider adding an index')
            if explain_result.get('rows') > 1000:
                analysis['recommendations'].append('Consider pagination or limit')
        
        self.query_history.append(analysis)
        
        return analysis
    
    def get_slow_queries(self) -> List[Dict[str, Any]]:
        """Ottiene le query lente"""
        return [q for q in self.query_history if q.get('is_slow')]
    
    def get_recommendations(self) -> List[str]:
        """Ottiene raccomandazioni generali"""
        recommendations = []
        
        slow_queries = self.get_slow_queries()
        if len(slow_queries) > 10:
            recommendations.append('High number of slow queries - consider indexing')
        
        avg_duration = sum(q['duration_ms'] for q in self.query_history) / len(self.query_history) if self.query_history else 0
        if avg_duration > 500:
            recommendations.append('Average query duration is high')
        
        return recommendations
