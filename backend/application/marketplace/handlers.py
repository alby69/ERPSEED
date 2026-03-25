"""
Marketplace Command and Query Handlers.

Handle commands and queries for marketplace operations.
"""
import logging
from typing import Dict, Any

from backend.shared.handlers import CommandHandler, CommandResult, QueryHandler

from .commands import (
    CreateListingCommand, PublishListingCommand, RejectListingCommand,
    CreateReviewCommand, ProcessPaymentCommand,
    BrowseListingsCommand, GetListingCommand, GetCategoryListCommand,
    GetListingReviewsCommand, GetUserPurchasesCommand, GetAuthorListingsCommand,
)

logger = logging.getLogger(__name__)


class CreateListingHandler(CommandHandler):
    def __init__(self, listing_repository, event_bus=None):
        self.listing_repo = listing_repository
        self.event_bus = event_bus

    @property
    def command_type(self) -> str:
        return "CreateListing"

    def handle(self, command: CreateListingCommand) -> CommandResult:
        try:
            existing = self.listing_repo.find_by_slug(command.slug)
            if existing:
                return CommandResult.error(f"Listing with slug '{command.slug}' already exists")

            result = self.listing_repo.create(command.to_payload())

            from backend.domain.marketplace import ListingCreatedEvent
            if self.event_bus:
                self.event_bus.publish(ListingCreatedEvent(
                    listing_id=result["id"],
                    author_id=command.author_id,
                    title=command.title,
                    tenant_id=command.tenant_id
                ))

            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error creating listing: {e}")
            return CommandResult.error(f"Failed to create listing: {str(e)}")


class PublishListingHandler(CommandHandler):
    def __init__(self, listing_repository, event_bus=None):
        self.listing_repo = listing_repository
        self.event_bus = event_bus

    @property
    def command_type(self) -> str:
        return "PublishListing"

    def handle(self, command: PublishListingCommand) -> CommandResult:
        try:
            listing = self.listing_repo.find_by_id(command.listing_id)
            if not listing:
                return CommandResult.error(f"Listing not found: {command.listing_id}")

            if listing["status"] == "published":
                return CommandResult.error("Listing is already published")

            result = self.listing_repo.update_status(command.listing_id, "published")

            from backend.domain.marketplace import ListingPublishedEvent
            if self.event_bus:
                self.event_bus.publish(ListingPublishedEvent(
                    listing_id=command.listing_id,
                    author_id=listing["author_id"],
                    title=listing["title"],
                    tenant_id=command.tenant_id
                ))

            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error publishing listing: {e}")
            return CommandResult.error(f"Failed to publish listing: {str(e)}")


class RejectListingHandler(CommandHandler):
    def __init__(self, listing_repository, event_bus=None):
        self.listing_repo = listing_repository
        self.event_bus = event_bus

    @property
    def command_type(self) -> str:
        return "RejectListing"

    def handle(self, command: RejectListingCommand) -> CommandResult:
        try:
            listing = self.listing_repo.find_by_id(command.listing_id)
            if not listing:
                return CommandResult.error(f"Listing not found: {command.listing_id}")

            result = self.listing_repo.update_status(
                command.listing_id, "rejected", command.reason
            )

            from backend.domain.marketplace import ListingRejectedEvent
            if self.event_bus:
                self.event_bus.publish(ListingRejectedEvent(
                    listing_id=command.listing_id,
                    author_id=listing["author_id"],
                    reason=command.reason,
                    tenant_id=command.tenant_id
                ))

            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error rejecting listing: {e}")
            return CommandResult.error(f"Failed to reject listing: {str(e)}")


class CreateReviewHandler(CommandHandler):
    def __init__(self, review_repository, listing_repository, event_bus=None):
        self.review_repo = review_repository
        self.listing_repo = listing_repository
        self.event_bus = event_bus

    @property
    def command_type(self) -> str:
        return "CreateReview"

    def handle(self, command: CreateReviewCommand) -> CommandResult:
        try:
            if command.rating < 1 or command.rating > 5:
                return CommandResult.error("Rating must be between 1 and 5")

            listing = self.listing_repo.find_by_id(command.listing_id)
            if not listing:
                return CommandResult.error(f"Listing not found: {command.listing_id}")

            if command.user_id == listing["author_id"]:
                return CommandResult.error("Cannot review your own listing")

            existing = self.review_repo.find_by_user_and_listing(command.user_id, command.listing_id)
            if existing:
                return CommandResult.error("You have already reviewed this listing")

            result = self.review_repo.create(command.to_payload())

            self.listing_repo.increment_rating(command.listing_id, command.rating)

            from backend.domain.marketplace import ReviewCreatedEvent
            if self.event_bus:
                self.event_bus.publish(ReviewCreatedEvent(
                    review_id=result["id"],
                    listing_id=command.listing_id,
                    user_id=command.user_id,
                    rating=command.rating,
                    tenant_id=command.tenant_id
                ))

            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error creating review: {e}")
            return CommandResult.error(f"Failed to create review: {str(e)}")


