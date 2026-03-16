from datetime import datetime, timezone
from app.extensions import db


class Role:
    ADMIN   = "admin"
    VENDOR  = "vendor"
    CLIENT  = "client"
    ALL     = [ADMIN, VENDOR, CLIENT]


class User(db.Model):
    __tablename__ = "users"

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(100), nullable=False)
    email         = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role          = db.Column(db.String(20), nullable=False, default=Role.CLIENT)
    is_active     = db.Column(db.Boolean, default=True)

    # 2FA
    totp_secret  = db.Column(db.String(64), nullable=True)
    totp_enabled = db.Column(db.Boolean, default=False)

    # Reset de contraseña
    reset_token        = db.Column(db.String(255), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    products = db.relationship("Product", back_populates="vendor", lazy="dynamic")
    orders   = db.relationship("Order",   back_populates="client", lazy="dynamic")
    reviews   = db.relationship("Review",   back_populates="user")
    favorites = db.relationship("Favorite", back_populates="user")

    def is_admin(self):  return self.role == Role.ADMIN
    def is_vendor(self): return self.role == Role.VENDOR
    def is_client(self): return self.role == Role.CLIENT
    def has_2fa(self):   return self.totp_enabled and self.totp_secret

    def __repr__(self):
        return f"<User {self.email} [{self.role}]>"