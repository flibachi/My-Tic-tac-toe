# datasoure/repository/__init__.py
"""
Repositories for data access
"""

from datasource.repository.game_repository import GameRepository
from datasource.repository.game_repository_interface import GameRepositoryInterface


__all__ = ['GameRepository', 'GameRepositoryInterface']
