"""
Health check endpoint
"""

from fastapi import APIRouter, status

router = APIRouter(tags=["Health"])


@router.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """
    Проверка здоровья сервиса

    - **200**: Сервис работает
    """
    return {"status": "healthy"}
