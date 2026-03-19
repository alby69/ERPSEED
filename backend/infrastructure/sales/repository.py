"""
Sales Repository - SQLAlchemy implementation for Sales Orders.
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime, date

logger = logging.getLogger(__name__)


class SalesOrderRepository:
    def __init__(self, db=None): self.db = db
    
    def _get_order_class(self):
        from backend.models import SalesOrder
        return SalesOrder
    
    def _get_line_class(self):
        from backend.models import SalesOrderLine
        return SalesOrderLine
    
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        SalesOrder = self._get_order_class(); SalesOrderLine = self._get_line_class()
        order = SalesOrder()
        order.tenant_id = data.get("tenant_id", 0); order.number = data.get("number", "")
        order.date = datetime.strptime(data["date"], "%Y-%m-%d").date() if data.get("date") else date.today()
        order.customer_id = data.get("customer_id", 0); order.notes = data.get("notes", ""); order.status = "draft"
        total = 0
        for line_data in data.get("lines", []):
            line = SalesOrderLine(); line.tenant_id = order.tenant_id
            line.product_id = line_data.get("product_id", 0); line.description = line_data.get("description", "")
            line.quantity = line_data.get("quantity", 0); line.unit_price = line_data.get("unit_price", 0)
            line.total_price = line.quantity * line.unit_price; total += line.total_price
            order.lines.append(line)
        order.total_amount = total
        self.db.session.add(order); self.db.session.commit()
        return self._to_dict(order)
    
    def find_by_id(self, order_id: int, tenant_id: int) -> Optional[Dict[str, Any]]:
        SalesOrder = self._get_order_class()
        order = SalesOrder.query.filter_by(id=order_id, tenant_id=tenant_id).first()
        return self._to_dict(order) if order else None
    
    def find_all(self, tenant_id: int, search: str = None, status: str = None, customer_id: int = None,
                 page: int = 1, per_page: int = 20, sort_by: str = "date", sort_order: str = "desc") -> Dict[str, Any]:
        SalesOrder = self._get_order_class()
        query = SalesOrder.query.filter_by(tenant_id=tenant_id)
        if search: query = query.filter(SalesOrder.number.ilike(f"%{search}%"))
        if status: query = query.filter_by(status=status)
        if customer_id: query = query.filter_by(customer_id=customer_id)
        total = query.count()
        sort_column = getattr(SalesOrder, sort_by, SalesOrder.date)
        query = query.order_by(sort_column.desc() if sort_order == "desc" else sort_column.asc())
        items = query.offset((page - 1) * per_page).limit(per_page).all()
        return {"items": [self._to_dict(o) for o in items], "total": total, "page": page, "per_page": per_page}
    
    def update(self, order_id: int, tenant_id: int, changes: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        SalesOrder = self._get_order_class()
        order = SalesOrder.query.filter_by(id=order_id, tenant_id=tenant_id).first()
        if not order: return None
        old_data = self._to_dict(order)
        for key, value in changes.items():
            if key == "date" and value: value = datetime.strptime(value, "%Y-%m-%d").date()
            if hasattr(order, key): setattr(order, key, value)
        self.db.session.commit()
        return {"old": old_data, "new": self._to_dict(order)}
    
    def delete(self, order_id: int, tenant_id: int) -> Optional[Dict[str, Any]]:
        SalesOrder = self._get_order_class()
        order = SalesOrder.query.filter_by(id=order_id, tenant_id=tenant_id).first()
        if not order: return None
        order_data = self._to_dict(order)
        self.db.session.delete(order); self.db.session.commit()
        return order_data
    
    def confirm(self, order_id: int, tenant_id: int) -> Optional[Dict[str, Any]]:
        return self.update(order_id, tenant_id, {"status": "confirmed"})
    
    def cancel(self, order_id: int, tenant_id: int) -> Optional[Dict[str, Any]]:
        return self.update(order_id, tenant_id, {"status": "cancelled"})
    
    def check_can_delete(self, order_id: int, tenant_id: int) -> Dict[str, Any]:
        SalesOrder = self._get_order_class()
        order = SalesOrder.query.filter_by(id=order_id, tenant_id=tenant_id).first()
        if not order: return {"can_delete": False, "reason": "Order not found"}
        if order.status not in ["draft", "cancelled"]: return {"can_delete": False, "reason": f"Cannot delete order with status '{order.status}'"}
        return {"can_delete": True}
    
    def _to_dict(self, order) -> Dict[str, Any]:
        return {"id": order.id, "tenant_id": order.tenant_id, "number": order.number,
            "date": order.date.isoformat() if order.date else None, "customer_id": order.customer_id,
            "status": order.status, "total_amount": order.total_amount, "notes": order.notes,
            "lines": [{"id": l.id, "product_id": l.product_id, "description": l.description,
                "quantity": l.quantity, "unit_price": l.unit_price, "total_price": l.total_price} for l in order.lines],
            "created_at": order.created_at.isoformat() if order.created_at else None,
            "updated_at": order.updated_at.isoformat() if order.updated_at else None}
