from flask import jsonify, g
from web.module.game_controller import create_game_controller
from web.auth.authenticator import user_authenticator
from domain.service.user_service import UserService
from di.container import Container

_user_service = UserService()


def register_routes(app):
    container = Container()
    service = container.get_service()
    repository = container.get_repository()

    bp = create_game_controller(service, repository)
    if bp is None:
        raise RuntimeError("Failed to create game controller blueprint")
    app.register_blueprint(bp, url_prefix='/game')

    # ------------------------------------------------------------------ #
    # GET /user/<uuid>  — Get user info by UUID                           #
    # ------------------------------------------------------------------ #
    @app.route("/user/<string:user_id>", methods=["GET"])
    @user_authenticator.require_auth
    def get_user(user_id: str):
        """Return public user information by UUID."""
        user = _user_service.get_by_id(user_id)
        if user is None:
            return jsonify({"error": "User not found"}), 404
        return jsonify({"id": user.id, "login": user.login}), 200