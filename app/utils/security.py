from flask import redirect, url_for
from app.models.user import User


def register_jwt_callbacks(jwt):

    @jwt.user_identity_loader
    def user_identity_lookup(user):
        return user.id if hasattr(user, "id") else user

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return User.query.filter_by(id=identity, is_active=True).one_or_none()

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return redirect(url_for("auth.login"))

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return redirect(url_for("auth.login"))

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return redirect(url_for("auth.login"))