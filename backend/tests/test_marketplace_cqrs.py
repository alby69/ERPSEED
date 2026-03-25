"""
Tests for Marketplace CQRS implementation.

Tests command handlers, query handlers, and domain models.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from decimal import Decimal

from backend.domain.marketplace import (
    Category, BlockListing, Review, PaymentTransaction, Author
)
from backend.domain.marketplace.events import (
    ListingCreatedEvent, ReviewCreatedEvent, PaymentCompletedEvent
)
from backend.application.marketplace.commands import (
    CreateListingCommand, CreateReviewCommand, ProcessPaymentCommand,
    BrowseListingsCommand, GetListingCommand
)
from backend.application.marketplace.handlers import (
    CreateListingHandler, CreateReviewHandler, ProcessPaymentHandler,
    BrowseListingsHandler, GetListingHandler
)


class TestMarketplaceModels:
    """Tests for marketplace domain models."""

    def test_category_validation(self):
        """Test Category model validation."""
        category = Category(name="Test", slug="test")
        is_valid, errors = category.validate()
        assert is_valid

        empty_category = Category()
        is_valid, errors = empty_category.validate()
        assert not is_valid
        assert "Category name is required" in errors

    def test_block_listing_rating_avg(self):
        """Test BlockListing rating_avg computed property."""
        listing = BlockListing(rating_sum=15, rating_count=3)
        assert listing.rating_avg == 5.0

        no_ratings = BlockListing(rating_sum=0, rating_count=0)
        assert no_ratings.rating_avg == 0.0

    def test_block_listing_validation(self):
        """Test BlockListing model validation."""
        listing = BlockListing(title="Test", slug="test")
        is_valid, errors = listing.validate()
        assert is_valid

        invalid_status = BlockListing(title="Test", slug="test", status="invalid")
        is_valid, errors = invalid_status.validate()
        assert not is_valid

    def test_review_validation(self):
        """Test Review model validation."""
        review = Review(rating=4)
        is_valid, errors = review.validate()
        assert is_valid

        invalid_rating_low = Review(rating=0)
        is_valid, errors = invalid_rating_low.validate()
        assert not is_valid

        invalid_rating_high = Review(rating=6)
        is_valid, errors = invalid_rating_high.validate()
        assert not is_valid

    def test_category_to_dict(self):
        """Test Category to_dict conversion."""
        category = Category(id=1, name="Test", slug="test", description="Desc")
        data = category.to_dict()
        assert data["id"] == 1
        assert data["name"] == "Test"
        assert data["slug"] == "test"
        assert data["description"] == "Desc"

    def test_block_listing_to_dict(self):
        """Test BlockListing to_dict conversion."""
        listing = BlockListing(
            id=1, title="Test", slug="test", price=Decimal("19.99"),
            rating_sum=10, rating_count=2
        )
        data = listing.to_dict()
        assert data["id"] == 1
        assert data["title"] == "Test"
        assert data["price"] == 19.99
        assert data["rating_avg"] == 5.0


class TestMarketplaceCommands:
    """Tests for marketplace command parsing."""

    def test_create_listing_command_from_dict(self):
        """Test CreateListingCommand creation from dictionary."""
        data = {
            "block_id": 1,
            "author_id": 2,
            "title": "Test Block",
            "slug": "test-block",
            "price": 29.99,
            "tenant_id": 1
        }
        command = CreateListingCommand.from_dict(data)
        assert command.block_id == 1
        assert command.author_id == 2
        assert command.title == "Test Block"
        assert command.slug == "test-block"
        assert command.price == 29.99

    def test_create_review_command_from_dict(self):
        """Test CreateReviewCommand creation from dictionary."""
        data = {
            "listing_id": 1,
            "user_id": 2,
            "rating": 5,
            "comment": "Great!"
        }
        command = CreateReviewCommand.from_dict(data)
        assert command.listing_id == 1
        assert command.user_id == 2
        assert command.rating == 5
        assert command.comment == "Great!"

    def test_process_payment_command_from_dict(self):
        """Test ProcessPaymentCommand creation from dictionary."""
        data = {
            "listing_id": 1,
            "buyer_id": 2,
            "payment_method": "stripe",
            "amount": 49.99
        }
        command = ProcessPaymentCommand.from_dict(data)
        assert command.listing_id == 1
        assert command.buyer_id == 2
        assert command.payment_method == "stripe"
        assert command.amount == 49.99

    def test_browse_listings_command_with_pagination(self):
        """Test BrowseListingsCommand with pagination data."""
        data = {
            "status": "published",
            "category": "inventory",
            "search": "test",
            "pagination": {"page": 2, "per_page": 10}
        }
        command = BrowseListingsCommand.from_dict(data)
        assert command.status == "published"
        assert command.category == "inventory"
        assert command.search == "test"
        assert command.page == 2
        assert command.per_page == 10


class TestMarketplaceEvents:
    """Tests for marketplace domain events."""

    def test_listing_created_event(self):
        """Test ListingCreatedEvent."""
        event = ListingCreatedEvent(
            listing_id=1, author_id=2, title="Test", tenant_id=1
        )
        data = event.to_dict()
        assert data["event_type"] == "listing.created"
        assert data["listing_id"] == 1
        assert data["author_id"] == 2

    def test_review_created_event(self):
        """Test ReviewCreatedEvent."""
        event = ReviewCreatedEvent(
            review_id=1, listing_id=2, user_id=3, rating=5
        )
        data = event.to_dict()
        assert data["event_type"] == "review.created"
        assert data["review_id"] == 1
        assert data["rating"] == 5

    def test_payment_completed_event(self):
        """Test PaymentCompletedEvent."""
        event = PaymentCompletedEvent(
            payment_id=1, listing_id=2, buyer_id=3, author_id=4,
            amount=99.99, currency="EUR"
        )
        data = event.to_dict()
        assert data["event_type"] == "payment.completed"
        assert data["amount"] == 99.99


class TestCreateListingHandler:
    """Tests for CreateListingHandler."""

    def test_create_listing_success(self):
        """Test successful listing creation."""
        mock_repo = Mock()
        mock_repo.find_by_slug.return_value = None
        mock_repo.create.return_value = {
            "id": 1, "title": "Test", "slug": "test", "status": "draft"
        }

        handler = CreateListingHandler(mock_repo)
        command = CreateListingCommand(
            block_id=1, author_id=2, title="Test", slug="test"
        )

        result = handler.handle(command)

        assert result.success
        assert result.data["id"] == 1
        mock_repo.create.assert_called_once()

    def test_create_listing_duplicate_slug(self):
        """Test listing creation with duplicate slug."""
        mock_repo = Mock()
        mock_repo.find_by_slug.return_value = {"id": 1, "slug": "test"}

        handler = CreateListingHandler(mock_repo)
        command = CreateListingCommand(
            block_id=1, author_id=2, title="Test", slug="test"
        )

        result = handler.handle(command)

        assert not result.success
        assert "already exists" in result.error


class TestCreateReviewHandler:
    """Tests for CreateReviewHandler."""

    def test_create_review_success(self):
        """Test successful review creation."""
        mock_review_repo = Mock()
        mock_listing_repo = Mock()
        mock_event_bus = Mock()

        mock_listing_repo.find_by_id.return_value = {
            "id": 1, "author_id": 99, "rating_sum": 0, "rating_count": 0
        }
        mock_review_repo.find_by_user_and_listing.return_value = None
        mock_review_repo.create.return_value = {
            "id": 1, "listing_id": 1, "user_id": 2, "rating": 5
        }

        handler = CreateReviewHandler(mock_review_repo, mock_listing_repo, mock_event_bus)
        command = CreateReviewCommand(
            listing_id=1, user_id=2, rating=5, comment="Great!"
        )

        result = handler.handle(command)

        assert result.success
        assert result.data["rating"] == 5
        mock_listing_repo.increment_rating.assert_called_once_with(1, 5)

    def test_create_review_invalid_rating(self):
        """Test review creation with invalid rating."""
        mock_review_repo = Mock()
        mock_listing_repo = Mock()

        handler = CreateReviewHandler(mock_review_repo, mock_listing_repo)
        command = CreateReviewCommand(listing_id=1, user_id=2, rating=0)

        result = handler.handle(command)

        assert not result.success
        assert "between 1 and 5" in result.error

    def test_create_review_own_listing(self):
        """Test review creation on own listing."""
        mock_review_repo = Mock()
        mock_listing_repo = Mock()

        mock_listing_repo.find_by_id.return_value = {
            "id": 1, "author_id": 2, "rating_sum": 0, "rating_count": 0
        }

        handler = CreateReviewHandler(mock_review_repo, mock_listing_repo)
        command = CreateReviewCommand(listing_id=1, user_id=2, rating=5)

        result = handler.handle(command)

        assert not result.success
        assert "own listing" in result.error

    def test_create_review_duplicate(self):
        """Test duplicate review creation."""
        mock_review_repo = Mock()
        mock_listing_repo = Mock()

        mock_listing_repo.find_by_id.return_value = {
            "id": 1, "author_id": 99, "rating_sum": 0, "rating_count": 0
        }
        mock_review_repo.find_by_user_and_listing.return_value = {"id": 1}

        handler = CreateReviewHandler(mock_review_repo, mock_listing_repo)
        command = CreateReviewCommand(listing_id=1, user_id=2, rating=5)

        result = handler.handle(command)

        assert not result.success
        assert "already reviewed" in result.error


class TestProcessPaymentHandler:
    """Tests for ProcessPaymentHandler."""

    def test_process_payment_success(self):
        """Test successful payment processing."""
        mock_payment_repo = Mock()
        mock_listing_repo = Mock()
        mock_author_repo = Mock()
        mock_event_bus = Mock()

        mock_listing_repo.find_by_id.return_value = {
            "id": 1, "author_id": 99, "price": 49.99, "currency": "EUR"
        }
        mock_payment_repo.find_completed_by_buyer_and_listing.return_value = None
        mock_payment_repo.create.return_value = {"id": 1}
        mock_payment_repo.complete.return_value = {
            "id": 1, "status": "completed", "transaction_id": "txn_1"
        }
        mock_author_repo.find_by_user_id.return_value = {"id": 1}

        handler = ProcessPaymentHandler(
            mock_payment_repo, mock_listing_repo, mock_author_repo, mock_event_bus
        )
        command = ProcessPaymentCommand(
            listing_id=1, buyer_id=2, payment_method="stripe", amount=49.99
        )

        result = handler.handle(command)

        assert result.success
        assert result.data["status"] == "completed"
        mock_listing_repo.increment_downloads.assert_called_once_with(1)

    def test_process_payment_own_listing(self):
        """Test payment for own listing."""
        mock_payment_repo = Mock()
        mock_listing_repo = Mock()
        mock_author_repo = Mock()

        mock_listing_repo.find_by_id.return_value = {
            "id": 1, "author_id": 2, "price": 49.99, "currency": "EUR"
        }

        handler = ProcessPaymentHandler(
            mock_payment_repo, mock_listing_repo, mock_author_repo
        )
        command = ProcessPaymentCommand(
            listing_id=1, buyer_id=2, payment_method="stripe"
        )

        result = handler.handle(command)

        assert not result.success
        assert "own listing" in result.error

    def test_process_payment_already_purchased(self):
        """Test payment for already purchased listing."""
        mock_payment_repo = Mock()
        mock_listing_repo = Mock()
        mock_author_repo = Mock()

        mock_listing_repo.find_by_id.return_value = {
            "id": 1, "author_id": 99, "price": 49.99, "currency": "EUR"
        }
        mock_payment_repo.find_completed_by_buyer_and_listing.return_value = {"id": 1}

        handler = ProcessPaymentHandler(
            mock_payment_repo, mock_listing_repo, mock_author_repo
        )
        command = ProcessPaymentCommand(
            listing_id=1, buyer_id=2, payment_method="stripe"
        )

        result = handler.handle(command)

        assert not result.success
        assert "already purchased" in result.error


class TestBrowseListingsHandler:
    """Tests for BrowseListingsHandler."""

    def test_browse_listings(self):
        """Test browsing listings."""
        mock_repo = Mock()
        mock_repo.find_all.return_value = {
            "items": [{"id": 1, "title": "Test"}],
            "total": 1, "page": 1, "per_page": 20
        }

        handler = BrowseListingsHandler(mock_repo)
        command = BrowseListingsCommand(status="published")

        result = handler.handle(command)

        assert result.success
        assert len(result.data["items"]) == 1
        mock_repo.find_all.assert_called_once()

    def test_browse_listings_with_filters(self):
        """Test browsing listings with filters."""
        mock_repo = Mock()
        mock_repo.find_all.return_value = {
            "items": [], "total": 0, "page": 1, "per_page": 20
        }

        handler = BrowseListingsHandler(mock_repo)
        command = BrowseListingsCommand(
            status="published",
            category="inventory",
            search="test",
            page=2,
            per_page=10
        )

        result = handler.handle(command)

        assert result.success
        mock_repo.find_all.assert_called_once_with(
            status="published",
            category_slug="inventory",
            search="test",
            page=2,
            per_page=10
        )


class TestGetListingHandler:
    """Tests for GetListingHandler."""

    def test_get_listing_success(self):
        """Test successful listing retrieval."""
        mock_repo = Mock()
        mock_repo.find_by_id.return_value = {"id": 1, "title": "Test"}

        handler = GetListingHandler(mock_repo)
        command = GetListingCommand(listing_id=1)

        result = handler.handle(command)

        assert result.success
        assert result.data["id"] == 1

    def test_get_listing_not_found(self):
        """Test listing not found."""
        mock_repo = Mock()
        mock_repo.find_by_id.return_value = None

        handler = GetListingHandler(mock_repo)
        command = GetListingCommand(listing_id=999)

        result = handler.handle(command)

        assert not result.success
        assert "not found" in result.error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
