from functools import wraps
from flask import request, jsonify, g
from domain.service.auth_service import AuthService


class UserAuthenticator:
    """
    Validates Basic Auth for protected endpoints.
    If validation succeeds, request execution continues.
    If validation fails, returns 401 and does not execute endpoint handler.
    """

    def __init__(self, auth_service: AuthService | None = None):
        self._auth_service = auth_service or AuthService()

    def require_auth(self, f):
        """Decorator for endpoints that require authorization."""
        @wraps(f)
        def decorated(*args, **kwargs):
            auth_header = request.headers.get("Authorization", "")
            user_id = self._auth_service.authorize(auth_header)
            if not user_id:
                return jsonify({"error": "Invalid credentials"}), 401

            g.user_id = user_id
            return f(*args, **kwargs)

        return decorated


user_authenticator = UserAuthenticator()
