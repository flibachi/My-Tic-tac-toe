import uuid
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from domain.model.game_state import GameState

db = SQLAlchemy()


class UserModel(db.Model):
    __tablename__ = 'users'

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    login: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)


class GameModel(db.Model):
    __tablename__ = 'games'

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    state: Mapped[str] = mapped_column(String(50), default=GameState.WAITING, nullable=False)
    board: Mapped[list] = mapped_column(JSONB, nullable=False)
    player1_id: Mapped[str] = mapped_column(String(36), ForeignKey('users.id'), nullable=False)
    player2_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    # "X" for player1, "O" for player2 (or "COMPUTER")
    player1_mark: Mapped[str] = mapped_column(String(1), default="X", nullable=False)
    player2_mark: Mapped[str] = mapped_column(String(1), default="O", nullable=False)