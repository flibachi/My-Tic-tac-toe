from web.model.web_board_model import WebBoard
from web.model.web_game_model import WebGame
from domain.model.board_model import Board
from domain.model.game_model import Game


def web_to_domain(web_game: WebGame) -> Game:
    game = Game()
    game.id = web_game.id
    game.board = Board()
    game.board.grid = [row[:] for row in web_game.board.grid]
    return game


def domain_to_web(game: Game) -> WebGame:
    return WebGame(
        id=game.id,
        board=WebBoard(grid=[row[:] for row in game.board.grid])
    )
