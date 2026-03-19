"""
Marketplace API - REST API for Marketplace operations.

This module provides Flask-Smorest Blueprint for Marketplace:
- Categories: Browse marketplace categories
- Listings: Browse, search, view marketplace blocks
- Reviews: View and create reviews
- Payments: Process payments for blocks
"""
import logging
from typing import Dict, Any
from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity

from backend.shared.handlers import CommandResult
from backend.application.marketplace.commands import (
    CreateListingCommand, PublishListingCommand, RejectListingCommand,
    CreateReviewCommand, ProcessPaymentCommand,
    BrowseListingsCommand, GetListingCommand, GetCategoryListCommand,
    GetListingReviewsCommand, GetUserPurchasesCommand, GetAuthorListingsCommand,
)
from backend.application.marketplace.handlers import (
    CreateListingHandler, PublishListingHandler, RejectListingHandler,
    CreateReviewHandler, ProcessPaymentHandler,
    BrowseListingsHandler, GetListingHandler, GetCategoryListHandler,
    GetListingReviewsHandler, GetUserPurchasesHandler, GetAuthorListingsHandler,
)
from backend.infrastructure.marketplace.repository import (
    CategoryRepository, ListingRepository, ReviewRepository,
    PaymentRepository, AuthorRepository,
)

logger = logging.getLogger(__name__)

blp = Blueprint("marketplace", __name__, url_prefix="/api/marketplace", description="Marketplace API")


