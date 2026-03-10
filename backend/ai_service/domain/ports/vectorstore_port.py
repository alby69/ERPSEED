"""
Vector Store Port - Interface for vector storage providers.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class Document:
    """Represents a document for vector storage."""

    def __init__(
        self,
        content: str,
        metadata: Dict[str, Any] = None,
        embedding: List[float] = None,
        doc_id: str = None,
    ):
        self.content = content
        self.metadata = metadata or {}
        self.embedding = embedding
        self.doc_id = doc_id


class SearchResult:
    """Represents a search result from vector store."""

    def __init__(
        self,
        document: Document,
        score: float = None,
    ):
        self.document = document
        self.score = score


class VectorStorePort(ABC):
    """
    Abstract port for vector storage providers.

    Implement this for RAG functionality.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the provider name."""
        pass

    @abstractmethod
    def add_documents(self, documents: List[Document]) -> List[str]:
        """
        Add documents to the vector store.

        Args:
            documents: List of Document objects

        Returns:
            List of document IDs
        """
        pass

    @abstractmethod
    def search(
        self,
        query: str,
        top_k: int = 5,
        filters: Dict = None,
    ) -> List[SearchResult]:
        """
        Search for similar documents.

        Args:
            query: Search query
            top_k: Number of results
            filters: Optional metadata filters

        Returns:
            List of SearchResult objects
        """
        pass

    @abstractmethod
    def delete(self, doc_ids: List[str]) -> bool:
        """
        Delete documents by ID.

        Args:
            doc_ids: List of document IDs to delete

        Returns:
            True if successful
        """
        pass

    def create_index(self, name: str, **kwargs) -> bool:
        """Create a new index/collection."""
        return True

    def list_indexes(self) -> List[str]:
        """List available indexes."""
        return []
