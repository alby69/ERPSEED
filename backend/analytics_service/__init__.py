"""
Analytics Service Package - Modular analytics/charts management service.

Usage:
    from backend.analytics_service import execute
    
    # Create a chart
    result = execute({
        "command": "CreateChart",
        "tenant_id": 1,
        "project_id": 1,
        "name": "Sales Chart",
        "chart_type": "bar"
    })
    
    # List charts
    result = execute({
        "command": "ListCharts",
        "tenant_id": 1,
        "project_id": 1
    })

Architecture:
    ├── api.py              # Main entry point (execute function)
    ├── container.py        # Dependency injection
    ├── domain/            # Domain models and events
    ├── application/       # Commands and handlers
    └── infrastructure/    # Repository implementations
"""

from .api import AnalyticsService, execute, get_analytics_service
from .container import register_analytics_service, get_analytics_service

__version__ = "1.0.0"

__all__ = ["AnalyticsService", "execute", "get_analytics_service", "register_analytics_service", "get_analytics_service"]
