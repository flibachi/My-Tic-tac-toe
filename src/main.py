from flask import Flask, render_template
from datasource.model.models import db
from web.route.game_routes import register_routes
from web.module.auth_controller import auth_bp


def create_app() -> Flask:
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/tictactoe_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()

    # Auth endpoints are open (no require_auth)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    # All game/user endpoints require auth (enforced per-route)
    register_routes(app)

    @app.route("/")
    def index():
        return render_template("index.html")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)
