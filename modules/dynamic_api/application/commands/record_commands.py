from dataclasses import dataclass
from typing import Dict, Any, List

@dataclass
class ListRecordsCommand:
    project_id: int
    model_name: int
    page: int = 1
    per_page: int = 10
    filters: Dict[str, Any] = None

@dataclass
class CreateRecordCommand:
    project_id: int
    model_name: str
    data: Dict[str, Any]

@dataclass
class UpdateRecordCommand:
    project_id: int
    model_name: str
    item_id: int
    data: Dict[str, Any]

@dataclass
class DeleteRecordCommand:
    project_id: int
    model_name: str
    item_id: int

@dataclass
class BulkDeleteCommand:
    project_id: int
    model_name: str
    ids: List[int]
