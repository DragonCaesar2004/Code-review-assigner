"""
Схемы для обработки ошибок согласно OpenAPI спецификации
"""

from enum import Enum
from pydantic import BaseModel


class ErrorCode(str, Enum):
    """Коды ошибок согласно OpenAPI"""

    TEAM_EXISTS = "TEAM_EXISTS"
    PR_EXISTS = "PR_EXISTS"
    PR_MERGED = "PR_MERGED"
    NOT_ASSIGNED = "NOT_ASSIGNED"
    NO_CANDIDATE = "NO_CANDIDATE"
    NOT_FOUND = "NOT_FOUND"


class ErrorDetail(BaseModel):
    """Детали ошибки"""

    code: ErrorCode
    message: str


class ErrorResponse(BaseModel):
    """Стандартный формат ответа с ошибкой"""

    error: ErrorDetail
