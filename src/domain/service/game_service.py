import copy
from domain.service.game_service_interface import GameServiceInterface
from domain.model.game_model import Game


class GameService(GameServiceInterface):

    # ------------------------------------------------------------------ #
    #  Публичный API (реализация интерфейса)                              #
    # ------------------------------------------------------------------ #

    def get_next_move(self, game: Game) -> Game:
        """Выбирает лучший ход для компьютера с помощью алгоритма Минимакс."""
        board = copy.deepcopy(game.board.grid)
        size = game.board.size
        best_score = -float('inf')
        best_move = None

        for i in range(size):
            for j in range(size):
                if board[i][j] == 0:
                    board[i][j] = 2
                    score = self._minimax(board, 0, False)
                    board[i][j] = 0
                    if score > best_score:
                        best_score = score
                        best_move = (i, j)

        if best_move:
            game.board.grid[best_move[0]][best_move[1]] = 2

        return game

    def validate_board(self, old_game: Game, new_game: Game) -> bool:
        """Проверяет, что игрок изменил ровно одну пустую клетку и не тронул остальные."""
        if old_game.id != new_game.id:
            return False

        size = old_game.board.size
        old_board = old_game.board.grid
        new_board = new_game.board.grid
        changes = 0

        for i in range(size):
            for j in range(size):
                old_val = old_board[i][j]
                new_val = new_board[i][j]

                if old_val != 0 and old_val != new_val:
                    return False
                if new_val not in (0, 1, 2):
                    return False
                if old_val == 0 and new_val != 0:
                    changes += 1

        return changes == 1

    def is_game_over(self, game: Game) -> bool:
        """Возвращает True, если игра завершена (победа или ничья)."""
        return self.determine_winner(game.board.grid) is not None

    def determine_winner(self, board: list) -> int | None:
        """
        Определяет победителя:
        -1  — победил игрок (1)
         1  — победил компьютер (2)
         0  — ничья
        None — игра продолжается
        """
        size = len(board)

        for i in range(size):
            if all(cell == 1 for cell in board[i]):
                return -1
            if all(cell == 2 for cell in board[i]):
                return 1
            if all(row[i] == 1 for row in board):
                return -1
            if all(row[i] == 2 for row in board):
                return 1

        if all(board[i][i] == 1 for i in range(size)):
            return -1
        if all(board[i][i] == 2 for i in range(size)):
            return 1
        if all(board[i][size - 1 - i] == 1 for i in range(size)):
            return -1
        if all(board[i][size - 1 - i] == 2 for i in range(size)):
            return 1

        if all(cell != 0 for row in board for cell in row):
            return 0

        return None

    # ------------------------------------------------------------------ #
    #  Вспомогательные методы минимакса (приватные)                       #
    # ------------------------------------------------------------------ #

    def _minimax(self, board: list, depth: int, is_maximizing: bool) -> int:
        result = self.determine_winner(board)
        if result is not None:
            # Весовой коэффициент: компьютер предпочитает быструю победу,
            # игрок предпочитает затянуть проигрыш.
            return result * (10 - depth)

        if is_maximizing:
            best_score = -float('inf')
            for i in range(len(board)):
                for j in range(len(board[0])):
                    if board[i][j] == 0:
                        board[i][j] = 2
                        score = self._minimax(board, depth + 1, False)
                        board[i][j] = 0
                        best_score = max(score, best_score)
            return best_score
        else:
            best_score = float('inf')
            for i in range(len(board)):
                for j in range(len(board[0])):
                    if board[i][j] == 0:
                        board[i][j] = 1
                        score = self._minimax(board, depth + 1, True)
                        board[i][j] = 0
                        best_score = min(score, best_score)
            return best_score
