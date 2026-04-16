"""
Marketplace Models - BlockListing, Category, Review, Payment
This module defines models for the Marketplace functionality.
"""

from extensions import db
import datetime


class Category(db.Model):
    """
    Block categories for marketplace organization.
    Supports hierarchical categories (parent/child).
    """

    __tablename__ = "marketplace_categories"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))

    # Hierarchy
    parent_id = db.Column(db.Integer, db.ForeignKey("marketplace_categories.id"))
    order_index = db.Column(db.Integer, default=0)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    # Relationships
    parent = db.relationship("Category", remote_side=[id], backref="children")
    listings = db.relationship("BlockListing", back_populates="category")

    def __repr__(self):
        return f"<Category {self.name}>"


class BlockListing(db.Model):
    """
    Published block in marketplace.
    Represents a block ready for discovery and installation.
    """

    __tablename__ = "marketplace_listings"

    id = db.Column(db.Integer, primary_key=True)

    # References
    block_id = db.Column(db.Integer, db.ForeignKey("blocks.id"), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("marketplace_categories.id"))

    # Identity
    title = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text)
    long_description = db.Column(db.Text)  # Markdown supported

    # Business
    price = db.Column(db.Numeric(10, 2), default=0)
    currency = db.Column(db.String(3), default="EUR")

    # Media
    thumbnail_url = db.Column(db.String(255))
    screenshots = db.Column(db.JSON, default=list)
    demo_url = db.Column(db.String(255))

    # Stats
    downloads = db.Column(db.Integer, default=0)
    rating_sum = db.Column(db.Integer, default=0)
    rating_count = db.Column(db.Integer, default=0)

    @property
    def rating_avg(self):
        if self.rating_count > 0:
            return round(self.rating_sum / self.rating_count, 2)
        return 0

    # Status (Hybrid: internal + external with approval)
    status = db.Column(
        db.String(20),
        default="draft",
        comment="draft, pending_review, published, rejected",
    )
    rejection_reason = db.Column(db.Text)
    published_at = db.Column(db.DateTime)

    # Versioning
    current_version = db.Column(db.String(20))
    changelog = db.Column(db.Text)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    # Relationships
    block = db.relationship("Block", backref="listing")
    author = db.relationship("User", backref="published_listings")
    category = db.relationship("Category", back_populates="listings")
    reviews = db.relationship(
        "Review", back_populates="listing", cascade="all, delete-orphan"
    )
    transactions = db.relationship(
        "PaymentTransaction", back_populates="listing", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<BlockListing {self.title}>"


class Review(db.Model):
    """
    User reviews and ratings for marketplace blocks.
    """

    __tablename__ = "marketplace_reviews"

    id = db.Column(db.Integer, primary_key=True)

    # References
    listing_id = db.Column(
        db.Integer, db.ForeignKey("marketplace_listings.id"), nullable=False
    )
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # Review content
    rating = db.Column(db.Integer)  # 1-5
    comment = db.Column(db.Text)

    # Status
    is_verified_purchase = db.Column(db.Boolean, default=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    # Relationships
    listing = db.relationship("BlockListing", back_populates="reviews")
    user = db.relationship("User", backref="block_reviews")

    def __repr__(self):
        return f"<Review {self.rating} stars for {self.listing_id}>"


class PaymentTransaction(db.Model):
    """
    Payment processing for paid marketplace blocks.
    Supports multiple payment methods.
    """

    __tablename__ = "marketplace_payments"

    id = db.Column(db.Integer, primary_key=True)

    # References
    listing_id = db.Column(
        db.Integer, db.ForeignKey("marketplace_listings.id"), nullable=False
    )
    buyer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # Amount
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default="EUR")

    # Status
    status = db.Column(
        db.String(20), default="pending", comment="pending, completed, failed, refunded"
    )

    # Payment details
    payment_method = db.Column(db.String(50), comment="stripe, paypal, etc.")
    transaction_id = db.Column(db.String(255))
    payment_data = db.Column(db.JSON, default=dict)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    # Relationships
    listing = db.relationship("BlockListing", back_populates="transactions")
    buyer = db.relationship("User", foreign_keys=[buyer_id], backref="block_purchases")

    def __repr__(self):
        return f"<PaymentTransaction {self.amount} {self.currency}>"


class Author(db.Model):
    """
    Marketplace author profile.
    """

    __tablename__ = "marketplace_authors"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True
    )

    # Profile
    display_name = db.Column(db.String(120))
    bio = db.Column(db.Text)
    avatar_url = db.Column(db.String(255))
    website = db.Column(db.String(255))

    # Stats
    total_downloads = db.Column(db.Integer, default=0)
    total_revenue = db.Column(db.Numeric(12, 2), default=0)
    avg_rating = db.Column(db.Numeric(3, 2), default=0)

    # Verification
    is_verified = db.Column(db.Boolean, default=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    # Relationships
    user = db.relationship("User", backref="marketplace_author")

    def __repr__(self):
        return f"<Author {self.display_name}>"


# Default categories
def create_default_categories():
    """Create default marketplace categories."""
    categories = [
        {
            "name": "Accounting",
            "slug": "accounting",
            "icon": "DollarOutlined",
            "order_index": 1,
        },
        {
            "name": "Inventory",
            "slug": "inventory",
            "icon": "InboxOutlined",
            "order_index": 2,
        },
        {"name": "CRM", "slug": "crm", "icon": "TeamOutlined", "order_index": 3},
        {"name": "HR", "slug": "hr", "icon": "UserOutlined", "order_index": 4},
        {
            "name": "E-Commerce",
            "slug": "e-commerce",
            "icon": "ShoppingCartOutlined",
            "order_index": 5,
        },
        {
            "name": "Project Management",
            "slug": "project-management",
            "icon": "ProjectOutlined",
            "order_index": 6,
        },
        {
            "name": "Manufacturing",
            "slug": "manufacturing",
            "icon": "BuildOutlined",
            "order_index": 7,
        },
        {
            "name": "Analytics",
            "slug": "analytics",
            "icon": "BarChartOutlined",
            "order_index": 8,
        },
        {
            "name": "Utilities",
            "slug": "utilities",
            "icon": "ToolOutlined",
            "order_index": 9,
        },
    ]

    for cat_data in categories:
        existing = Category.query.filter_by(slug=cat_data["slug"]).first()
        if not existing:
            category = Category(**cat_data)
            db.session.add(category)

    db.session.commit()
