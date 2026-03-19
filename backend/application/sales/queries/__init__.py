"""
Read Model Queries for Sales Orders.

This module demonstrates true CQRS by separating read operations from write operations.
Read models are optimized for query performance and can include denormalized data.

Key differences from write model:
- Read-only operations (no commits)
- Optimized SQL with JOINs for complex queries
- Denormalized data for dashboard/reports
- No business logic, just data retrieval
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from abc import ABC, abstractmethod
import logging

from sqlalchemy import text

logger = logging.getLogger(__name__)


def _format_datetime(value):
    """Format a datetime/date value that could be a date, datetime, or string."""
    if value is None:
        return None
    if hasattr(value, 'isoformat'):
        return value.isoformat()
    return str(value)


@dataclass
class SalesOrderListQuery:
    """Query for listing sales orders with filtering and pagination."""
    tenant_id: int
    status: Optional[str] = None
    customer_id: Optional[int] = None
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    search: Optional[str] = None
    page: int = 1
    page_size: int = 20


@dataclass
class SalesOrderDetailQuery:
    """Query for getting a single sales order with full details."""
    order_id: int
    tenant_id: int


@dataclass
class SalesOrderSummary:
    """Read-only summary of a sales order."""
    id: int
    number: str
    date: str
    customer_id: int
    customer_name: str
    status: str
    total_amount: float
    line_count: int
    created_at: str
    updated_at: str


@dataclass
class SalesOrderDetail:
    """Read-only detailed view of a sales order with all related data."""
    id: int
    number: str
    date: str
    customer_id: int
    customer_name: str
    status: str
    total_amount: float
    notes: str
    lines: List[Dict[str, Any]]
    created_at: str
    updated_at: str


@dataclass
class SalesOrderListResult:
    """Result of a sales order list query with pagination."""
    items: List[SalesOrderSummary]
    total: int
    page: int
    page_size: int
    has_next: bool


class BaseQueryHandler(ABC):
    """Base class for all query handlers."""
    
    def __init__(self, db):
        self.db = db
    
    @abstractmethod
    def handle(self, query):
        """Handle the query and return results."""
        pass


class SalesOrderReadRepository:
    """
    Read-only repository for sales orders.
    
    This repository is optimized for query operations and should NOT be used
    for writes. It demonstrates the CQRS pattern by separating read concerns
    from write concerns.
    
    Features:
    - Optimized SQL with proper JOINs
    - Denormalized data for performance
    - No business logic
    - No commits (read-only)
    """
    
    def __init__(self, db=None):
        from backend.extensions import db as _db
        self.db = db or _db
    
    def list_orders(self, query: SalesOrderListQuery) -> SalesOrderListResult:
        """
        List sales orders with filters and pagination.
        
        Uses optimized SQL with LEFT JOINs for customer name retrieval.
        """
        params = {
            'tenant_id': query.tenant_id,
            'limit': query.page_size,
            'offset': (query.page - 1) * query.page_size,
        }
        
        where_clauses = ['so.tenant_id = :tenant_id']
        
        if query.status:
            where_clauses.append('so.status = :status')
            params['status'] = query.status
        
        if query.customer_id:
            where_clauses.append('so.customer_id = :customer_id')
            params['customer_id'] = query.customer_id
        
        if query.from_date:
            where_clauses.append('so.date >= :from_date')
            params['from_date'] = query.from_date.isoformat()
        
        if query.to_date:
            where_clauses.append('so.date <= :to_date')
            params['to_date'] = query.to_date.isoformat()
        
        if query.search:
            where_clauses.append('(so.number ILIKE :search OR so.notes ILIKE :search)')
            params['search'] = f'%{query.search}%'
        
        where_sql = ' AND '.join(where_clauses)
        
        count_sql = text(f"""
            SELECT COUNT(*) as total
            FROM sales_orders so
            WHERE {where_sql}
        """)
        
        items_sql = text(f"""
            SELECT 
                so.id,
                so.number,
                so.date,
                so.customer_id,
                COALESCE(s.nome, 'Unknown') as customer_name,
                so.status,
                so.total_amount,
                COUNT(sol.id) as line_count,
                so.created_at,
                so.updated_at
            FROM sales_orders so
            LEFT JOIN soggetti s ON so.customer_id = s.id
            LEFT JOIN sales_order_lines sol ON so.id = sol.order_id
            WHERE {where_sql}
            GROUP BY so.id, so.number, so.date, so.customer_id, s.nome, so.status, so.total_amount, so.created_at, so.updated_at
            ORDER BY so.date DESC, so.created_at DESC
            LIMIT :limit OFFSET :offset
        """)
        
        count_result = self.db.session.execute(count_sql, params).fetchone()
        total = count_result.total if count_result else 0
        
        items_result = self.db.session.execute(items_sql, params).fetchall()
        
        items = [
            SalesOrderSummary(
                id=row.id,
                number=row.number,
                date=_format_datetime(row.date),
                customer_id=row.customer_id,
                customer_name=row.customer_name,
                status=row.status,
                total_amount=float(row.total_amount) if row.total_amount else 0,
                line_count=row.line_count,
                created_at=_format_datetime(row.created_at),
                updated_at=_format_datetime(row.updated_at),
            )
            for row in items_result
        ]
        
        return SalesOrderListResult(
            items=items,
            total=total,
            page=query.page,
            page_size=query.page_size,
            has_next=(query.page * query.page_size) < total,
        )
    
    def get_order_detail(self, query: SalesOrderDetailQuery) -> Optional[SalesOrderDetail]:
        """
        Get detailed information about a single sales order.
        
        Uses optimized SQL with all JOINs to avoid N+1 queries.
        """
        sql = text("""
            SELECT 
                so.id,
                so.number,
                so.date,
                so.customer_id,
                COALESCE(s.nome, 'Unknown') as customer_name,
                so.status,
                so.total_amount,
                so.notes,
                so.created_at,
                so.updated_at
            FROM sales_orders so
            LEFT JOIN soggetti s ON so.customer_id = s.id
            WHERE so.id = :order_id AND so.tenant_id = :tenant_id
        """)
        
        order_result = self.db.session.execute(sql, {
            'order_id': query.order_id,
            'tenant_id': query.tenant_id,
        }).fetchone()
        
        if not order_result:
            return None
        
        lines_sql = text("""
            SELECT 
                sol.id,
                sol.product_id,
                COALESCE(p.name, sol.description) as product_name,
                sol.description,
                sol.quantity,
                sol.unit_price,
                sol.total_price
            FROM sales_order_lines sol
            LEFT JOIN products p ON sol.product_id = p.id
            WHERE sol.order_id = :order_id
            ORDER BY sol.id
        """)
        
        lines_result = self.db.session.execute(lines_sql, {
            'order_id': query.order_id,
        }).fetchall()
        
        lines = [
            {
                'id': row.id,
                'product_id': row.product_id,
                'product_name': row.product_name,
                'description': row.description,
                'quantity': row.quantity,
                'unit_price': float(row.unit_price) if row.unit_price else 0,
                'total_price': float(row.total_price) if row.total_price else 0,
            }
            for row in lines_result
        ]
        
        return SalesOrderDetail(
            id=order_result.id,
            number=order_result.number,
            date=_format_datetime(order_result.date),
            customer_id=order_result.customer_id,
            customer_name=order_result.customer_name,
            status=order_result.status,
            total_amount=float(order_result.total_amount) if order_result.total_amount else 0,
            notes=order_result.notes,
            lines=lines,
            created_at=_format_datetime(order_result.created_at),
            updated_at=_format_datetime(order_result.updated_at),
        )
    
    def get_order_stats(self, tenant_id: int, from_date: date = None, to_date: date = None) -> Dict[str, Any]:
        """
        Get aggregated statistics for sales orders.
        
        Useful for dashboards and reports.
        """
        params = {'tenant_id': tenant_id}
        where_clauses = ['tenant_id = :tenant_id']
        
        if from_date:
            where_clauses.append('date >= :from_date')
            params['from_date'] = from_date.isoformat()
        
        if to_date:
            where_clauses.append('date <= :to_date')
            params['to_date'] = to_date.isoformat()
        
        where_sql = ' AND '.join(where_clauses)
        
        sql = text(f"""
            SELECT 
                COUNT(*) as total_orders,
                SUM(total_amount) as total_revenue,
                AVG(total_amount) as avg_order_value,
                COUNT(CASE WHEN status = 'confirmed' THEN 1 END) as confirmed,
                COUNT(CASE WHEN status = 'draft' THEN 1 END) as draft,
                COUNT(CASE WHEN status = 'cancelled' THEN 1 END) as cancelled
            FROM sales_orders
            WHERE {where_sql}
        """)
        
        result = self.db.session.execute(sql, params).fetchone()
        
        return {
            'total_orders': result.total_orders or 0,
            'total_revenue': float(result.total_revenue) if result.total_revenue else 0,
            'avg_order_value': float(result.avg_order_value) if result.avg_order_value else 0,
            'confirmed_orders': result.confirmed or 0,
            'draft_orders': result.draft or 0,
            'cancelled_orders': result.cancelled or 0,
        }


class SalesOrderListQueryHandler:
    """Handler for listing sales orders with read model optimization."""
    
    def __init__(self, db=None):
        self.repository = SalesOrderReadRepository(db)
    
    def handle(self, query: SalesOrderListQuery) -> SalesOrderListResult:
        """Handle list query using read repository."""
        return self.repository.list_orders(query)


class SalesOrderDetailQueryHandler:
    """Handler for getting sales order details with read model optimization."""
    
    def __init__(self, db=None):
        self.repository = SalesOrderReadRepository(db)
    
    def handle(self, query: SalesOrderDetailQuery) -> Optional[SalesOrderDetail]:
        """Handle detail query using read repository."""
        return self.repository.get_order_detail(query)


class SalesOrderStatsQueryHandler:
    """Handler for getting sales order statistics."""
    
    def __init__(self, db=None):
        self.repository = SalesOrderReadRepository(db)
    
    def handle(self, tenant_id: int, from_date: date = None, to_date: date = None) -> Dict[str, Any]:
        """Handle stats query using read repository."""
        return self.repository.get_order_stats(tenant_id, from_date, to_date)
