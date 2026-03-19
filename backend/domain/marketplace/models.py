"""
Marketplace Domain Models.

Pure Python dataclasses for marketplace entities.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List
from decimal import Decimal


@dataclass
class Category:
    """Marketplace category for organizing blocks."""
    id: Optional[int] = None
    name: str = ""
    slug: str = ""
    description: str = ""
    icon: str = ""
    parent_id: Optional[int] = None
    order_index: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "name": self.name, "slug": self.slug,
            "description": self.description, "icon": self.icon,
            "parent_id": self.parent_id, "order_index": self.order_index,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Category":
        return cls(
            id=data.get("id"), name=data.get("name", ""), slug=data.get("slug", ""),
            description=data.get("description", ""), icon=data.get("icon", ""),
            parent_id=data.get("parent_id"), order_index=data.get("order_index", 0),
        )
    
    def validate(self) -> tuple[bool, List[str]]:
        errors = []
        if not self.name: errors.append("Category name is required")
        if not self.slug: errors.append("Slug is required")
        return len(errors) == 0, errors


@dataclass
class BlockListing:
    """Published block in the marketplace."""
    id: Optional[int] = None
    block_id: int = 0
    author_id: int = 0
    category_id: Optional[int] = None
    title: str = ""
    slug: str = ""
    description: str = ""
    long_description: str = ""
    price: Decimal = Decimal("0.00")
    currency: str = "EUR"
    thumbnail_url: str = ""
    screenshots: List[str] = field(default_factory=list)
    demo_url: str = ""
    downloads: int = 0
    rating_sum: int = 0
    rating_count: int = 0
    status: str = "draft"
    rejection_reason: str = ""
    published_at: Optional[datetime] = None
    current_version: str = ""
    changelog: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def rating_avg(self) -> float:
        if self.rating_count == 0:
            return 0.0
        return round(self.rating_sum / self.rating_count, 2)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "block_id": self.block_id, "author_id": self.author_id,
            "category_id": self.category_id, "title": self.title, "slug": self.slug,
            "description": self.description, "long_description": self.long_description,
            "price": float(self.price), "currency": self.currency,
            "thumbnail_url": self.thumbnail_url, "screenshots": self.screenshots,
            "demo_url": self.demo_url, "downloads": self.downloads,
            "rating_sum": self.rating_sum, "rating_count": self.rating_count,
            "rating_avg": self.rating_avg, "status": self.status,
            "rejection_reason": self.rejection_reason,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "current_version": self.current_version, "changelog": self.changelog,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BlockListing":
        return cls(
            id=data.get("id"), block_id=data.get("block_id", 0),
            author_id=data.get("author_id", 0), category_id=data.get("category_id"),
            title=data.get("title", ""), slug=data.get("slug", ""),
            description=data.get("description", ""), long_description=data.get("long_description", ""),
            price=Decimal(str(data.get("price", 0))),
            currency=data.get("currency", "EUR"),
            thumbnail_url=data.get("thumbnail_url", ""),
            screenshots=data.get("screenshots", []),
            demo_url=data.get("demo_url", ""), downloads=data.get("downloads", 0),
            rating_sum=data.get("rating_sum", 0), rating_count=data.get("rating_count", 0),
            status=data.get("status", "draft"),
            rejection_reason=data.get("rejection_reason", ""),
            published_at=data.get("published_at"),
            current_version=data.get("current_version", ""), changelog=data.get("changelog", ""),
        )
    
    def validate(self) -> tuple[bool, List[str]]:
        errors = []
        if not self.title: errors.append("Title is required")
        if not self.slug: errors.append("Slug is required")
        if self.status not in ["draft", "pending_review", "published", "rejected"]:
            errors.append(f"Invalid status: {self.status}")
        return len(errors) == 0, errors


@dataclass
class Review:
    """User review for a marketplace listing."""
    id: Optional[int] = None
    listing_id: int = 0
    user_id: int = 0
    rating: int = 0
    comment: str = ""
    is_verified_purchase: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "listing_id": self.listing_id, "user_id": self.user_id,
            "rating": self.rating, "comment": self.comment,
            "is_verified_purchase": self.is_verified_purchase,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Review":
        return cls(
            id=data.get("id"), listing_id=data.get("listing_id", 0),
            user_id=data.get("user_id", 0), rating=data.get("rating", 0),
            comment=data.get("comment", ""), is_verified_purchase=data.get("is_verified_purchase", False),
        )
    
    def validate(self) -> tuple[bool, List[str]]:
        errors = []
        if self.rating < 1 or self.rating > 5:
            errors.append("Rating must be between 1 and 5")
        return len(errors) == 0, errors


@dataclass
class PaymentTransaction:
    """Payment record for purchased blocks."""
    id: Optional[int] = None
    listing_id: int = 0
    buyer_id: int = 0
    amount: Decimal = Decimal("0.00")
    currency: str = "EUR"
    status: str = "pending"
    payment_method: str = ""
    transaction_id: str = ""
    payment_data: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "listing_id": self.listing_id, "buyer_id": self.buyer_id,
            "amount": float(self.amount), "currency": self.currency, "status": self.status,
            "payment_method": self.payment_method, "transaction_id": self.transaction_id,
            "payment_data": self.payment_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PaymentTransaction":
        return cls(
            id=data.get("id"), listing_id=data.get("listing_id", 0),
            buyer_id=data.get("buyer_id", 0),
            amount=Decimal(str(data.get("amount", 0))),
            currency=data.get("currency", "EUR"), status=data.get("status", "pending"),
            payment_method=data.get("payment_method", ""),
            transaction_id=data.get("transaction_id", ""),
            payment_data=data.get("payment_data", {}),
            completed_at=data.get("completed_at"),
        )


@dataclass
class Author:
    """Marketplace author profile."""
    id: Optional[int] = None
    user_id: int = 0
    display_name: str = ""
    bio: str = ""
    avatar_url: str = ""
    website: str = ""
    total_downloads: int = 0
    total_revenue: Decimal = Decimal("0.00")
    avg_rating: float = 0.0
    is_verified: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "user_id": self.user_id, "display_name": self.display_name,
            "bio": self.bio, "avatar_url": self.avatar_url, "website": self.website,
            "total_downloads": self.total_downloads, "total_revenue": float(self.total_revenue),
            "avg_rating": self.avg_rating, "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Author":
        return cls(
            id=data.get("id"), user_id=data.get("user_id", 0),
            display_name=data.get("display_name", ""), bio=data.get("bio", ""),
            avatar_url=data.get("avatar_url", ""), website=data.get("website", ""),
            total_downloads=data.get("total_downloads", 0),
            total_revenue=Decimal(str(data.get("total_revenue", 0))),
            avg_rating=data.get("avg_rating", 0.0), is_verified=data.get("is_verified", False),
        )
