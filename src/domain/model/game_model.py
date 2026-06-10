import uuid
from domain.model.board_model import Board
from domain.model.game_state import GameState


class Game:
    def __init__(self):
        self.id: str = str(uuid.uuid4())
        self.board: Board = Board()
        self.state: str = GameState.WAITING
        self.player1_id: str | None = None
        self.player2_id: str | None = None
        self.player1_mark: str = "X"
        self.player2_mark: str = "O"