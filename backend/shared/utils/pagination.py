"""
Pagination utilities.
"""

from dataclasses import dataclass
from typing import List, Any, Optional


@dataclass
class PaginationInfo:
    """Pagination metadata."""

    page: int
    per_page: int
    total: int
    pages: int

    @property
    def has_next(self) -> bool:
        return self.page < self.pages

    @property
    def has_prev(self) -> bool:
        return self.page > 1

    @property
    def start_index(self) -> int:
        return (self.page - 1) * self.per_page + 1

    @property
    def end_index(self) -> int:
        return min(self.page * self.per_page, self.total)


def paginate_result(
    items: List[Any], page: int = 1, per_page: int = 10, total: int = None
) -> tuple:
    """Paginate a list of items.

    Args:
        items: List of items to paginate
        page: Current page number (1-indexed)
        per_page: Items per page
        total: Total count (defaults to len(items))

    Returns:
        Tuple of (items, pagination_info)
    """
    if total is None:
        total = len(items)

    total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0

    pagination_info = PaginationInfo(
        page=page, per_page=per_page, total=total, pages=total_pages
    )

    start = (page - 1) * per_page
    end = start + per_page
    paginated_items = items[start:end]

    return paginated_items, pagination_info
