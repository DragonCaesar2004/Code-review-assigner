from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, TYPE_CHECKING

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.user import User


class Team(Base):

    __tablename__ = "teams"

    # Первичный ключ - имя команды (согласно API спецификации)
    team_name: Mapped[str] = mapped_column(String(255), primary_key=True, index=True)

    # Связь: команда содержит множество пользователей
    members: Mapped[List["User"]] = relationship("User", back_populates="team")
