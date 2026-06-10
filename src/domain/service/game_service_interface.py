from abc import ABC, abstractmethod
from domain.model.game_model import Game


class GameServiceInterface(ABC):

    @abstractmethod
    def get_next_move(self, game: Game) -> Game:
        """Вычисляет и делает следующий ход с помощью алгоритма Минимакс."""
        pass

    @abstractmethod
    def validate_board(self, old_game: Game, new_game: Game) -> bool:
        """Проверяет, не были ли изменены уже сделанные ходы."""
        pass

    @abstractmethod
    def is_game_over(self, game: Game) -> bool:
        """Проверяет, завершена ли игра."""
        pass

    @abstractmethod
    def determine_winner(self, board: list) -> int | None:
        """
        Определяет победителя:
        -1  — победил игрок (1)
         1  — победил компьютер (2)
         0  — ничья
        None — игра продолжается
        """
        pass
