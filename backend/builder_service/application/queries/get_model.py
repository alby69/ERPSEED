"""
Query Handlers for Builder Service.

Implements CQRS pattern for handling queries.
"""

import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class GetModelQuery:
    """Query to get a single model."""

    def __init__(
        self, model_id: int = None, technical_name: str = None, project_id: int = None
    ):
        self.model_id = model_id
        self.technical_name = technical_name
        self.project_id = project_id


class ListModelsQuery:
    """Query to list models."""

    def __init__(
        self,
        project_id: int,
        status: str = None,
        search: str = None,
        page: int = 1,
        per_page: int = 20,
    ):
        self.project_id = project_id
        self.status = status
        self.search = search
        self.page = page
        self.per_page = per_page


class GetFieldsQuery:
    """Query to get fields for a model."""

    def __init__(self, model_id: int):
        self.model_id = model_id


class GetFieldQuery:
    """Query to get a single field."""

    def __init__(self, field_id: int):
        self.field_id = field_id


class QueryHandler:
    """Handles model queries."""

    def __init__(self, repository):
        self.repository = repository

    def handle_get_model(self, query: GetModelQuery) -> Optional[Dict[str, Any]]:
        """Handle get model query."""
        if query.model_id:
            return self.repository.find_by_id(query.model_id)
        elif query.technical_name and query.project_id:
            return self.repository.find_by_technical_name(
                query.technical_name, query.project_id
            )
        return None

    def handle_list_models(self, query: ListModelsQuery) -> Dict[str, Any]:
        """Handle list models query."""
        models = self.repository.find_by_project(
            query.project_id,
            status=query.status,
            search=query.search,
        )

        total = len(models)
        start = (query.page - 1) * query.per_page
        end = start + query.per_page

        paginated = models[start:end]

        return {
            "items": paginated,
            "total": total,
            "page": query.page,
            "per_page": query.per_page,
            "pages": (total + query.per_page - 1) // query.per_page,
        }

    def handle_get_fields(self, query: GetFieldsQuery) -> List[Dict[str, Any]]:
        """Handle get fields query."""
        return self.repository.get_fields(query.model_id)

    def handle_get_field(self, query: GetFieldQuery) -> Optional[Dict[str, Any]]:
        """Handle get field query."""
        return self.repository.find_field_by_id(query.field_id)
