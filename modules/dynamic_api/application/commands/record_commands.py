from dataclasses import dataclass
from typing import Dict, Any, List

@dataclass
class ListRecordsCommand:
    projectId: int
    model_name: int
    page: int = 1
    per_page: int = 10
    filters: Dict[str, Any] = None

@dataclass
class CreateRecordCommand:
    projectId: int
    model_name: str
    data: Dict[str, Any]

@dataclass
class UpdateRecordCommand:
    projectId: int
    model_name: str
    itemId: int
    data: Dict[str, Any]

@dataclass
class DeleteRecordCommand:
    projectId: int
    model_name: str
    itemId: int

@dataclass
class BulkDeleteCommand:
    projectId: int
    model_name: str
    ids: List[int]
