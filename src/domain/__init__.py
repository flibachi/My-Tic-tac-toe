# domain/__init__.py
"""
Domain layer - bussiness logic and models
"""

from domain.model.board_model import Board
from domain.model.game_model import Game
from domain.service.game_service import GameService
from domain.service.game_service_interface import GameServiceInterface

__all__ = [
    'Board',
    'Game',
    'GameService',
    'GameServiceInterface'
]
