"""
Обработчики исключений для FastAPI приложения.
Централизованная обработка кастомных исключений приложения.
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse

from src.services.exceptions import (
    TeamExistsException,
    PRExistsException,
    PRMergedException,
    NotAssignedException,
    NoCandidateException,
    NotFoundException,
)
from src.schemas.error import ErrorResponse, ErrorDetail


async def team_exists_exception_handler(request: Request, exc: TeamExistsException):
    """Обработчик исключения: команда уже существует"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ErrorResponse(
            error=ErrorDetail(code=exc.code, message=exc.message)
        ).model_dump(),
    )


async def pr_exists_exception_handler(request: Request, exc: PRExistsException):
    """Обработчик исключения: PR уже существует"""
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=ErrorResponse(
            error=ErrorDetail(code=exc.code, message=exc.message)
        ).model_dump(),
    )


async def pr_merged_exception_handler(request: Request, exc: PRMergedException):
    """Обработчик исключения: операция недоступна для merged PR"""
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=ErrorResponse(
            error=ErrorDetail(code=exc.code, message=exc.message)
        ).model_dump(),
    )


async def not_assigned_exception_handler(request: Request, exc: NotAssignedException):
    """Обработчик исключения: пользователь не назначен ревьювером"""
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=ErrorResponse(
            error=ErrorDetail(code=exc.code, message=exc.message)
        ).model_dump(),
    )


async def no_candidate_exception_handler(request: Request, exc: NoCandidateException):
    """Обработчик исключения: нет доступных кандидатов"""
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=ErrorResponse(
            error=ErrorDetail(code=exc.code, message=exc.message)
        ).model_dump(),
    )


async def not_found_exception_handler(request: Request, exc: NotFoundException):
    """Обработчик исключения: ресурс не найден"""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=ErrorResponse(
            error=ErrorDetail(code=exc.code, message=exc.message)
        ).model_dump(),
    )


def register_exception_handlers(app):
    """
    Регистрирует все обработчики исключений в приложении FastAPI.
    
    Args:
        app: Экземпляр FastAPI приложения
    """
    app.add_exception_handler(TeamExistsException, team_exists_exception_handler)
    app.add_exception_handler(PRExistsException, pr_exists_exception_handler)
    app.add_exception_handler(PRMergedException, pr_merged_exception_handler)
    app.add_exception_handler(NotAssignedException, not_assigned_exception_handler)
    app.add_exception_handler(NoCandidateException, no_candidate_exception_handler)
    app.add_exception_handler(NotFoundException, not_found_exception_handler)
