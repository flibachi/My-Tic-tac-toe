import base64
from web.model.web_auth_model import SignUpRequest
from domain.service.user_service import UserService


class AuthService:
    def __init__(self, user_service: UserService | None = None):
        self._user_service = user_service or UserService()

    def register(self, request: SignUpRequest) -> bool:
        return self._user_service.register(request)

    def authorize(self, authorization_header: str) -> str | None:
        if not authorization_header.startswith("Basic "):
            return None

        try:
            encoded = authorization_header[len("Basic "):]
            decoded = base64.b64decode(encoded).decode("utf-8")
            login, password = decoded.split(":", 1)
        except Exception:
            return None

        return self._user_service.authenticate(login, password)
