"""
Marketplace API
REST API for browsing and managing marketplace blocks

DEPRECATED: Use backend.endpoints.marketplace for the new CQRS REST API.
This module is kept for reference only and is not registered.
"""
import warnings
warnings.warn(
    "backend.marketplace.api is deprecated. Use backend.endpoints.marketplace instead.",
    DeprecationWarning,
    stacklevel=2
)

from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from marshmallow import Schema, fields

from backend.extensions import db
from backend.marketplace.models import (
    Category,
    BlockListing,
    Review,
    PaymentTransaction,
    Author,
    create_default_categories,
)
from backend.marketplace import create_default_categories

blp = Blueprint(
    "marketplace",
    __name__,
    url_prefix="/api/marketplace",
    description="Marketplace API",
)


# === SCHEMAS ===


class ReviewCreateSchema(Schema):
    rating = fields.Integer(required=True)
    comment = fields.String()


class PaymentCreateSchema(Schema):
    listing_id = fields.Integer(required=True)
    amount = fields.Float(required=True)
    payment_method = fields.String(required=True)
    transaction_id = fields.String()


class ListingCreateSchema(Schema):
    name = fields.String(required=True)
    description = fields.String()
    category_id = fields.Integer(required=True)
    price = fields.Float()
    version = fields.String()
    tags = fields.List(fields.String())
    demo_url = fields.String()
    documentation_url = fields.String()


class CategorySchema(Schema):
    id = fields.Int()
    name = fields.Str()
    slug = fields.Str()
    description = fields.Str()
    icon = fields.Str()
    parent_id = fields.Int()
    block_count = fields.Int()

class AuthorSchema(Schema):
    id = fields.Int()
    display_name = fields.Str()
    avatar_url = fields.Str()
    bio = fields.Str()

class BlockListingSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    slug = fields.Str()
    description = fields.Str()
    price = fields.Float()
    currency = fields.Str()
    rating_avg = fields.Function(lambda obj: obj.rating_avg)
    rating_count = fields.Int()
    downloads = fields.Int()
    author = fields.Nested(AuthorSchema)
    category = fields.Nested(CategorySchema)
    thumbnail_url = fields.Str()

class BlockListingDetailSchema(BlockListingSchema):
    long_description = fields.Str()
    status = fields.Str()
    current_version = fields.Str()
    changelog = fields.Str()
    screenshots = fields.List(fields.Str())
    demo_url = fields.Str()
    created_at = fields.DateTime()

class PaginatedBlockListingSchema(Schema):
    items = fields.List(fields.Nested(BlockListingSchema))
    total = fields.Int()
    page = fields.Int()
    per_page = fields.Int()
    pages = fields.Int()


# === CATEGORIES ===


@blp.route("/categories")
class CategoryList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, CategorySchema(many=True))
    def get(self):
        """List all marketplace categories"""
        categories = Category.query.order_by(Category.order_index).all()
        # Manually add block_count to each category object before serialization
        for c in categories:
            c.block_count = len(c.listings) if c.listings else 0
        return categories


# === LISTINGS ===


@blp.route("/blocks")
class ListingList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, PaginatedBlockListingSchema)
    def get(self):
        """Browse marketplace blocks"""
        # Get query params
        category = request.args.get("category")
        search = request.args.get("q")
        status = request.args.get("status", "published")
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)

        query = BlockListing.query

        # Filter by status
        if status:
            query = query.filter(BlockListing.status == status)

        # Filter by category
        if category:
            cat = Category.query.filter_by(slug=category).first()
            if cat:
                query = query.filter(BlockListing.category_id == cat.id)

        # Search
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (BlockListing.title.ilike(search_term))
                | (BlockListing.description.ilike(search_term))
            )

        # Order by popularity
        query = query.order_by(BlockListing.downloads.desc())

        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return pagination


@blp.route("/blocks/<int:listing_id>")
class ListingDetail(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200, BlockListingDetailSchema)
    def get(self, listing_id):
        """Get block listing details"""
        listing = BlockListing.query.get_or_404(listing_id)

        return listing


# === REVIEWS ===


@blp.route("/blocks/<int:listing_id>/reviews")
class ReviewList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200)
    def get(self, listing_id):
        """Get reviews for a listing"""
        reviews = (
            Review.query.filter_by(listing_id=listing_id)
            .order_by(Review.created_at.desc())
            .all()
        )
        return [
            {
                "id": r.id,
                "rating": r.rating,
                "comment": r.comment,
                "is_verified_purchase": r.is_verified_purchase,
                "user": {
                    "id": r.user.id,
                    "email": r.user.email,
                },
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in reviews
        ]

    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(ReviewCreateSchema)
    @blp.response(201)
    def post(self, listing_id, review_data):
        """Add a review"""
        user_id = get_jwt_identity()

        review = Review(
            listing_id=listing_id,
            user_id=user_id,
            rating=review_data.get("rating"),
            comment=review_data.get("comment"),
        )

        # Update listing rating
        listing = BlockListing.query.get_or_404(listing_id)
        listing.rating_sum = (listing.rating_sum or 0) + review.rating
        listing.rating_count = (listing.rating_count or 0) + 1

        db.session.add(review)
        db.session.commit()

        return {"id": review.id, "message": "Review added"}


# === PAYMENTS ===


@blp.route("/payments")
class PaymentList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200)
    def get(self):
        """Get user's purchases"""
        user_id = get_jwt_identity()
        purchases = PaymentTransaction.query.filter_by(buyer_id=user_id).all()
        return [
            {
                "id": p.id,
                "listing_id": p.listing_id,
                "amount": float(p.amount),
                "currency": p.currency,
                "status": p.status,
                "payment_method": p.payment_method,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in purchases
        ]


@blp.route("/payments/process")
class PaymentProcess(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.arguments(PaymentCreateSchema)
    @blp.response(201)
    def post(self, payment_data):
        """Process a payment for a block"""
        user_id = get_jwt_identity()

        listing_id = payment_data.get("listing_id")
        payment_method = payment_data.get("payment_method", "stripe")

        listing = BlockListing.query.get_or_404(listing_id)

        payment = PaymentTransaction(
            listing_id=listing_id,
            buyer_id=user_id,
            amount=listing.price,
            currency=listing.currency or "EUR",
            status="pending",
            payment_method=payment_method,
        )

        # In production, this would integrate with Stripe/PayPal
        # For now, simulate completion
        payment.status = "completed"
        payment.transaction_id = f"txn_{payment.id}"

        db.session.add(payment)
        db.session.commit()

        return {
            "id": payment.id,
            "status": payment.status,
            "transaction_id": payment.transaction_id,
        }


# === INIT DEFAULT CATEGORIES ===


@blp.route("/init")
class MarketplaceInit(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200)
    def post(self):
        """Initialize marketplace with default categories"""
        create_default_categories()
        return {"message": "Marketplace initialized"}


# === MY LISTINGS ===


@blp.route("/my-listings")
class MyListings(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    @blp.response(200)
    def get(self):
        """Get current user's listings"""
        user_id = get_jwt_identity()
        listings = BlockListing.query.filter_by(author_id=user_id).all()
        return [
            {
                "id": l.id,
                "title": l.title,
                "slug": l.slug,
                "status": l.status,
                "downloads": l.downloads,
                "rating_avg": l.rating_avg,
                "price": float(l.price) if l.price else 0,
                "created_at": l.created_at.isoformat() if l.created_at else None,
            }
            for l in listings
        ]
