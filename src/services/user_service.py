"""
Сервис для работы с пользователями (Users)
"""

from sqlalchemy.orm import Session
from src.crud import user_crud
from src.schemas.user import UserSchema, UserResponse
from src.services.exceptions import NotFoundException


class UserService:
    """Бизнес-логика для пользователей"""

    def set_user_active_status(
        self, db: Session, user_id: str, is_active: bool
    ) -> UserResponse:
        """
        Установить статус активности пользователя

        Args:
            db: Сессия БД
            user_id: ID пользователя
            is_active: Новый статус активности

        Returns:
            UserResponse с обновленным пользователем

        Raises:
            NotFoundException: Если пользователь не найден
        """
        db_user = user_crud.set_active_status(db, user_id, is_active)

        if not db_user:
            raise NotFoundException("User", user_id)

        return UserResponse(user=UserSchema.model_validate(db_user))

    def get_user(self, db: Session, user_id: str) -> UserSchema:
        """
        Получить пользователя по ID

        Args:
            db: Сессия БД
            user_id: ID пользователя

        Returns:
            UserSchema

        Raises:
            NotFoundException: Если пользователь не найден
        """
        db_user = user_crud.get_by_id(db, user_id)

        if not db_user:
            raise NotFoundException("User", user_id)

        return UserSchema.model_validate(db_user)


# Singleton экземпляр для использования в приложении
user_service = UserService()
