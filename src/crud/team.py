"""
CRUD операции для команд (Teams)
"""

from typing import Optional
from sqlalchemy.orm import Session
from src.crud.base import BaseCRUD
from src.models.team import Team
from src.schemas.team import TeamSchema


class TeamCRUD(BaseCRUD[Team, TeamSchema, TeamSchema]):
    """CRUD операции для команд"""

    def __init__(self):
        super().__init__(model=Team, pk_field="team_name")

    def get_by_name(self, db: Session, team_name: str) -> Optional[Team]:
        """
        Получить команду по имени

        Args:
            db: Сессия БД
            team_name: Имя команды

        Returns:
            Объект Team или None
        """
        return self.get(db, team_name)

    def create_team(self, db: Session, team_name: str) -> Team:
        """
        Создать команду (без участников)

        Args:
            db: Сессия БД
            team_name: Имя команды

        Returns:
            Созданный объект Team
        """
        db_team = Team(team_name=team_name)
        db.add(db_team)
        db.commit()
        db.refresh(db_team)
        return db_team


# Singleton экземпляр для использования в приложении
team_crud = TeamCRUD()
