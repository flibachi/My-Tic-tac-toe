# domain/service/__init__.py
"""
Domain service with business logic
"""

from domain.service.game_service import GameService
from domain.service.game_service_interface import GameServiceInterface

__all__ = ['GameService', 'GameServiceInterface']
