from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.models.base import Base

# Типы для Generic класса
ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseCRUD(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Базовый класс CRUD операций с Generic типами

    Пример использования:
        class UserCRUD(BaseCRUD[User, UserCreateSchema, UserUpdateSchema]):
            pass
    """

    def __init__(self, model: Type[ModelType], pk_field: str = "id"):
        """
        Инициализация CRUD класса

        Args:
            model: SQLAlchemy модель
            pk_field: Имя поля первичного ключа (по умолчанию "id")
        """
        self.model = model
        self.pk_field = pk_field

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """
        Получить запись по первичному ключу

        Args:
            db: Сессия БД
            id: Значение первичного ключа

        Returns:
            Объект модели или None
        """
        return (
            db.query(self.model)
            .filter(getattr(self.model, self.pk_field) == id)
            .first()
        )

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        Получить список записей с пагинацией

        Args:
            db: Сессия БД
            skip: Количество записей для пропуска
            limit: Максимальное количество записей

        Returns:
            Список объектов модели
        """
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Создать новую запись

        Args:
            db: Сессия БД
            obj_in: Pydantic схема с данными для создания

        Returns:
            Созданный объект модели
        """
        obj_in_data = (
            obj_in.model_dump() if hasattr(obj_in, "model_dump") else obj_in.dict()
        )
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        """
        Обновить существующую запись

        Args:
            db: Сессия БД
            db_obj: Существующий объект модели из БД
            obj_in: Pydantic схема или словарь с новыми данными

        Returns:
            Обновленный объект модели
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = (
                obj_in.model_dump(exclude_unset=True)
                if hasattr(obj_in, "model_dump")
                else obj_in.dict(exclude_unset=True)
            )

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: Any) -> Optional[ModelType]:
        """
        Удалить запись по первичному ключу

        Args:
            db: Сессия БД
            id: Значение первичного ключа

        Returns:
            Удаленный объект или None
        """
        obj = self.get(db, id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj

    def exists(self, db: Session, id: Any) -> bool:
        """
        Проверить существование записи по первичному ключу

        Args:
            db: Сессия БД
            id: Значение первичного ключа

        Returns:
            True если запись существует, иначе False
        """
        return (
            db.query(self.model)
            .filter(getattr(self.model, self.pk_field) == id)
            .first()
            is not None
        )
