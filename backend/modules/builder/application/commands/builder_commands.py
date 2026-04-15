from dataclasses import dataclass
from typing import Dict, Any, List

@dataclass
class CreateModelCommand:
    projectId: int
    name: str
    title: str
    description: str = None
    permissions: str = None
    technical_name: str = None
    table_name: str = None

@dataclass
class UpdateModelCommand:
    modelId: int
    data: Dict[str, Any]

@dataclass
class DeleteModelCommand:
    modelId: int

@dataclass
class CreateFieldCommand:
    modelId: int
    name: str
    field_type: str
    title: str = None
    technical_name: str = None
    kwargs: Dict[str, Any] = None

@dataclass
class UpdateFieldCommand:
    field_id: int
    data: Dict[str, Any]

@dataclass
class DeleteFieldCommand:
    field_id: int

@dataclass
class SyncSchemaCommand:
    modelId: int
    db_engine: Any

@dataclass
class ResetTableCommand:
    modelId: int
    userId: int
    backup_folder: str = 'backups'

@dataclass
class CloneModelCommand:
    modelId: int
    userId: int
    new_name: str
    new_title: str
