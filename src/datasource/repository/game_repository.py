from datasource.repository.game_repository_interface import GameRepositoryInterface
from domain.model.game_model import Game
from domain.model.board_model import Board
from domain.model.game_state import GameState
from datasource.model.models import GameModel, db


class GameRepository(GameRepositoryInterface):

    def save(self, game: Game) -> None:
        ds_game = db.session.get(GameModel, game.id)
        if not ds_game:
            ds_game = GameModel(id=game.id)
            db.session.add(ds_game)

        ds_game.board = game.board.grid
        ds_game.state = game.state
        ds_game.player1_id = game.player1_id
        ds_game.player2_id = game.player2_id
        ds_game.player1_mark = game.player1_mark
        ds_game.player2_mark = game.player2_mark
        db.session.commit()

    def get(self, game_id: str) -> Game | None:
        ds_game = db.session.get(GameModel, game_id)
        if not ds_game:
            return None

        game = Game()
        game.id = ds_game.id
        game.board = Board()
        game.board.grid = ds_game.board
        game.state = ds_game.state
        game.player1_id = ds_game.player1_id
        game.player2_id = ds_game.player2_id
        game.player1_mark = ds_game.player1_mark
        game.player2_mark = ds_game.player2_mark
        return game

    def get_waiting(self) -> list[Game]:
        """Return all games in WAITING state."""
        rows = GameModel.query.filter_by(state=GameState.WAITING).all()
        games = []
        for ds_game in rows:
            game = Game()
            game.id = ds_game.id
            game.board = Board()
            game.board.grid = ds_game.board
            game.state = ds_game.state
            game.player1_id = ds_game.player1_id
            game.player2_id = ds_game.player2_id
            game.player1_mark = ds_game.player1_mark
            game.player2_mark = ds_game.player2_mark
            games.append(game)
        return games