from dataclasses import dataclass
from typing import Dict, Any, List, Optional

@dataclass
class CreateChartCommand:
    title: str
    library: str
    chart_type: str
    model_id: int
    x_axis: str
    y_axis: str
    aggregation: str
    filters: Optional[str] = None
    filters_config: Optional[Dict] = None
    library_options: Optional[Dict] = None

@dataclass
class UpdateChartCommand:
    chart_id: int
    data: Dict[str, Any]

@dataclass
class DeleteChartCommand:
    chart_id: int

@dataclass
class CreateDashboardCommand:
    title: str
    description: Optional[str] = None
    layout: Optional[str] = None
    is_public: bool = False
    refresh_interval: int = 0
    default_library: Optional[str] = None
    created_by: Optional[int] = None

@dataclass
class UpdateDashboardCommand:
    dashboard_id: int
    data: Dict[str, Any]

@dataclass
class DeleteDashboardCommand:
    dashboard_id: int
