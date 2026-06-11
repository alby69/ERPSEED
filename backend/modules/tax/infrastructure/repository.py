import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class TaxRateRepository:
    def __init__(self, db=None):
        from backend.extensions import db as _db
        self.db = db or _db

    def _get_model_class(self):
        from backend.models import TaxRate
        return TaxRate

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        TaxRate = self._get_model_class()
        rate = TaxRate()
        for key, value in data.items():
            if hasattr(rate, key) and value is not None:
                setattr(rate, key, value)
        self.db.session.add(rate)
        self.db.session.commit()
        return self._to_dict(rate)

    def find_by_id(self, tax_rate_id: int, tenant_id: int) -> Optional[Dict[str, Any]]:
        TaxRate = self._get_model_class()
        rate = TaxRate.query.filter_by(id=tax_rate_id, tenant_id=tenant_id).first()
        if not rate:
            return None
        return self._to_dict(rate)

    def find_by_code(self, code: str, tenant_id: int) -> Optional[Dict[str, Any]]:
        TaxRate = self._get_model_class()
        rate = TaxRate.query.filter_by(code=code, tenant_id=tenant_id).first()
        if not rate:
            return None
        return self._to_dict(rate)

    def find_all(
        self,
        tenant_id: int,
        search: str = None,
        is_active: bool = None,
        page: int = 1,
        per_page: int = 20,
    ) -> Dict[str, Any]:
        TaxRate = self._get_model_class()
        query = TaxRate.query.filter_by(tenant_id=tenant_id)

        if search:
            term = f"%{search}%"
            query = query.filter(
                (TaxRate.name.ilike(term)) |
                (TaxRate.code.ilike(term)) |
                (TaxRate.description.ilike(term))
            )
        if is_active is not None:
            query = query.filter_by(is_active=is_active)

        query = query.order_by(TaxRate.code.asc())
        total = query.count()
        items = query.offset((page - 1) * per_page).limit(per_page).all()

        return {
            "items": [self._to_dict(r) for r in items],
            "total": total,
            "page": page,
            "per_page": per_page,
        }

    def update(self, tax_rate_id: int, tenant_id: int, changes: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        TaxRate = self._get_model_class()
        rate = TaxRate.query.filter_by(id=tax_rate_id, tenant_id=tenant_id).first()
        if not rate:
            return None
        old_data = self._to_dict(rate)
        for key, value in changes.items():
            if hasattr(rate, key) and value is not None:
                setattr(rate, key, value)
        self.db.session.commit()
        new_data = self._to_dict(rate)
        return {"old": old_data, "new": new_data}

    def delete(self, tax_rate_id: int, tenant_id: int) -> Optional[Dict[str, Any]]:
        TaxRate = self._get_model_class()
        rate = TaxRate.query.filter_by(id=tax_rate_id, tenant_id=tenant_id).first()
        if not rate:
            return None
        data = self._to_dict(rate)
        self.db.session.delete(rate)
        self.db.session.commit()
        return data

    def _to_dict(self, rate) -> Dict[str, Any]:
        return {
            "id": rate.id,
            "tenant_id": rate.tenant_id,
            "code": rate.code,
            "name": rate.name,
            "rate": rate.rate,
            "description": rate.description,
            "is_active": rate.is_active,
            "valid_from": rate.valid_from.isoformat() if rate.valid_from else None,
            "valid_to": rate.valid_to.isoformat() if rate.valid_to else None,
            "created_at": rate.created_at.isoformat() if rate.created_at else None,
            "updated_at": rate.updated_at.isoformat() if rate.updated_at else None,
        }
