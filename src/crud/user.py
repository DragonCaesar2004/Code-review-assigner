"""
CRUD операции для пользователей (Users)
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from src.crud.base import BaseCRUD
from src.models.user import User
from src.schemas.user import UserSchema


class UserCRUD(BaseCRUD[User, UserSchema, UserSchema]):
    """CRUD операции для пользователей"""

    def __init__(self):
        super().__init__(model=User, pk_field="user_id")

    def get_by_id(self, db: Session, user_id: str) -> Optional[User]:
        """
        Получить пользователя по ID

        Args:
            db: Сессия БД
            user_id: ID пользователя

        Returns:
            Объект User или None
        """
        return self.get(db, user_id)

    def create_or_update(
        self, db: Session, user_id: str, username: str, team_name: str, is_active: bool
    ) -> User:
        """
        Создать пользователя или обновить существующего

        Args:
            db: Сессия БД
            user_id: ID пользователя
            username: Имя пользователя
            team_name: Имя команды
            is_active: Флаг активности

        Returns:
            Созданный или обновленный объект User
        """
        db_user = self.get_by_id(db, user_id)

        if db_user:
            # Обновляем существующего пользователя
            db_user.username = username
            db_user.team_name = team_name
            db_user.is_active = is_active
            db.commit()
            db.refresh(db_user)
        else:
            # Создаем нового пользователя
            db_user = User(
                user_id=user_id,
                username=username,
                team_name=team_name,
                is_active=is_active,
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)

        return db_user

    def set_active_status(
        self, db: Session, user_id: str, is_active: bool
    ) -> Optional[User]:
        """
        Установить статус активности пользователя

        Args:
            db: Сессия БД
            user_id: ID пользователя
            is_active: Новый статус активности

        Returns:
            Обновленный объект User или None если не найден
        """
        db_user = self.get_by_id(db, user_id)
        if db_user:
            db_user.is_active = is_active
            db.commit()
            db.refresh(db_user)
        return db_user

    def get_active_team_members(
        self, db: Session, team_name: str, exclude_user_id: Optional[str] = None
    ) -> List[User]:
        """
        Получить активных участников команды (с возможностью исключить пользователя)

        Args:
            db: Сессия БД
            team_name: Имя команды
            exclude_user_id: ID пользователя для исключения (например, автора PR)

        Returns:
            Список активных пользователей команды
        """
        query = db.query(User).filter(
            User.team_name == team_name, User.is_active == True
        )

        if exclude_user_id:
            query = query.filter(User.user_id != exclude_user_id)

        return query.all()

    def get_by_team(self, db: Session, team_name: str) -> List[User]:
        """
        Получить всех участников команды

        Args:
            db: Сессия БД
            team_name: Имя команды

        Returns:
            Список всех пользователей команды
        """
        return db.query(User).filter(User.team_name == team_name).all()


# Singleton экземпляр для использования в приложении
user_crud = UserCRUD()
