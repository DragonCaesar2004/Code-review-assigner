"""
Сервис для работы с командами (Teams)
"""

from sqlalchemy.orm import Session
from src.crud import team_crud, user_crud
from src.schemas.team import TeamSchema, TeamResponse
from src.services.exceptions import TeamExistsException, NotFoundException


class TeamService:
    """Бизнес-логика для команд"""

    def create_team_with_members(
        self, db: Session, team_data: TeamSchema
    ) -> TeamResponse:
        """
        Создать команду и добавить/обновить всех участников

        Бизнес-правила:
        - Команда с таким именем не должна существовать
        - Создаем/обновляем всех пользователей из списка members
        - Операция транзакционная

        Args:
            db: Сессия БД
            team_data: Данные команды с участниками

        Returns:
            TeamResponse с созданной командой

        Raises:
            TeamExistsException: Если команда уже существует
        """
        # Проверка: команда не должна существовать
        if team_crud.exists(db, team_data.team_name):
            raise TeamExistsException(team_data.team_name)

        # Создаем команду
        db_team = team_crud.create_team(db, team_data.team_name)

        # Создаем/обновляем всех участников
        for member in team_data.members:
            user_crud.create_or_update(
                db=db,
                user_id=member.user_id,
                username=member.username,
                team_name=team_data.team_name,
                is_active=member.is_active,
            )

        # Перезагружаем команду с участниками
        db.refresh(db_team)

        return TeamResponse(team=TeamSchema.model_validate(db_team))

    def get_team_with_members(self, db: Session, team_name: str) -> TeamSchema:
        """
        Получить команду с участниками

        Args:
            db: Сессия БД
            team_name: Имя команды

        Returns:
            TeamSchema с участниками

        Raises:
            NotFoundException: Если команда не найдена
        """
        db_team = team_crud.get_by_name(db, team_name)

        if not db_team:
            raise NotFoundException("Team", team_name)

        return TeamSchema.model_validate(db_team)


# Singleton экземпляр для использования в приложении
team_service = TeamService()
