from werkzeug.security import generate_password_hash, check_password_hash
from datasource.model.models import UserModel, db
from web.model.web_auth_model import SignUpRequest
from domain.model.user_model import User


class UserService:

    def register(self, request: SignUpRequest) -> bool:
        """Register a new user. Returns True on success, False if login already taken."""
        if UserModel.query.filter_by(login=request.login).first():
            return False

        hashed_pw = generate_password_hash(request.password)
        new_user = UserModel(login=request.login, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        return True

    def authenticate(self, login: str, password: str) -> str | None:
        """Verify credentials. Returns user UUID on success, None otherwise."""
        user = UserModel.query.filter_by(login=login).first()
        if user and check_password_hash(user.password, password):
            return user.id
        return None

    def get_by_id(self, user_id: str) -> User | None:
        """Return user by UUID."""
        user = db.session.get(UserModel, user_id)
        if user is None:
            return None
        return User(id=user.id, login=user.login)
