"""
Кастомные исключения для бизнес-логики приложения
"""

from src.schemas.error import ErrorCode


class AppException(Exception):
    """Базовое исключение приложения"""

    def __init__(self, code: ErrorCode, message: str):
        self.code = code
        self.message = message
        super().__init__(self.message)


class TeamExistsException(AppException):
    """Команда уже существует"""

    def __init__(self, team_name: str):
        super().__init__(
            code=ErrorCode.TEAM_EXISTS, message=f"Team '{team_name}' already exists"
        )


class PRExistsException(AppException):
    """Pull Request уже существует"""

    def __init__(self, pull_request_id: str):
        super().__init__(
            code=ErrorCode.PR_EXISTS,
            message=f"Pull Request '{pull_request_id}' already exists",
        )


class PRMergedException(AppException):
    """Операция недоступна для merged PR"""

    def __init__(self, pull_request_id: str):
        super().__init__(
            code=ErrorCode.PR_MERGED,
            message=f"Cannot reassign reviewers on merged PR '{pull_request_id}'",
        )


class NotAssignedException(AppException):
    """Пользователь не назначен ревьювером на этот PR"""

    def __init__(self, user_id: str, pull_request_id: str):
        super().__init__(
            code=ErrorCode.NOT_ASSIGNED,
            message=f"User '{user_id}' is not assigned as reviewer to PR '{pull_request_id}'",
        )


class NoCandidateException(AppException):
    """Нет доступных кандидатов для назначения"""

    def __init__(self, reason: str = "No active candidates available"):
        super().__init__(code=ErrorCode.NO_CANDIDATE, message=reason)


class NotFoundException(AppException):
    """Ресурс не найден"""

    def __init__(self, resource: str, identifier: str):
        super().__init__(
            code=ErrorCode.NOT_FOUND, message=f"{resource} '{identifier}' not found"
        )
