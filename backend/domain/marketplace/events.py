"""
Marketplace Domain Events.

Events published by the marketplace domain.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional


@dataclass
class MarketplaceEvent:
    """Base event for marketplace."""
    event_id: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    tenant_id: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "tenant_id": self.tenant_id,
        }


@dataclass
class ListingCreatedEvent(MarketplaceEvent):
    """Published when a new listing is created."""
    listing_id: int = 0
    author_id: int = 0
    title: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "event_type": "listing.created",
            "listing_id": self.listing_id,
            "author_id": self.author_id,
            "title": self.title,
        })
        return base


@dataclass
class ListingPublishedEvent(MarketplaceEvent):
    """Published when a listing is published."""
    listing_id: int = 0
    author_id: int = 0
    title: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "event_type": "listing.published",
            "listing_id": self.listing_id,
            "author_id": self.author_id,
            "title": self.title,
        })
        return base


@dataclass
class ListingRejectedEvent(MarketplaceEvent):
    """Published when a listing is rejected."""
    listing_id: int = 0
    author_id: int = 0
    reason: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "event_type": "listing.rejected",
            "listing_id": self.listing_id,
            "author_id": self.author_id,
            "reason": self.reason,
        })
        return base


@dataclass
class ReviewCreatedEvent(MarketplaceEvent):
    """Published when a new review is created."""
    review_id: int = 0
    listing_id: int = 0
    user_id: int = 0
    rating: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "event_type": "review.created",
            "review_id": self.review_id,
            "listing_id": self.listing_id,
            "user_id": self.user_id,
            "rating": self.rating,
        })
        return base


@dataclass
class PaymentCompletedEvent(MarketplaceEvent):
    """Published when a payment is completed."""
    payment_id: int = 0
    listing_id: int = 0
    buyer_id: int = 0
    author_id: int = 0
    amount: float = 0.0
    currency: str = "EUR"
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "event_type": "payment.completed",
            "payment_id": self.payment_id,
            "listing_id": self.listing_id,
            "buyer_id": self.buyer_id,
            "author_id": self.author_id,
            "amount": self.amount,
            "currency": self.currency,
        })
        return base
