"""
Marketplace Repository - SQLAlchemy implementation.

Infrastructure layer handling persistence for marketplace entities.
"""
import logging
from typing import Optional, Dict, Any, List
from decimal import Decimal
from datetime import datetime

logger = logging.getLogger(__name__)


class CategoryRepository:
    """Repository for Category entity."""

    def __init__(self, db=None):
        self.db = db

    def _get_model(self):
        from backend.marketplace.models import Category
        return Category

    def find_by_id(self, category_id: int) -> Optional[Dict[str, Any]]:
        Category = self._get_model()
        category = Category.query.get(category_id)
        return self._to_dict(category) if category else None

    def find_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        Category = self._get_model()
        category = Category.query.filter_by(slug=slug).first()
        return self._to_dict(category) if category else None

    def find_all(self, parent_id: int = None) -> List[Dict[str, Any]]:
        Category = self._get_model()
        query = Category.query.order_by(Category.order_index)
        if parent_id is not None:
            query = query.filter_by(parent_id=parent_id)
        categories = query.all()
        result = []
        for c in categories:
            cat_dict = self._to_dict(c)
            cat_dict["block_count"] = len(c.listings) if c.listings else 0
            result.append(cat_dict)
        return result

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        Category = self._get_model()
        category = Category()
        for key, value in data.items():
            if hasattr(category, key):
                setattr(category, key, value)
        self.db.session.add(category)
        self.db.session.commit()
        return self._to_dict(category)

    def _to_dict(self, category) -> Dict[str, Any]:
        if not category:
            return None
        return {
            "id": category.id,
            "name": category.name,
            "slug": category.slug,
            "description": category.description,
            "icon": category.icon,
            "parent_id": category.parent_id,
            "order_index": category.order_index,
            "created_at": category.created_at.isoformat() if category.created_at else None,
            "updated_at": category.updated_at.isoformat() if category.updated_at else None,
        }


