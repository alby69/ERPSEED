"""
Telemetry System - Raccoglie metriche di utilizzo.

Monitora:
- Tempo risposta API
- Utilizzo risorse
- Errori
- Pattern di utilizzo
"""
import time
import psutil
import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class Metric:
    """Singola metrica registrata"""
    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class RequestMetric:
    """Metrica per richieste HTTP"""
    method: str
    path: str
    status_code: int
    duration_ms: float
    timestamp: datetime
    user_id: Optional[int] = None


class Telemetry:
    """
    Sistema di telemetria per raccogliere metriche.
    
    Usage:
        telemetry = Telemetry()
        telemetry.track('api_call', {'endpoint': '/users', 'duration': 45.2})
        
        stats = telemetry.get_stats()
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self._request_metrics: deque = deque(maxlen=10000)
        self._counters: Dict[str, int] = defaultdict(int)
        self._start_time = time.time()
        self._enabled = True
        self._initialized = True
    
    def enable(self):
        self._enabled = True
    
    def disable(self):
        self._enabled = False
    
    def is_enabled(self) -> bool:
        return self._enabled
    
    def track(self, event: str, data: Dict[str, Any] = None, value: float = 1.0):
        """Registra un evento"""
        if not self._enabled:
            return
        
        metric = Metric(
            name=event,
            value=value,
            timestamp=datetime.now(),
            tags=data or {}
        )
        self._metrics[event].append(metric)
        self._counters[event] += 1
    
    def track_request(self, method: str, path: str, status_code: int, 
                      duration_ms: float, user_id: Optional[int] = None):
        """Registra una richiesta HTTP"""
        if not self._enabled:
            return
        
        metric = RequestMetric(
            method=method,
            path=path,
            status_code=status_code,
            duration_ms=duration_ms,
            timestamp=datetime.now(),
            user_id=user_id
        )
        self._request_metrics.append(metric)
        
        self.track(f"request.{method}", {'path': path, 'status': status_code}, duration_ms)
    
    def increment(self, counter: str, value: int = 1):
        """Incrementa un contatore"""
        self._counters[counter] += value
    
    def get_stats(self, event: str = None) -> Dict[str, Any]:
        """Ottiene statistiche"""
        if event:
            metrics = list(self._metrics.get(event, []))
            if not metrics:
                return {'count': 0}
            
            values = [m.value for m in metrics]
            return {
                'count': len(values),
                'sum': sum(values),
                'avg': sum(values) / len(values),
                'min': min(values),
                'max': max(values),
                'latest': metrics[-1].value if metrics else None,
            }
        
        return {
            'uptime_seconds': time.time() - self._start_time,
            'total_events': sum(self._counters.values()),
            'counters': dict(self._counters),
            'metrics_count': {k: len(v) for k, v in self._metrics.items()},
        }
    
    def get_request_stats(self, since: datetime = None) -> Dict[str, Any]:
        """Ottiene statistiche sulle richieste"""
        metrics = list(self._request_metrics)
        
        if since:
            metrics = [m for m in metrics if m.timestamp >= since]
        
        if not metrics:
            return {'count': 0, 'avg_duration_ms': 0}
        
        total_duration = sum(m.duration_ms for m in metrics)
        status_counts = defaultdict(int)
        
        for m in metrics:
            status_counts[m.status_code] += 1
        
        return {
            'count': len(metrics),
            'avg_duration_ms': total_duration / len(metrics),
            'min_duration_ms': min(m.duration_ms for m in metrics),
            'max_duration_ms': max(m.duration_ms for m in metrics),
            'status_codes': dict(status_counts),
            'methods': dict(defaultdict(int, ((m.method, 0) for m in metrics))),
        }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Ottiene statistiche di sistema"""
        try:
            process = psutil.Process(os.getpid())
            cpu_percent = process.cpu_percent(interval=0.1)
            memory = process.memory_info()
            
            return {
                'cpu_percent': cpu_percent,
                'memory_rss_mb': memory.rss / 1024 / 1024,
                'memory_vms_mb': memory.vms / 1024 / 1024,
                'num_threads': process.num_threads(),
                'open_files': len(process.open_files()),
            }
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            return {}
    
    def get_api_endpoints_stats(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Ottiene statistiche per endpoint"""
        endpoints = defaultdict(lambda: {'count': 0, 'total_duration': 0.0, 'errors': 0})
        
        for m in self._request_metrics:
            key = f"{m.method} {m.path}"
            endpoints[key]['count'] += 1
            endpoints[key]['total_duration'] += m.duration_ms
            if m.status_code >= 400:
                endpoints[key]['errors'] += 1
        
        results = []
        for endpoint, stats in endpoints.items():
            results.append({
                'endpoint': endpoint,
                'count': stats['count'],
                'avg_duration_ms': stats['total_duration'] / stats['count'] if stats['count'] else 0,
                'error_rate': stats['errors'] / stats['count'] if stats['count'] else 0,
            })
        
        return sorted(results, key=lambda x: x['count'], reverse=True)[:limit]
    
    def get_error_rate(self, since: datetime = None) -> float:
        """Calcola il tasso di errore"""
        metrics = list(self._request_metrics)
        
        if since:
            metrics = [m for m in metrics if m.timestamp >= since]
        
        if not metrics:
            return 0.0
        
        errors = sum(1 for m in metrics if m.status_code >= 400)
        return errors / len(metrics)
    
    def clear(self):
        """Pulisce tutte le metriche"""
        self._metrics.clear()
        self._request_metrics.clear()
        self._counters.clear()
    
    def export(self) -> Dict[str, Any]:
        """Esporta tutte le metriche"""
        return {
            'stats': self.get_stats(),
            'request_stats': self.get_request_stats(),
            'system': self.get_system_stats(),
            'endpoints': self.get_api_endpoints_stats(),
            'error_rate': self.get_error_rate(),
        }


def get_telemetry() -> Telemetry:
    """Ottiene l'istanza globale di Telemetry"""
    return Telemetry()
