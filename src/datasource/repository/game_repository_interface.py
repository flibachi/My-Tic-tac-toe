from abc import ABC, abstractmethod
from domain.model.game_model import Game


class GameRepositoryInterface(ABC):

    @abstractmethod
    def save(self, game: Game) -> None:
        pass

    @abstractmethod
    def get(self, game_id: str) -> Game | None:
        pass

    @abstractmethod
    def get_waiting(self) -> list[Game]:
        pass