class ListingRepository:
    """Repository for BlockListing entity."""

    def __init__(self, db=None):
        self.db = db

    def _get_model(self):
        from backend.marketplace.models import BlockListing
        return BlockListing

    def find_by_id(self, listing_id: int) -> Optional[Dict[str, Any]]:
        Listing = self._get_model()
        listing = Listing.query.get(listing_id)
        return self._to_dict(listing) if listing else None

    def find_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        Listing = self._get_model()
        listing = Listing.query.filter_by(slug=slug).first()
        return self._to_dict(listing) if listing else None

    def find_by_block_id(self, block_id: int) -> Optional[Dict[str, Any]]:
        Listing = self._get_model()
        listing = Listing.query.filter_by(block_id=block_id).first()
        return self._to_dict(listing) if listing else None

    def find_all(
        self,
        status: str = "published",
        category_slug: str = None,
        search: str = None,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        Listing = self._get_model()
        query = Listing.query

        if status:
            query = query.filter_by(status=status)
        if category_slug:
            from backend.marketplace.models import Category
            cat = Category.query.filter_by(slug=category_slug).first()
            if cat:
                query = query.filter_by(category_id=cat.id)
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Listing.title.ilike(search_term)) | (Listing.description.ilike(search_term))
            )

        total = query.count()
        query = query.order_by(Listing.downloads.desc())
        items = query.offset((page - 1) * per_page).limit(per_page).all()

        return {
            "items": [self._to_dict(l) for l in items],
            "total": total,
            "page": page,
            "per_page": per_page,
        }

    def find_by_author(self, author_id: int) -> List[Dict[str, Any]]:
        Listing = self._get_model()
        listings = Listing.query.filter_by(author_id=author_id).order_by(Listing.created_at.desc()).all()
        return [self._to_dict(l) for l in listings]

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        Listing = self._get_model()
        listing = Listing()
        for key, value in data.items():
            if hasattr(listing, key):
                if key == "screenshots" and value is None:
                    value = []
                setattr(listing, key, value)
        self.db.session.add(listing)
        self.db.session.flush()
        return self._to_dict(listing)

    def update(self, listing_id: int, changes: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        Listing = self._get_model()
        listing = Listing.query.get(listing_id)
        if not listing:
            return None
        for key, value in changes.items():
            if hasattr(listing, key):
                setattr(listing, key, value)
        self.db.session.commit()
        return self._to_dict(listing)

    def update_status(self, listing_id: int, status: str, rejection_reason: str = None) -> Optional[Dict[str, Any]]:
        Listing = self._get_model()
        listing = Listing.query.get(listing_id)
        if not listing:
            return None
        listing.status = status
        if status == "published":
            listing.published_at = datetime.utcnow()
        if rejection_reason:
            listing.rejection_reason = rejection_reason
        self.db.session.commit()
        return self._to_dict(listing)

    def increment_rating(self, listing_id: int, rating: int) -> Optional[Dict[str, Any]]:
        Listing = self._get_model()
        listing = Listing.query.get(listing_id)
        if not listing:
            return None
        listing.rating_sum = (listing.rating_sum or 0) + rating
        listing.rating_count = (listing.rating_count or 0) + 1
        self.db.session.commit()
        return self._to_dict(listing)

    def increment_downloads(self, listing_id: int) -> Optional[Dict[str, Any]]:
        Listing = self._get_model()
        listing = Listing.query.get(listing_id)
        if not listing:
            return None
        listing.downloads = (listing.downloads or 0) + 1
        self.db.session.commit()
        return self._to_dict(listing)

    def _to_dict(self, listing) -> Dict[str, Any]:
        if not listing:
            return None
        return {
            "id": listing.id,
            "block_id": listing.block_id,
            "author_id": listing.author_id,
            "category_id": listing.category_id,
            "title": listing.title,
            "slug": listing.slug,
            "description": listing.description,
            "long_description": listing.long_description,
            "price": float(listing.price) if listing.price else 0.0,
            "currency": listing.currency,
            "thumbnail_url": listing.thumbnail_url,
            "screenshots": listing.screenshots or [],
            "demo_url": listing.demo_url,
            "downloads": listing.downloads or 0,
            "rating_sum": listing.rating_sum or 0,
            "rating_count": listing.rating_count or 0,
            "rating_avg": listing.rating_avg,
            "status": listing.status,
            "rejection_reason": listing.rejection_reason,
            "published_at": listing.published_at.isoformat() if listing.published_at else None,
            "current_version": listing.current_version,
            "changelog": listing.changelog,
            "created_at": listing.created_at.isoformat() if listing.created_at else None,
            "updated_at": listing.updated_at.isoformat() if listing.updated_at else None,
        }


class ReviewRepository:
    """Repository for Review entity."""

    def __init__(self, db=None):
        self.db = db

    def _get_model(self):
        from backend.marketplace.models import Review
        return Review

    def find_by_id(self, review_id: int) -> Optional[Dict[str, Any]]:
        Review = self._get_model()
        review = Review.query.get(review_id)
        return self._to_dict(review) if review else None

    def find_by_listing(self, listing_id: int) -> List[Dict[str, Any]]:
        Review = self._get_model()
        reviews = Review.query.filter_by(listing_id=listing_id).order_by(Review.created_at.desc()).all()
        return [self._to_dict(r) for r in reviews]

    def find_by_user_and_listing(self, user_id: int, listing_id: int) -> Optional[Dict[str, Any]]:
        Review = self._get_model()
        review = Review.query.filter_by(user_id=user_id, listing_id=listing_id).first()
        return self._to_dict(review) if review else None

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        Review = self._get_model()
        review = Review()
        for key, value in data.items():
            if hasattr(review, key):
                setattr(review, key, value)
        self.db.session.add(review)
        self.db.session.commit()
        return self._to_dict(review)

    def _to_dict(self, review) -> Dict[str, Any]:
        if not review:
            return None
        result = {
            "id": review.id,
            "listing_id": review.listing_id,
            "user_id": review.user_id,
            "rating": review.rating,
            "comment": review.comment,
            "is_verified_purchase": review.is_verified_purchase,
            "created_at": review.created_at.isoformat() if review.created_at else None,
            "updated_at": review.updated_at.isoformat() if review.updated_at else None,
        }
        if hasattr(review, "user") and review.user:
            result["user"] = {"id": review.user.id, "email": review.user.email}
        return result


class PaymentRepository:
    """Repository for PaymentTransaction entity."""

    def __init__(self, db=None):
        self.db = db

    def _get_model(self):
        from backend.marketplace.models import PaymentTransaction
        return PaymentTransaction

    def find_by_id(self, payment_id: int) -> Optional[Dict[str, Any]]:
        Payment = self._get_model()
        payment = Payment.query.get(payment_id)
        return self._to_dict(payment) if payment else None

    def find_by_buyer(self, buyer_id: int) -> List[Dict[str, Any]]:
        Payment = self._get_model()
        payments = Payment.query.filter_by(buyer_id=buyer_id).order_by(Payment.created_at.desc()).all()
        return [self._to_dict(p) for p in payments]

    def find_completed_by_buyer_and_listing(self, buyer_id: int, listing_id: int) -> Optional[Dict[str, Any]]:
        Payment = self._get_model()
        payment = Payment.query.filter_by(
            buyer_id=buyer_id, listing_id=listing_id, status="completed"
        ).first()
        return self._to_dict(payment) if payment else None

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        Payment = self._get_model()
        payment = Payment()
        for key, value in data.items():
            if hasattr(payment, key):
                setattr(payment, key, value)
        self.db.session.add(payment)
        self.db.session.flush()
        return self._to_dict(payment)

    def complete(self, payment_id: int, transaction_id: str) -> Optional[Dict[str, Any]]:
        Payment = self._get_model()
        payment = Payment.query.get(payment_id)
        if not payment:
            return None
        payment.status = "completed"
        payment.transaction_id = transaction_id
        payment.completed_at = datetime.utcnow()
        self.db.session.commit()
        return self._to_dict(payment)

    def _to_dict(self, payment) -> Dict[str, Any]:
        if not payment:
            return None
        return {
            "id": payment.id,
            "listing_id": payment.listing_id,
            "buyer_id": payment.buyer_id,
            "amount": float(payment.amount) if payment.amount else 0.0,
            "currency": payment.currency,
            "status": payment.status,
            "payment_method": payment.payment_method,
            "transaction_id": payment.transaction_id,
            "payment_data": payment.payment_data or {},
            "created_at": payment.created_at.isoformat() if payment.created_at else None,
            "completed_at": payment.completed_at.isoformat() if payment.completed_at else None,
        }


class AuthorRepository:
    """Repository for Author entity."""

    def __init__(self, db=None):
        self.db = db

    def _get_model(self):
        from backend.marketplace.models import Author
        return Author

    def find_by_user_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        Author = self._get_model()
        author = Author.query.filter_by(user_id=user_id).first()
        return self._to_dict(author) if author else None

    def find_by_id(self, author_id: int) -> Optional[Dict[str, Any]]:
        Author = self._get_model()
        author = Author.query.get(author_id)
        return self._to_dict(author) if author else None

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        Author = self._get_model()
        author = Author()
        for key, value in data.items():
            if hasattr(author, key):
                setattr(author, key, value)
        self.db.session.add(author)
        self.db.session.commit()
        return self._to_dict(author)

    def update_revenue(self, author_id: int, amount: float) -> Optional[Dict[str, Any]]:
        Author = self._get_model()
        author = Author.query.get(author_id)
        if not author:
            return None
        author.total_revenue = (author.total_revenue or 0) + amount
        self.db.session.commit()
        return self._to_dict(author)

    def increment_downloads(self, author_id: int) -> Optional[Dict[str, Any]]:
        Author = self._get_model()
        author = Author.query.get(author_id)
        if not author:
            return None
        author.total_downloads = (author.total_downloads or 0) + 1
        self.db.session.commit()
        return self._to_dict(author)

    def _to_dict(self, author) -> Dict[str, Any]:
        if not author:
            return None
        return {
            "id": author.id,
            "user_id": author.user_id,
            "display_name": author.display_name,
            "bio": author.bio,
            "avatar_url": author.avatar_url,
            "website": author.website,
            "total_downloads": author.total_downloads or 0,
            "total_revenue": float(author.total_revenue) if author.total_revenue else 0.0,
            "avg_rating": float(author.avg_rating) if author.avg_rating else 0.0,
            "is_verified": author.is_verified,
            "created_at": author.created_at.isoformat() if author.created_at else None,
            "updated_at": author.updated_at.isoformat() if author.updated_at else None,
        }