class ProcessPaymentHandler(CommandHandler):
    def __init__(self, payment_repository, listing_repository, author_repository, event_bus=None):
        self.payment_repo = payment_repository
        self.listing_repo = listing_repository
        self.author_repo = author_repository
        self.event_bus = event_bus

    @property
    def command_type(self) -> str:
        return "ProcessPayment"

    def handle(self, command: ProcessPaymentCommand) -> CommandResult:
        try:
            listing = self.listing_repo.find_by_id(command.listing_id)
            if not listing:
                return CommandResult.error(f"Listing not found: {command.listing_id}")

            if command.buyer_id == listing["author_id"]:
                return CommandResult.error("Cannot purchase your own listing")

            existing = self.payment_repo.find_completed_by_buyer_and_listing(
                command.buyer_id, command.listing_id
            )
            if existing:
                return CommandResult.error("You have already purchased this listing")

            amount = command.amount if command.amount > 0 else listing["price"]

            payment = self.payment_repo.create({
                **command.to_payload(),
                "amount": amount,
            })

            transaction_id = f"txn_{payment['id']}"
            result = self.payment_repo.complete(payment["id"], transaction_id)

            self.listing_repo.increment_downloads(command.listing_id)

            author = self.author_repo.find_by_user_id(listing["author_id"])
            if author:
                self.author_repo.update_revenue(author["id"], amount)

            from backend.domain.marketplace import PaymentCompletedEvent
            if self.event_bus:
                self.event_bus.publish(PaymentCompletedEvent(
                    payment_id=result["id"],
                    listing_id=command.listing_id,
                    buyer_id=command.buyer_id,
                    author_id=listing["author_id"],
                    amount=amount,
                    currency=listing["currency"],
                    tenant_id=command.tenant_id
                ))

            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error processing payment: {e}")
            return CommandResult.error(f"Failed to process payment: {str(e)}")


class BrowseListingsHandler(QueryHandler):
    def __init__(self, listing_repository):
        self.listing_repo = listing_repository

    @property
    def command_type(self) -> str:
        return "BrowseListings"

    def handle(self, command: BrowseListingsCommand) -> CommandResult:
        try:
            result = self.listing_repo.find_all(
                status=command.status,
                category_slug=command.category,
                search=command.search,
                page=command.page,
                per_page=command.per_page,
            )
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error browsing listings: {e}")
            return CommandResult.error(f"Failed to browse listings: {str(e)}")


class GetListingHandler(QueryHandler):
    def __init__(self, listing_repository):
        self.listing_repo = listing_repository

    @property
    def command_type(self) -> str:
        return "GetListing"

    def handle(self, command: GetListingCommand) -> CommandResult:
        try:
            result = self.listing_repo.find_by_id(command.listing_id)
            if not result:
                return CommandResult.error(f"Listing not found: {command.listing_id}")
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error getting listing: {e}")
            return CommandResult.error(f"Failed to get listing: {str(e)}")


class GetCategoryListHandler(QueryHandler):
    def __init__(self, category_repository):
        self.category_repo = category_repository

    @property
    def command_type(self) -> str:
        return "GetCategoryList"

    def handle(self, command: GetCategoryListCommand) -> CommandResult:
        try:
            result = self.category_repo.find_all()
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error getting categories: {e}")
            return CommandResult.error(f"Failed to get categories: {str(e)}")


class GetListingReviewsHandler(QueryHandler):
    def __init__(self, review_repository):
        self.review_repo = review_repository

    @property
    def command_type(self) -> str:
        return "GetListingReviews"

    def handle(self, command: GetListingReviewsCommand) -> CommandResult:
        try:
            result = self.review_repo.find_by_listing(command.listing_id)
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error getting reviews: {e}")
            return CommandResult.error(f"Failed to get reviews: {str(e)}")


class GetUserPurchasesHandler(QueryHandler):
    def __init__(self, payment_repository):
        self.payment_repo = payment_repository

    @property
    def command_type(self) -> str:
        return "GetUserPurchases"

    def handle(self, command: GetUserPurchasesCommand) -> CommandResult:
        try:
            result = self.payment_repo.find_by_buyer(command.buyer_id)
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error getting purchases: {e}")
            return CommandResult.error(f"Failed to get purchases: {str(e)}")


class GetAuthorListingsHandler(QueryHandler):
    def __init__(self, listing_repository):
        self.listing_repo = listing_repository

    @property
    def command_type(self) -> str:
        return "GetAuthorListings"

    def handle(self, command: GetAuthorListingsCommand) -> CommandResult:
        try:
            result = self.listing_repo.find_by_author(command.author_id)
            return CommandResult.ok(result)
        except Exception as e:
            logger.error(f"Error getting author listings: {e}")
            return CommandResult.error(f"Failed to get author listings: {str(e)}")
