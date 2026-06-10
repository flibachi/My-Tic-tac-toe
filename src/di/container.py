from datasource.repository.game_repository import GameRepository
from datasource.service.game_service_impl import GameServiceWithRepo


class Container:
    """
    DI-контейнер. Зависимости (репозиторий и сервис) — синглтоны:
    один экземпляр на всё время жизни приложения.
    """
    _repository_instance: GameRepository | None = None
    _service_instance: GameServiceWithRepo | None = None

    def __init__(self):
        if Container._repository_instance is None:
            Container._repository_instance = GameRepository()

        if Container._service_instance is None:
            Container._service_instance = GameServiceWithRepo(Container._repository_instance)

    def get_repository(self) -> GameRepository:
        return Container._repository_instance

    def get_service(self) -> GameServiceWithRepo:
        return Container._service_instance
