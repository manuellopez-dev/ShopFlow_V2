from datetime import datetime, timezone
from app.extensions import db


class Product(db.Model):
    __tablename__ = "products"

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    price       = db.Column(db.Numeric(10, 2), nullable=False)
    stock       = db.Column(db.Integer, default=0)
    image_url   = db.Column(db.String(500), nullable=True)
    is_active   = db.Column(db.Boolean, default=True)
    min_stock   = db.Column(db.Integer, default=5, nullable=False)

    vendor_id   = db.Column(db.Integer, db.ForeignKey("users.id"),      nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    vendor    = db.relationship("User",      back_populates="products")
    category  = db.relationship("Category",  back_populates="products")
    items     = db.relationship("OrderItem", back_populates="product")
    reviews   = db.relationship("Review",    back_populates="product", cascade="all, delete-orphan")
    favorites = db.relationship("Favorite",  back_populates="product", cascade="all, delete-orphan")

    @property
    def avg_rating(self):
        if not self.reviews:
            return 0
        return round(sum(r.rating for r in self.reviews) / len(self.reviews), 1)

    @property
    def review_count(self):
        return len(self.reviews)

    def get_discounted_price(self, qty: int) -> float:
        if not self.quantity_discounts:
            return float(self.price)
        discounts = sorted(self.quantity_discounts, key=lambda d: d.min_qty, reverse=True)
        for d in discounts:
            if qty >= d.min_qty:
                return round(float(self.price) * (1 - float(d.discount) / 100), 2)
        return float(self.price)

    def get_applicable_discount(self, qty: int):
        if not self.quantity_discounts:
            return None
        discounts = sorted(self.quantity_discounts, key=lambda d: d.min_qty, reverse=True)
        for d in discounts:
            if qty >= d.min_qty:
                return d
        return None

    def get_related(self, limit=4):
        if not self.category_id:
            return Product.query.filter(
                Product.id != self.id,
                Product.is_active == True
            ).order_by(db.func.random()).limit(limit).all()
        return Product.query.filter(
            Product.category_id == self.category_id,
            Product.id != self.id,
            Product.is_active == True
        ).order_by(db.func.random()).limit(limit).all()

    def __repr__(self):
        return f"<Product {self.name} ${self.price}>"


class Review(db.Model):
    __tablename__ = "reviews"

    id         = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"),    nullable=False)
    rating     = db.Column(db.Integer, nullable=False)
    comment    = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    product = db.relationship("Product", back_populates="reviews")
    user    = db.relationship("User",    back_populates="reviews")

    def __repr__(self):
        return f"<Review {self.rating}★ product={self.product_id}>"


class Favorite(db.Model):
    __tablename__ = "favorites"

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"),    nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user    = db.relationship("User",    back_populates="favorites")
    product = db.relationship("Product", back_populates="favorites")

    __table_args__ = (
        db.UniqueConstraint("user_id", "product_id", name="uq_user_product_favorite"),
    )


class QuantityDiscount(db.Model):
    __tablename__ = "quantity_discounts"

    id         = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    min_qty    = db.Column(db.Integer, nullable=False)
    discount   = db.Column(db.Numeric(5, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    product = db.relationship("Product", backref="quantity_discounts")

    def __repr__(self):
        return f"<QuantityDiscount {self.min_qty}+ → {self.discount}%>"


class PriceHistory(db.Model):
    __tablename__ = "price_history"

    id         = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    old_price  = db.Column(db.Numeric(10, 2), nullable=False)
    new_price  = db.Column(db.Numeric(10, 2), nullable=False)
    changed_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    changed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    product = db.relationship("Product", backref="price_history")
    user    = db.relationship("User", foreign_keys=[changed_by])

    @property
    def change_percent(self):
        if float(self.old_price) == 0:
            return 0
        return round(((float(self.new_price) - float(self.old_price)) / float(self.old_price)) * 100, 1)