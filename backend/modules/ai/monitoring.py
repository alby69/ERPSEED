"""
AI Monitoring & Cost Tracking Service
Tracks LLM usage, token costs, and success rates.
"""

import logging
import os
from typing import Dict, Any, Optional
from datetime import datetime
from backend.models import db, BaseModel
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON

class AIMetrics(db.Model):
    """Stores AI usage metrics for monitoring and billing."""
    __tablename__ = "ai_metrics"

    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, index=True)
    projectId = Column(Integer, index=True)
    userId = Column(Integer)
    provider = Column(String(50))
    model = Column(String(100))
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    estimated_cost = Column(Float, default=0.0)
    capability_used = Column(String(100))
    status = Column(String(20)) # success, error
    latency_ms = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)
    metadata_json = Column(JSON)

class AIMonitorService:
    """Service to track and report AI usage."""

    # Cost per 1k tokens (example rates)
    RATES = {
        "gpt-4o": {"prompt": 0.005, "completion": 0.015},
        "claude-3-5-sonnet": {"prompt": 0.003, "completion": 0.015},
        "deepseek-chat": {"prompt": 0.0001, "completion": 0.0002},
        "default": {"prompt": 0.002, "completion": 0.002}
    }

    def track_usage(self,
                    tenant_id: Optional[int],
                    projectId: int,
                    userId: int,
                    provider: str,
                    model: str,
                    prompt_tokens: int,
                    completion_tokens: int,
                    capability: str = None,
                    status: str = "success",
                    latency: int = 0,
                    meta: Dict = None):
        """Records a single AI interaction."""

        rate = self.RATES.get(model, self.RATES["default"])
        cost = ((prompt_tokens / 1000) * rate["prompt"]) + ((completion_tokens / 1000) * rate["completion"])

        metric = AIMetrics(
            tenant_id=tenant_id,
            projectId=projectId,
            userId=userId,
            provider=provider,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            estimated_cost=cost,
            capability_used=capability,
            status=status,
            latency_ms=latency,
            metadata_json=meta
        )

        try:
            db.session.add(metric)
            db.session.commit()
            return metric.id
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error tracking AI metrics: {e}")
            return None

    def get_summary(self, tenant_id: int = None, days: int = 30):
        """Returns usage summary for a tenant."""
        from sqlalchemy import func

        query = db.session.query(
            func.count(AIMetrics.id).label("total_calls"),
            func.sum(AIMetrics.total_tokens).label("total_tokens"),
            func.sum(AIMetrics.estimated_cost).label("total_cost")
        )

        if tenant_id:
            query = query.filter_by(tenant_id=tenant_id)

        return query.first()

# Global singleton
ai_monitor = AIMonitorService()