class MarketplaceCommandExecutor:
    """Executes CQRS commands for Marketplace."""
    
    COMMAND_HANDLERS = {
        "CreateListing": CreateListingHandler,
        "PublishListing": PublishListingHandler,
        "RejectListing": RejectListingHandler,
        "CreateReview": CreateReviewHandler,
        "ProcessPayment": ProcessPaymentHandler,
        "BrowseListings": BrowseListingsHandler,
        "GetListing": GetListingHandler,
        "GetCategoryList": GetCategoryListHandler,
        "GetListingReviews": GetListingReviewsHandler,
        "GetUserPurchases": GetUserPurchasesHandler,
        "GetAuthorListings": GetAuthorListingsHandler,
    }
    
    def __init__(self):
        self._handlers = {}
        self._repositories = {}
        self._db = None
    
    @property
    def db(self):
        if self._db is None:
            from backend.extensions import db
            self._db = db
        return self._db
    
    @property
    def category_repo(self):
        if "category" not in self._repositories:
            self._repositories["category"] = CategoryRepository(db=self.db)
        return self._repositories["category"]
    
    @property
    def listing_repo(self):
        if "listing" not in self._repositories:
            self._repositories["listing"] = ListingRepository(db=self.db)
        return self._repositories["listing"]
    
    @property
    def review_repo(self):
        if "review" not in self._repositories:
            self._repositories["review"] = ReviewRepository(db=self.db)
        return self._repositories["review"]
    
    @property
    def payment_repo(self):
        if "payment" not in self._repositories:
            self._repositories["payment"] = PaymentRepository(db=self.db)
        return self._repositories["payment"]
    
    @property
    def author_repo(self):
        if "author" not in self._repositories:
            self._repositories["author"] = AuthorRepository(db=self.db)
        return self._repositories["author"]
    
    def _get_handler(self, command_name: str):
        if command_name not in self._handlers:
            handler_map = {
                "CreateListing": (CreateListingHandler, [self.listing_repo]),
                "PublishListing": (PublishListingHandler, [self.listing_repo]),
                "RejectListing": (RejectListingHandler, [self.listing_repo]),
                "CreateReview": (CreateReviewHandler, [self.review_repo, self.listing_repo]),
                "ProcessPayment": (ProcessPaymentHandler, [self.payment_repo, self.listing_repo, self.author_repo]),
                "BrowseListings": (BrowseListingsHandler, [self.listing_repo]),
                "GetListing": (GetListingHandler, [self.listing_repo]),
                "GetCategoryList": (GetCategoryListHandler, [self.category_repo]),
                "GetListingReviews": (GetListingReviewsHandler, [self.review_repo]),
                "GetUserPurchases": (GetUserPurchasesHandler, [self.payment_repo]),
                "GetAuthorListings": (GetAuthorListingsHandler, [self.listing_repo]),
            }
            
            handler_class, repos = handler_map.get(command_name, (None, None))
            if not handler_class:
                return None
            self._handlers[command_name] = handler_class(*repos)
        return self._handlers[command_name]
    
    def execute(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        command_name = command_data.get("command")
        if not command_name:
            return CommandResult.error("Command name is required").to_dict()
        
        handler = self._get_handler(command_name)
        if not handler:
            return CommandResult.error(f"Unknown command: {command_name}").to_dict()
        
        from backend.application.marketplace.commands import (
            CreateListingCommand, PublishListingCommand, RejectListingCommand,
            CreateReviewCommand, ProcessPaymentCommand,
            BrowseListingsCommand, GetListingCommand, GetCategoryListCommand,
            GetListingReviewsCommand, GetUserPurchasesCommand, GetAuthorListingsCommand,
        )
        
        command_classes = {
            "CreateListing": CreateListingCommand,
            "PublishListing": PublishListingCommand,
            "RejectListing": RejectListingCommand,
            "CreateReview": CreateReviewCommand,
            "ProcessPayment": ProcessPaymentCommand,
            "BrowseListings": BrowseListingsCommand,
            "GetListing": GetListingCommand,
            "GetCategoryList": GetCategoryListCommand,
            "GetListingReviews": GetListingReviewsCommand,
            "GetUserPurchases": GetUserPurchasesCommand,
            "GetAuthorListings": GetAuthorListingsCommand,
        }
        
        command_class = command_classes.get(command_name)
        if not command_class:
            return CommandResult.error(f"Unknown command: {command_name}").to_dict()
        
        try:
            command = command_class.from_dict(command_data)
            result = handler.handle(command)
            return result.to_dict()
        except Exception as e:
            logger.error(f"Error executing command {command_name}: {e}", exc_info=True)
            return CommandResult.error(f"Internal error: {str(e)}").to_dict()


_executor = MarketplaceCommandExecutor()


def get_service():
    """Get the marketplace command executor."""
    return _executor


@blp.route("/categories")
class CategoryList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        """List all marketplace categories."""
        result = get_service().execute({"command": "GetCategoryList"})
        if not result.get("success"):
            return []
        return result.get("data", [])


@blp.route("/blocks")
class ListingList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        """Browse marketplace listings."""
        category = request.args.get("category")
        search = request.args.get("q")
        status = request.args.get("status", "published")
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        
        result = get_service().execute({
            "command": "BrowseListings",
            "status": status,
            "category": category,
            "search": search,
            "page": page,
            "per_page": per_page,
        })
        
        if not result.get("success"):
            return {"items": [], "total": 0, "page": page, "per_page": per_page}
        return result.get("data", {})


@blp.route("/blocks/<int:listing_id>")
class ListingDetail(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, listing_id):
        """Get listing details."""
        result = get_service().execute({
            "command": "GetListing",
            "listing_id": listing_id,
        })
        
        if not result.get("success"):
            abort(404, message=result.get("error", "Listing not found"))
        return result.get("data", {})


@blp.route("/blocks/<int:listing_id>/reviews")
class ReviewList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self, listing_id):
        """Get reviews for a listing."""
        result = get_service().execute({
            "command": "GetListingReviews",
            "listing_id": listing_id,
        })
        
        if not result.get("success"):
            return []
        return result.get("data", [])
    
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self, listing_id):
        """Create a review for a listing."""
        user_id = get_jwt_identity()
        data = request.get_json()
        
        result = get_service().execute({
            "command": "CreateReview",
            "listing_id": listing_id,
            "user_id": user_id,
            **data,
        })
        
        if not result.get("success"):
            abort(400, message=result.get("error", "Failed to create review"))
        return result.get("data", {}), 201


@blp.route("/payments")
class PaymentList(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        """Get user's purchase history."""
        user_id = get_jwt_identity()
        
        result = get_service().execute({
            "command": "GetUserPurchases",
            "buyer_id": user_id,
        })
        
        if not result.get("success"):
            return []
        return result.get("data", [])


@blp.route("/payments/process")
class PaymentProcess(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def post(self):
        """Process payment for a listing."""
        user_id = get_jwt_identity()
        data = request.get_json()
        
        result = get_service().execute({
            "command": "ProcessPayment",
            "listing_id": data.get("listing_id"),
            "buyer_id": user_id,
            "payment_method": data.get("payment_method", ""),
            "amount": data.get("amount", 0),
            "currency": data.get("currency", "EUR"),
        })
        
        if not result.get("success"):
            abort(400, message=result.get("error", "Failed to process payment"))
        return result.get("data", {})


@blp.route("/my-listings")
class MyListings(MethodView):
    @blp.doc(security=[{"jwt": []}])
    @jwt_required()
    def get(self):
        """Get current user's own listings."""
        user_id = get_jwt_identity()
        
        result = get_service().execute({
            "command": "GetAuthorListings",
            "author_id": user_id,
        })
        
        if not result.get("success"):
            return []
        return result.get("data", [])
