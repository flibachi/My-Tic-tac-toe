class GameState:
    WAITING = "WAITING"
    DRAW = "DRAW"
    TURN_PREFIX = "TURN:"
    WIN_PREFIX = "WIN:"

    @staticmethod
    def turn(user_id: str) -> str:
        return f"{GameState.TURN_PREFIX}{user_id}"

    @staticmethod
    def win(user_id: str) -> str:
        return f"{GameState.WIN_PREFIX}{user_id}"

    @staticmethod
    def is_turn(state: str) -> bool:
        return state.startswith(GameState.TURN_PREFIX)
