from datetime import datetime, timezone
from app.extensions import db


class OrderStatus:
    PENDING   = "pending"
    CONFIRMED = "confirmed"
    SHIPPED   = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class Coupon(db.Model):
    __tablename__ = "coupons"

    id              = db.Column(db.Integer, primary_key=True)
    code            = db.Column(db.String(50), unique=True, nullable=False)
    discount_type   = db.Column(db.String(20), default="percent")  # percent | fixed
    discount_value  = db.Column(db.Numeric(10, 2), nullable=False)
    min_order       = db.Column(db.Numeric(10, 2), default=0)
    max_uses        = db.Column(db.Integer, default=100)
    used_count      = db.Column(db.Integer, default=0)
    is_active       = db.Column(db.Boolean, default=True)
    expires_at      = db.Column(db.DateTime, nullable=True)
    created_at      = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def is_valid(self, order_total: float) -> tuple[bool, str]:
        if not self.is_active:
            return False, "Cupón inactivo."
        if self.expires_at:
            expires = self.expires_at.replace(tzinfo=timezone.utc) if self.expires_at.tzinfo is None else self.expires_at
        if datetime.now(timezone.utc) > expires:
            return False, "Cupón expirado."
        if self.used_count >= self.max_uses:
            return False, "Cupón agotado."
        if order_total < float(self.min_order):
         return False, f"Mínimo de compra: ${self.min_order}"
        return True, "OK"

    def apply(self, order_total: float) -> float:
        if self.discount_type == "percent":
            discount = order_total * float(self.discount_value) / 100
        else:
            discount = float(self.discount_value)
        return round(max(order_total - discount, 0), 2)

    def __repr__(self):
        return f"<Coupon {self.code} {self.discount_value}{'%' if self.discount_type == 'percent' else '$'}>"


class Order(db.Model):
    __tablename__ = "orders"

    id             = db.Column(db.Integer, primary_key=True)
    client_id      = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    status         = db.Column(db.String(20), default=OrderStatus.PENDING)
    total          = db.Column(db.Numeric(10, 2), default=0)
    discount       = db.Column(db.Numeric(10, 2), default=0)
    coupon_code    = db.Column(db.String(50), nullable=True)
    notes          = db.Column(db.Text)
    payment_method = db.Column(db.String(20), default="pending")
    payment_id     = db.Column(db.String(200))
    payment_status = db.Column(db.String(20), default="unpaid")
    created_at     = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at     = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                               onupdate=lambda: datetime.now(timezone.utc))
    shipping_address = db.Column(db.String(500), nullable=True)
    shipping_city    = db.Column(db.String(100), nullable=True)
    shipping_state   = db.Column(db.String(100), nullable=True)
    shipping_zip     = db.Column(db.String(20),  nullable=True)
    shipping_phone   = db.Column(db.String(20),  nullable=True)

    client = db.relationship("User",      back_populates="orders")
    items  = db.relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    def calculate_total(self):
        self.total = sum(item.subtotal for item in self.items)

    def __repr__(self):
        return f"<Order #{self.id} [{self.status}]>"


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id         = db.Column(db.Integer, primary_key=True)
    order_id   = db.Column(db.Integer, db.ForeignKey("orders.id"),   nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity   = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)

    order   = db.relationship("Order",   back_populates="items")
    product = db.relationship("Product", back_populates="items")

    @property
    def subtotal(self):
        return self.quantity * self.unit_price