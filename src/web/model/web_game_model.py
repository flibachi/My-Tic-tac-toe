from dataclasses import dataclass
from web.model.web_board_model import WebBoard


@dataclass
class WebGame:
    id: str
    board: WebBoard
