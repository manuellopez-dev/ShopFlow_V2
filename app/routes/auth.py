import secrets
from datetime import datetime, timezone, timedelta
from app.utils.sanitize import sanitize
import pyotp
import qrcode
import io, base64

from flask import (Blueprint, render_template, redirect, url_for,
                   request, flash, make_response, session)
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                set_access_cookies, set_refresh_cookies,
                                unset_jwt_cookies, jwt_required, get_jwt_identity)
from app.extensions import db, bcrypt, limiter
from app.models.user import User, Role
from app.utils.email import send_password_reset_email

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
@limiter.limit("3 per minute", error_message="Demasiados registros. Espera 1 minuto.")
def register():
    if request.method == "POST":
        name     = sanitize(request.form.get("name", "").strip())
        email    = sanitize(request.form.get("email", "").strip().lower())
        password = request.form.get("password", "")

        if not name or not email or not password:
            flash("Todos los campos son obligatorios.", "danger")
            return render_template("auth/register.html")

        if len(password) < 8:
            flash("La contraseña debe tener al menos 8 caracteres.", "danger")
            return render_template("auth/register.html")

        if User.query.filter_by(email=email).first():
            flash("El correo ya está registrado.", "warning")
            return render_template("auth/register.html")

        pw_hash = bcrypt.generate_password_hash(password, rounds=12).decode("utf-8")
        user = User(name=name, email=email, password_hash=pw_hash, role=Role.CLIENT)
        db.session.add(user)
        db.session.commit()
        flash("Cuenta creada. Inicia sesión.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute", methods=["POST"], error_message="Demasiados intentos.")
@limiter.limit("20 per hour", methods=["POST"], error_message="Demasiados intentos.")
def login():
    if request.method == "POST":
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email, is_active=True).first()

        # Delay para prevenir timing attacks
        if not user:
            bcrypt.check_password_hash(
                "$2b$12$KIXVVqkOoFBg1FhGj3h5OeZ1234567890abcdefghijklmnop",
                password
            )
            flash("Credenciales incorrectas.", "danger")
            return render_template("auth/login.html")

        if not bcrypt.check_password_hash(user.password_hash, password):
            flash("Credenciales incorrectas.", "danger")
            return render_template("auth/login.html")

        if user.has_2fa():
            session["pending_2fa_user_id"] = user.id
            return redirect(url_for("auth.verify_2fa"))

        return _issue_tokens_and_redirect(user)

    return render_template("auth/login.html")


@auth_bp.route("/2fa", methods=["GET", "POST"])
def verify_2fa():
    user_id = session.get("pending_2fa_user_id")
    if not user_id:
        return redirect(url_for("auth.login"))

    user = User.query.get(user_id)
    if not user:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        code = request.form.get("code", "").strip()
        totp = pyotp.TOTP(user.totp_secret)
        if totp.verify(code, valid_window=1):
            session.pop("pending_2fa_user_id", None)
            return _issue_tokens_and_redirect(user)
        flash("Código incorrecto. Intenta de nuevo.", "danger")

    return render_template("auth/2fa_verify.html")


@auth_bp.route("/2fa/setup", methods=["GET", "POST"])
@jwt_required()
def setup_2fa():
    user = User.query.get(get_jwt_identity())
    if not user or not user.is_admin():
        flash("Solo administradores pueden activar 2FA.", "danger")
        return redirect(url_for("main.index"))

    if request.method == "POST":
        code   = request.form.get("code", "").strip()
        secret = session.get("temp_totp_secret")
        totp   = pyotp.TOTP(secret)
        if secret and totp.verify(code, valid_window=1):
            user.totp_secret  = secret
            user.totp_enabled = True
            db.session.commit()
            session.pop("temp_totp_secret", None)
            flash("2FA activado exitosamente.", "success")
            return redirect(url_for("admin.dashboard"))
        flash("Código incorrecto. Escanea el QR de nuevo.", "danger")

    secret = pyotp.random_base32()
    session["temp_totp_secret"] = secret
    totp    = pyotp.TOTP(secret)
    otp_uri = totp.provisioning_uri(name=user.email, issuer_name="ShopFlow")

    img = qrcode.make(otp_uri)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    qr_b64 = base64.b64encode(buf.getvalue()).decode()

    return render_template("auth/2fa_setup.html", qr_b64=qr_b64, secret=secret)


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
@limiter.limit("3 per minute", error_message="Demasiadas solicitudes. Espera 1 minuto.")
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        user  = User.query.filter_by(email=email).first()

        flash("Si el correo existe, recibirás un enlace en breve.", "info")

        if user:
            token = secrets.token_urlsafe(32)
            user.reset_token        = token
            user.reset_token_expiry = datetime.now(timezone.utc) + timedelta(minutes=15)
            db.session.commit()
            reset_url = url_for("auth.reset_password", token=token, _external=True)
            try:
                send_password_reset_email(user, reset_url)
            except Exception as e:
                print(f"[EMAIL ERROR] {e}")

        return redirect(url_for("auth.login"))

    return render_template("auth/forgot_password.html")


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    user = User.query.filter_by(reset_token=token).first()
    now  = datetime.now(timezone.utc)

    if not user or not user.reset_token_expiry:
        flash("Enlace inválido.", "danger")
        return redirect(url_for("auth.login"))

    expiry = user.reset_token_expiry
    if expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)

    if now > expiry:
        flash("El enlace ha expirado. Solicita uno nuevo.", "warning")
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":
        password = request.form.get("password", "")
        confirm  = request.form.get("confirm_password", "")

        if password != confirm:
            flash("Las contraseñas no coinciden.", "danger")
            return render_template("auth/reset_password.html", token=token)

        user.password_hash      = bcrypt.generate_password_hash(password, rounds=12).decode()
        user.reset_token        = None
        user.reset_token_expiry = None
        db.session.commit()
        flash("Contraseña actualizada. Inicia sesión.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html", token=token)


@auth_bp.route("/logout")
def logout():
    from flask import session as flask_session
    flask_session.clear()
    response = redirect(url_for("main.index"))
    unset_jwt_cookies(response)
    response.delete_cookie("session")
    response.delete_cookie("access_token_cookie")
    response.delete_cookie("refresh_token_cookie")
    return response


def _issue_tokens_and_redirect(user: User):
    from flask import session as flask_session
    access_token  = create_access_token(identity=user)
    refresh_token = create_refresh_token(identity=user)

    flask_session["user_id"] = user.id
    flask_session["user_role"] = user.role
    flask_session.permanent = True

    destinations = {
        Role.ADMIN:  "admin.dashboard",
        Role.VENDOR: "vendor.dashboard",
        Role.CLIENT: "client.catalog",
    }
    dest = destinations.get(user.role, "main.index")
    resp = make_response(redirect(url_for(dest)))
    set_access_cookies(resp, access_token)
    set_refresh_cookies(resp, refresh_token)
    return resp