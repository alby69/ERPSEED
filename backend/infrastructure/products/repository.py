"""
Product Repository - SQLAlchemy implementation for Products.

Infrastructure layer handling persistence.
"""
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class ProductRepository:
    """SQLAlchemy repository for Product entity."""
    
    def __init__(self, db=None):
        self.db = db
    
    def _get_model_class(self):
        from backend.models import Product
        return Product
    
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        Product = self._get_model_class()
        product = Product()
        for key, value in data.items():
            if hasattr(product, key):
                setattr(product, key, value)
        self.db.session.add(product)
        self.db.session.commit()
        return self._to_dict(product)
    
    def find_by_id(self, product_id: int, tenant_id: int) -> Optional[Dict[str, Any]]:
        Product = self._get_model_class()
        product = Product.query.filter_by(id=product_id, tenant_id=tenant_id).first()
        return self._to_dict(product) if product else None
    
    def find_by_code(self, code: str, tenant_id: int) -> Optional[Dict[str, Any]]:
        Product = self._get_model_class()
        product = Product.query.filter_by(code=code, tenant_id=tenant_id).first()
        return self._to_dict(product) if product else None
    
    def find_all(self, tenant_id: int, search: str = None, category: str = None, is_active: bool = None,
                 min_price: float = None, max_price: float = None, page: int = 1, per_page: int = 20,
                 sort_by: str = "name", sort_order: str = "asc") -> Dict[str, Any]:
        Product = self._get_model_class()
        query = Product.query.filter_by(tenant_id=tenant_id)
        if search:
            search_term = f"%{search}%"
            query = query.filter((Product.name.ilike(search_term)) | (Product.code.ilike(search_term)) | (Product.description.ilike(search_term)))
        if category: query = query.filter_by(category=category)
        if is_active is not None: query = query.filter_by(is_active=is_active)
        if min_price is not None: query = query.filter(Product.unit_price >= min_price)
        if max_price is not None: query = query.filter(Product.unit_price <= max_price)
        total = query.count()
        sort_column = getattr(Product, sort_by, Product.name)
        if sort_order == "desc": query = query.order_by(sort_column.desc())
        else: query = query.order_by(sort_column.asc())
        items = query.offset((page - 1) * per_page).limit(per_page).all()
        return {"items": [self._to_dict(p) for p in items], "total": total, "page": page, "per_page": per_page}
    
    def update(self, product_id: int, tenant_id: int, changes: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        Product = self._get_model_class()
        product = Product.query.filter_by(id=product_id, tenant_id=tenant_id).first()
        if not product: return None
        old_data = self._to_dict(product)
        for key, value in changes.items():
            if hasattr(product, key): setattr(product, key, value)
        self.db.session.commit()
        return {"old": old_data, "new": self._to_dict(product)}
    
    def delete(self, product_id: int, tenant_id: int) -> Optional[Dict[str, Any]]:
        Product = self._get_model_class()
        product = Product.query.filter_by(id=product_id, tenant_id=tenant_id).first()
        if not product: return None
        product_data = self._to_dict(product)
        self.db.session.delete(product)
        self.db.session.commit()
        return product_data
    
    def check_dependencies(self, product_id: int, tenant_id: int) -> Dict[str, Any]:
        from backend.models import SalesOrderLine, PurchaseOrderLine, ProductStock
        Product = self._get_model_class()
        product = Product.query.filter_by(id=product_id, tenant_id=tenant_id).first()
        if not product: return {"has_dependencies": False}
        sales_lines = SalesOrderLine.query.filter_by(product_id=product_id).count()
        purchase_lines = PurchaseOrderLine.query.filter_by(product_id=product_id).count()
        has_stock = ProductStock.query.filter_by(product_id=product_id).first() is not None
        return {"has_dependencies": sales_lines > 0 or purchase_lines > 0 or has_stock,
                "sales_order_lines": sales_lines, "purchase_order_lines": purchase_lines, "has_stock_records": has_stock}
    
    def _to_dict(self, product) -> Dict[str, Any]:
        return {"id": product.id, "tenant_id": product.tenant_id, "name": product.name, "code": product.code,
            "description": product.description, "unit_price": product.unit_price, "category": product.category,
            "sku": product.sku, "barcode": product.barcode, "is_active": product.is_active,
            "track_inventory": product.track_inventory, "current_stock": product.current_stock,
            "reorder_level": product.reorder_level, "unit_of_measure": product.unit_of_measure,
            "weight": product.weight, "dimensions": product.dimensions,
            "created_at": product.created_at.isoformat() if product.created_at else None,
            "updated_at": product.updated_at.isoformat() if product.updated_at else None}
