from functools import wraps
from flask import jsonify, redirect, url_for, session, request
from flask_jwt_extended import verify_jwt_in_request, get_current_user, decode_token
from app.models.user import Role


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request(locations=["cookies", "headers"])
        except Exception:
            # Intentar con sesión de Flask
            token = session.get("access_token")
            if not token:
                return redirect(url_for("auth.login"))
            try:
                from app.extensions import db
                from app.models.user import User
                data = decode_token(token)
                user = User.query.get(data["sub"])
                if not user:
                    return redirect(url_for("auth.login"))
            except Exception:
                return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = None
            try:
                verify_jwt_in_request(locations=["cookies", "headers"])
                user = get_current_user()
            except Exception:
                token = session.get("access_token")
                if not token:
                    return redirect(url_for("auth.login"))
                try:
                    from app.models.user import User
                    data = decode_token(token)
                    user = User.query.get(data["sub"])
                except Exception:
                    return redirect(url_for("auth.login"))

            if not user or user.role not in roles:
                return redirect(url_for("auth.login"))
            return f(*args, **kwargs)
        return decorated
    return decorator


def admin_required(f):
    return role_required(Role.ADMIN)(f)


def vendor_required(f):
    return role_required(Role.ADMIN, Role.VENDOR)(f)


def client_required(f):
    return role_required(Role.CLIENT)(f)