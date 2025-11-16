"""
API endpoints для работы с пользователями (Users)
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from src.models.database import get_db
from src.schemas.user import UserSetActiveSchema, UserResponse
from src.schemas.review import UserReviewsResponse
from src.services import user_service, pull_request_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/setIsActive", response_model=UserResponse, status_code=status.HTTP_200_OK
)
def set_user_active_status(data: UserSetActiveSchema, db: Session = Depends(get_db)):
    """
    Установить флаг активности пользователя

    - **200**: Обновлённый пользователь
    - **404**: Пользователь не найден (NOT_FOUND)
    """
    return user_service.set_user_active_status(db, data.user_id, data.is_active)


@router.get(
    "/getReview", response_model=UserReviewsResponse, status_code=status.HTTP_200_OK
)
def get_user_reviews(user_id: str, db: Session = Depends(get_db)):
    """
    Получить PR'ы, где пользователь назначен ревьювером

    - **200**: Список PR'ов пользователя
    """
    return pull_request_service.get_user_reviews(db, user_id)
