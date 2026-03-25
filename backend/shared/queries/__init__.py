"""
Query Base Classes - Base classes for read operations in CQRS pattern.

Queries are immutable objects that represent a request for data.
Unlike Commands, Queries do not modify state.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
import uuid


@dataclass
class Query:
    """Base class for all queries."""

    query_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    tenant_id: Optional[int] = None
    user_id: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert query to dictionary."""
        return {
            "query_id": self.query_id,
            "timestamp": self.timestamp.isoformat(),
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "metadata": self.metadata,
        }


@dataclass
class ListQuery(Query):
    """Base class for list/collection queries with pagination and sorting."""
    filters: Dict[str, Any] = field(default_factory=dict)
    pagination: Dict[str, Any] = field(default_factory=lambda: {"page": 1, "page_size": 20})
    sorting: Dict[str, Any] = field(default_factory=lambda: {"field": "id", "direction": "asc"})

    @property
    def page(self) -> int:
        return self.pagination.get("page", 1)

    @property
    def page_size(self) -> int:
        return self.pagination.get("page_size", 20)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


@dataclass
class GetByIdQuery(Query):
    """Base class for getting a single entity by ID."""
    entity_id: int = 0


@dataclass
class SearchQuery(Query):
    """Base class for search queries with full-text or complex filters."""
    search_term: str = ""
    filters: Dict[str, Any] = field(default_factory=dict)
    pagination: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QueryResult:
    """Standard result returned by all query handlers."""

    success: bool = True
    data: Any = None
    error: Optional[str] = None
    errors: List[str] = field(default_factory=list)
    total_count: int = 0
    page: int = 1
    page_size: int = 20
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary (JSON-serializable)."""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "errors": self.errors,
            "total_count": self.total_count,
            "page": self.page,
            "page_size": self.page_size,
            "metadata": self.metadata,
        }

    @property
    def has_next_page(self) -> bool:
        return (self.page * self.page_size) < self.total_count

    @property
    def has_prev_page(self) -> bool:
        return self.page > 1

    @property
    def total_pages(self) -> int:
        return (self.total_count + self.page_size - 1) // self.page_size if self.page_size > 0 else 0

    @classmethod
    def ok(cls, data: Any = None, total_count: int = 0, page: int = 1, page_size: int = 20, metadata: Dict = None) -> "QueryResult":
        """Create a success result."""
        return cls(
            success=True,
            data=data,
            total_count=total_count,
            page=page,
            page_size=page_size,
            metadata=metadata or {}
        )

    @classmethod
    def error(cls, message: str, errors: List[str] = None) -> "QueryResult":
        """Create an error result."""
        return cls(
            success=False,
            error=message,
            errors=errors or [message]
        )

    @classmethod
    def paginated(cls, items: List[Any], total: int, page: int, page_size: int) -> "QueryResult":
        """Create a paginated result."""
        return cls(
            success=True,
            data=items,
            total_count=total,
            page=page,
            page_size=page_size
        )


class QueryHandler(ABC):
    """Base class for all query handlers."""

    @abstractmethod
    def handle(self, query: Query) -> QueryResult:
        """
        Process a query and return a result.

        Args:
            query: The query to process

        Returns:
            QueryResult with data or error
        """
        pass

    @property
    @abstractmethod
    def query_type(self) -> str:
        """Return the query type this handler processes."""
        pass


class ListQueryHandler(QueryHandler, ABC):
    """Base class for list query handlers."""

    @property
    def query_type(self) -> str:
        return "list"


class GetByIdQueryHandler(QueryHandler, ABC):
    """Base class for get-by-id query handlers."""

    @property
    def query_type(self) -> str:
        return "get_by_id"


class SearchQueryHandler(QueryHandler, ABC):
    """Base class for search query handlers."""

    @property
    def query_type(self) -> str:
        return "search"
