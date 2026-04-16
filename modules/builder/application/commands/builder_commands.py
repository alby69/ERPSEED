from dataclasses import dataclass
from typing import Dict, Any, List

@dataclass
class CreateModelCommand:
    project_id: int
    name: str
    title: str
    description: str = None
    permissions: str = None
    technical_name: str = None
    table_name: str = None

@dataclass
class UpdateModelCommand:
    model_id: int
    data: Dict[str, Any]

@dataclass
class DeleteModelCommand:
    model_id: int

@dataclass
class CreateFieldCommand:
    model_id: int
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
    model_id: int
    db_engine: Any

@dataclass
class ResetTableCommand:
    model_id: int
    user_id: int
    backup_folder: str = 'backups'

@dataclass
class CloneModelCommand:
    model_id: int
    user_id: int
    new_name: str
    new_title: str
