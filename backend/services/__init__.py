"""
Services package - Business logic layer.

DEPRECATION NOTICE:
This package contains service classes that encapsulate business logic.
For new development, prefer CQRS pattern:
- backend.application.* for commands and handlers
- backend.domain.* for domain models
- backend.infrastructure.* for repositories
- backend.endpoints.* for REST APIs

Active services (still used by routes/core):
    - DynamicApiService: Dynamic CRUD for builder models
    - GenericService: Generic CRUD helper
    - ProjectService: Project management
    - UserService: User management
    - WorkflowService: Workflow automation
    - WebhookService: Webhook delivery
    - TemplateService: Starter templates
    - GDOReconciliationService: GDO reconciliation
    - GDOExcelReporter: GDO Excel reports
    - FileProcessingService: CSV/Excel processing

Deprecated services (kept for backward compatibility):
    - BuilderService: Use backend.endpoints.builder instead
"""

from .base import BaseService
from .dynamic_api_service import DynamicApiService
from .generic_service import generic_service, GenericService
from .project_service import ProjectService
from .user_service import UserService
from .workflow_service import WorkflowService
from .workflow_executor import NodeExecutor, WorkflowEngine
from .webhook_service import WebhookService
from .template_service import TemplateService, template_service
from .gdo_reconciliation_service import GDOReconciliationService
from .gdo_excel_reporter import GDOExcelReporter
from .file_processing_service import FileProcessingService

__all__ = [
    'BaseService',
    'DynamicApiService',
    'generic_service',
    'GenericService',
    'ProjectService',
    'UserService',
    'WorkflowService',
    'NodeExecutor',
    'WorkflowEngine',
    'WebhookService',
    'TemplateService',
    'template_service',
    'GDOReconciliationService',
    'GDOExcelReporter',
    'FileProcessingService',
]
