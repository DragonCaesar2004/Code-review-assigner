# Экспорт всех CRUD классов для удобного импорта
from .base import BaseCRUD
from .team import team_crud
from .user import user_crud
from .pull_request import pull_request_crud
from .pr_reviewer import pr_reviewer_crud

__all__ = [
    "BaseCRUD",
    "team_crud",
    "user_crud",
    "pull_request_crud",
    "pr_reviewer_crud",
]
