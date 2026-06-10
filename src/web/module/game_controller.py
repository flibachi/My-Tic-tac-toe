from flask import Blueprint, request, jsonify, g
from web.mapper.web_mapper import web_to_domain, domain_to_web
from web.model.web_game_model import WebGame, WebBoard
from datasource.repository.game_repository_interface import GameRepositoryInterface
from domain.service.game_service_interface import GameServiceInterface
from domain.service.user_service import UserService
from domain.model.game_model import Game
from domain.model.game_state import GameState
from web.auth.authenticator import user_authenticator

_user_service = UserService()


def _turn_state(user_id: str) -> str:
    return GameState.turn(user_id)


def create_game_controller(
    service: GameServiceInterface,
    repository: GameRepositoryInterface,
) -> Blueprint:
    bp = Blueprint("game", __name__)

    # ------------------------------------------------------------------ #
    # POST /game  — Create a new game with COMPUTER or MULTIPLAYER        #
    # ------------------------------------------------------------------ #
    @bp.route("", methods=["POST"])
    @user_authenticator.require_auth
    def create_game():
        """
        Body: {"mode": "COMPUTER" | "MULTIPLAYER"}
        Creates a new game. In COMPUTER mode the AI is player2 immediately.
        In MULTIPLAYER mode the game waits for a second player to join.
        """
        data = request.get_json() or {}
        mode = data.get("mode", "COMPUTER")
        opponent_user_id = data.get("opponent_user_id")

        game = Game()
        game.player1_id = g.user_id
        game.player1_mark = "X"
        game.player2_mark = "O"

        if opponent_user_id:
            if _user_service.get_by_id(opponent_user_id) is None:
                return jsonify({"error": "Opponent user not found"}), 404
            if opponent_user_id == g.user_id:
                return jsonify({"error": "Opponent should be a different user"}), 400
            game.player2_id = opponent_user_id
            game.state = _turn_state(game.player1_id)
        elif mode == "COMPUTER":
            game.player2_id = "COMPUTER"
            game.state = _turn_state(game.player1_id)
        else:
            game.state = GameState.WAITING

        repository.save(game)

        return jsonify({
            "id": game.id,
            "state": game.state,
            "board": game.board.grid,
            "player1_id": game.player1_id,
            "player2_id": game.player2_id,
            "player1_mark": game.player1_mark,
            "player2_mark": game.player2_mark,
        }), 201

    # ------------------------------------------------------------------ #
    # GET /game/available  — Getting the available current games          #
    # ------------------------------------------------------------------ #
    @bp.route("/available", methods=["GET"])
    @user_authenticator.require_auth
    def get_available_games():
        """Returns all games in WAITING state."""
        games = repository.get_waiting()
        return jsonify([
            {
                "id": g_obj.id,
                "player1_id": g_obj.player1_id,
                "state": g_obj.state,
            }
            for g_obj in games
        ]), 200

    # ------------------------------------------------------------------ #
    # POST /game/<id>/join  — Join an existing multiplayer game           #
    # ------------------------------------------------------------------ #
    @bp.route("/<string:game_id>/join", methods=["POST"])
    @user_authenticator.require_auth
    def join_game(game_id: str):
        """Allow a second player to join a WAITING game."""
        game = repository.get(game_id)
        if game is None:
            return jsonify({"error": "Game not found"}), 404
        if game.state != GameState.WAITING:
            return jsonify({"error": "Game already started or finished"}), 400
        if game.player1_id == g.user_id:
            return jsonify({"error": "Cannot join your own game"}), 400

        game.player2_id = g.user_id
        game.state = _turn_state(game.player1_id)
        repository.save(game)

        return jsonify({
            "message": "Successfully joined the game",
            "state": game.state,
            "board": game.board.grid,
            "player1_mark": game.player1_mark,
            "player2_mark": game.player2_mark,
        }), 200

    # ------------------------------------------------------------------ #
    # GET /game/<id>  — Get current game state                            #
    # ------------------------------------------------------------------ #
    @bp.route("/<string:game_id>", methods=["GET"])
    @user_authenticator.require_auth
    def get_game(game_id: str):
        """Return the current state of a game."""
        game = repository.get(game_id)
        if game is None:
            return jsonify({"error": "Game not found"}), 404

        if g.user_id not in (game.player1_id, game.player2_id):
            return jsonify({"error": "You are not a participant of this game"}), 403

        return jsonify({
            "id": game.id,
            "state": game.state,
            "board": game.board.grid,
            "player1_id": game.player1_id,
            "player2_id": game.player2_id,
            "player1_mark": game.player1_mark,
            "player2_mark": game.player2_mark,
        }), 200

    # ------------------------------------------------------------------ #
    # POST /game/<id>  — Make a move                                      #
    # ------------------------------------------------------------------ #
    @bp.route("/<string:game_id>", methods=["POST"])
    @user_authenticator.require_auth
    def play_game(game_id: str):
        """
        Body: {"board": [[...]]}
        Processes the player's move, validates it, determines winner,
        and triggers computer move if in COMPUTER mode.
        """
        try:
            data = request.get_json()
            if not data or not isinstance(data.get("board"), list):
                return jsonify({"error": "Invalid 'board' field format"}), 400

            original_game = repository.get(game_id)
            if original_game is None:
                return jsonify({"error": "Game not found"}), 404

            if not GameState.is_turn(original_game.state):
                return jsonify({"error": f"Game is not active. Current state: {original_game.state}"}), 400

            is_player_1 = (g.user_id == original_game.player1_id)
            is_player_2 = (g.user_id == original_game.player2_id)

            if not is_player_1 and not is_player_2:
                return jsonify({"error": "You are not a participant of this game"}), 403
            if original_game.state != _turn_state(g.user_id):
                return jsonify({"error": "Not your turn"}), 403

            user_game = web_to_domain(WebGame(id=game_id, board=WebBoard(grid=data["board"])))
            user_game.player1_id = original_game.player1_id
            user_game.player2_id = original_game.player2_id
            user_game.player1_mark = original_game.player1_mark
            user_game.player2_mark = original_game.player2_mark
            user_game.state = original_game.state

            expected_mark = 1 if is_player_1 else 2
            if not service.validate_board(original_game, user_game):
                return jsonify({"error": "Invalid board state (illegal move)"}), 400
            if not _is_expected_mark_move(original_game.board.grid, user_game.board.grid, expected_mark):
                return jsonify({"error": "Invalid move mark for current player"}), 400

            # Check result after human move
            _update_game_state(service, user_game)

            # If game still ongoing, switch turns
            if GameState.is_turn(user_game.state):
                next_player = user_game.player2_id if is_player_1 else user_game.player1_id
                user_game.state = _turn_state(next_player)

                # If it's the computer's turn, make the AI move
                if user_game.state == _turn_state("COMPUTER") and user_game.player2_id == "COMPUTER":
                    user_game = service.get_next_move(user_game)
                    _update_game_state(service, user_game)
                    # Return turn to player 1 if still going
                    if user_game.state == _turn_state("COMPUTER"):
                        user_game.state = _turn_state(user_game.player1_id)

            repository.save(user_game)

            return jsonify({
                "message": "Move accepted",
                "state": user_game.state,
                "board": domain_to_web(user_game).board.grid,
                "player1_mark": user_game.player1_mark,
                "player2_mark": user_game.player2_mark,
            }), 200

        except Exception as e:
            return jsonify({"error": f"Error processing request: {str(e)}"}), 500

    return bp


def _update_game_state(service: GameServiceInterface, game: Game) -> None:
    """Determine winner and update game state accordingly."""
    winner = service.determine_winner(game.board.grid)
    if winner == -1:
        game.state = GameState.win(game.player1_id)
    elif winner == 1:
        game.state = GameState.win(game.player2_id)
    elif winner == 0:
        game.state = GameState.DRAW
    elif GameState.is_turn(game.state):
        return


def _is_expected_mark_move(old_board: list, new_board: list, expected_mark: int) -> bool:
    for i in range(len(old_board)):
        for j in range(len(old_board[i])):
            if old_board[i][j] == 0 and new_board[i][j] != 0:
                return new_board[i][j] == expected_mark
    return False
