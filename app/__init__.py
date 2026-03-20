import os
from flask import Flask, app, render_template
from config import config_map
from app.extensions import db, jwt, bcrypt, mail, migrate, limiter
from app.routes.payments import payments_bp
from app.routes.reviews import reviews_bp
from app.routes.coupons import coupons_bp
from app.extensions import db, jwt, bcrypt, mail, migrate, limiter, csrf


def create_app(env: str = None) -> Flask:
    env = env or os.getenv("FLASK_ENV", "development")
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(config_map[env])

    app.config["JWT_COOKIE_SAMESITE"]    = "Lax"
    app.config["JWT_COOKIE_SECURE"]      = False
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False

    # ─── Extensiones ─────────────────────────────────────
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    csrf.init_app(app)

    # ─── Modelos ─────────────────────────────────────────
    from app.models import user, product, order, category  # noqa: F401

    # ─── Blueprints ──────────────────────────────────────
    from app.routes.main   import main_bp
    from app.routes.auth   import auth_bp
    from app.routes.admin  import admin_bp
    from app.routes.vendor import vendor_bp
    from app.routes.client import client_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp,   url_prefix="/auth")
    app.register_blueprint(admin_bp,  url_prefix="/admin")
    app.register_blueprint(vendor_bp, url_prefix="/vendor")
    app.register_blueprint(client_bp, url_prefix="/shop")
    app.register_blueprint(payments_bp, url_prefix="/payments")
    app.register_blueprint(reviews_bp, url_prefix="/social")
    app.register_blueprint(coupons_bp, url_prefix="/coupons")

    # ─── JWT callbacks ───────────────────────────────────
    from app.utils.security import register_jwt_callbacks
    register_jwt_callbacks(jwt)

    # ─── current_user en templates ───────────────────────
    @app.context_processor
    def inject_current_user():
        from flask import session as flask_session
        from app.models.user import User
        user_id = flask_session.get("user_id")
        if user_id:
            user = User.query.get(user_id)
            if user:
                return dict(current_user=user)
        return dict(current_user=None)
    
     # ─── Error handlers ──────────────────────────────────
    from flask import render_template as rt

    @app.errorhandler(429)
    def rate_limit_exceeded(e):
        from flask import flash, redirect, url_for
        flash("Demasiados intentos fallidos. Espera un momento antes de intentar de nuevo.", "danger")
        return redirect(url_for("auth.login")), 302

    # ─── Error handlers ───────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500

    return app