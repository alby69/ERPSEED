"""
Marketplace Commands.

CQRS commands for marketplace operations.
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime


@dataclass
class CreateListingCommand:
    """Command to create a new marketplace listing."""
    block_id: int = 0
    author_id: int = 0
    category_id: Optional[int] = None
    title: str = ""
    slug: str = ""
    description: str = ""
    long_description: str = ""
    price: float = 0.0
    currency: str = "EUR"
    thumbnail_url: str = ""
    screenshots: List[str] = field(default_factory=list)
    demo_url: str = ""
    tenant_id: Optional[int] = None
    user_id: Optional[int] = None
    entity_id: int = 0
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CreateListingCommand":
        return cls(
            block_id=data.get("block_id", 0),
            author_id=data.get("author_id", 0),
            category_id=data.get("category_id"),
            title=data.get("title", ""),
            slug=data.get("slug", ""),
            description=data.get("description", ""),
            long_description=data.get("long_description", ""),
            price=float(data.get("price", 0)),
            currency=data.get("currency", "EUR"),
            thumbnail_url=data.get("thumbnail_url", ""),
            screenshots=data.get("screenshots", []),
            demo_url=data.get("demo_url", ""),
            tenant_id=data.get("tenant_id"),
            user_id=data.get("user_id"),
        )
    
    def to_payload(self) -> Dict[str, Any]:
        return {
            "block_id": self.block_id,
            "author_id": self.author_id,
            "category_id": self.category_id,
            "title": self.title,
            "slug": self.slug,
            "description": self.description,
            "long_description": self.long_description,
            "price": self.price,
            "currency": self.currency,
            "thumbnail_url": self.thumbnail_url,
            "screenshots": self.screenshots,
            "demo_url": self.demo_url,
            "status": "draft",
        }


@dataclass
class PublishListingCommand:
    """Command to publish a listing."""
    listing_id: int = 0
    tenant_id: Optional[int] = None
    user_id: Optional[int] = None
    entity_id: int = 0
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PublishListingCommand":
        return cls(
            listing_id=data.get("listing_id", data.get("entity_id", 0)),
            tenant_id=data.get("tenant_id"),
            user_id=data.get("user_id"),
        )


@dataclass
class RejectListingCommand:
    """Command to reject a listing."""
    listing_id: int = 0
    reason: str = ""
    tenant_id: Optional[int] = None
    user_id: Optional[int] = None
    entity_id: int = 0
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RejectListingCommand":
        return cls(
            listing_id=data.get("listing_id", data.get("entity_id", 0)),
            reason=data.get("reason", ""),
            tenant_id=data.get("tenant_id"),
            user_id=data.get("user_id"),
        )


@dataclass
class CreateReviewCommand:
    """Command to create a review."""
    listing_id: int = 0
    user_id: int = 0
    rating: int = 0
    comment: str = ""
    is_verified_purchase: bool = False
    tenant_id: Optional[int] = None
    entity_id: int = 0
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CreateReviewCommand":
        return cls(
            listing_id=data.get("listing_id", 0),
            user_id=data.get("user_id", 0),
            rating=int(data.get("rating", 0)),
            comment=data.get("comment", ""),
            is_verified_purchase=data.get("is_verified_purchase", False),
            tenant_id=data.get("tenant_id"),
        )
    
    def to_payload(self) -> Dict[str, Any]:
        return {
            "listing_id": self.listing_id,
            "user_id": self.user_id,
            "rating": self.rating,
            "comment": self.comment,
            "is_verified_purchase": self.is_verified_purchase,
        }


@dataclass
class ProcessPaymentCommand:
    """Command to process a payment."""
    listing_id: int = 0
    buyer_id: int = 0
    payment_method: str = ""
    amount: float = 0.0
    currency: str = "EUR"
    tenant_id: Optional[int] = None
    user_id: Optional[int] = None
    entity_id: int = 0
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProcessPaymentCommand":
        return cls(
            listing_id=data.get("listing_id", 0),
            buyer_id=data.get("buyer_id", data.get("user_id", 0)),
            payment_method=data.get("payment_method", ""),
            amount=float(data.get("amount", 0)),
            currency=data.get("currency", "EUR"),
            tenant_id=data.get("tenant_id"),
            user_id=data.get("user_id"),
        )
    
    def to_payload(self) -> Dict[str, Any]:
        return {
            "listing_id": self.listing_id,
            "buyer_id": self.buyer_id,
            "amount": self.amount,
            "currency": self.currency,
            "status": "pending",
            "payment_method": self.payment_method,
        }


@dataclass
class BrowseListingsCommand:
    """Query to browse marketplace listings."""
    status: str = "published"
    category: str = None
    search: str = None
    page: int = 1
    per_page: int = 20
    tenant_id: Optional[int] = None
    user_id: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BrowseListingsCommand":
        pagination = data.get("pagination", {})
        return cls(
            status=data.get("status", "published"),
            category=data.get("category"),
            search=data.get("search"),
            page=pagination.get("page", data.get("page", 1)),
            per_page=pagination.get("per_page", data.get("per_page", 20)),
            tenant_id=data.get("tenant_id"),
            user_id=data.get("user_id"),
        )


@dataclass
class GetListingCommand:
    """Query to get a single listing."""
    listing_id: int = 0
    tenant_id: Optional[int] = None
    user_id: Optional[int] = None
    entity_id: int = 0
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GetListingCommand":
        return cls(
            listing_id=data.get("listing_id", data.get("entity_id", 0)),
            tenant_id=data.get("tenant_id"),
            user_id=data.get("user_id"),
        )


@dataclass
class GetCategoryListCommand:
    """Query to get all categories."""
    tenant_id: Optional[int] = None
    user_id: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GetCategoryListCommand":
        return cls(
            tenant_id=data.get("tenant_id"),
            user_id=data.get("user_id"),
        )


@dataclass
class GetListingReviewsCommand:
    """Query to get reviews for a listing."""
    listing_id: int = 0
    tenant_id: Optional[int] = None
    user_id: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GetListingReviewsCommand":
        return cls(
            listing_id=data.get("listing_id", 0),
            tenant_id=data.get("tenant_id"),
            user_id=data.get("user_id"),
        )


@dataclass
class GetUserPurchasesCommand:
    """Query to get user's purchases."""
    buyer_id: int = 0
    tenant_id: Optional[int] = None
    user_id: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GetUserPurchasesCommand":
        return cls(
            buyer_id=data.get("buyer_id", data.get("user_id", 0)),
            tenant_id=data.get("tenant_id"),
            user_id=data.get("user_id"),
        )


@dataclass
class GetAuthorListingsCommand:
    """Query to get author's listings."""
    author_id: int = 0
    tenant_id: Optional[int] = None
    user_id: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GetAuthorListingsCommand":
        return cls(
            author_id=data.get("author_id", data.get("user_id", 0)),
            tenant_id=data.get("tenant_id"),
            user_id=data.get("user_id"),
        )
