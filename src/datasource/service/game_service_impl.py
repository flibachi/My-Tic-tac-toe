from domain.service.game_service_interface import GameServiceInterface
from domain.service.game_service import GameService
from domain.model.game_model import Game
from datasource.repository.game_repository_interface import GameRepositoryInterface


class GameServiceWithRepo(GameServiceInterface):
    """
    Обёртка над GameService, которая добавляет персистентность:
    после каждого хода компьютера состояние игры сохраняется в репозиторий.
    Вся игровая логика (минимакс, валидация, проверка победы) делегирована
    доменному GameService — дублирования нет.
    """

    def __init__(self, repository: GameRepositoryInterface):
        self.repository = repository
        self._game_service = GameService()

    def get_next_move(self, game: Game) -> Game:
        updated_game = self._game_service.get_next_move(game)
        self.repository.save(updated_game)
        return updated_game

    def validate_board(self, old_game: Game, new_game: Game) -> bool:
        return self._game_service.validate_board(old_game, new_game)

    def is_game_over(self, game: Game) -> bool:
        return self._game_service.is_game_over(game)

    def determine_winner(self, board: list) -> int | None:
        return self._game_service.determine_winner(board)
