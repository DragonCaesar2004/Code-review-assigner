# Экспорт всех роутеров
from .teams import router as teams_router
from .users import router as users_router
from .pull_requests import router as pull_requests_router
from .health import router as health_router
from .stats import router as stats_router

__all__ = [
    "teams_router",
    "users_router",
    "pull_requests_router",
    "health_router",
    "stats_router",
]
