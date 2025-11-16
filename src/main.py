"""Главный файл приложения FastAPI."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api import teams_router, users_router, pull_requests_router, health_router, stats_router
from src.api.exception_handlers import register_exception_handlers

app = FastAPI(
    title="PR Reviewer Assignment Service",
    description="Сервис назначения ревьюеров для Pull Request'ов",
    version="1.0.0",
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Регистрация обработчиков исключений
register_exception_handlers(app)

# Подключение роутеров
app.include_router(health_router)
app.include_router(teams_router)
app.include_router(users_router)
app.include_router(pull_requests_router)
app.include_router(stats_router)


@app.get("/")
async def root():
    """Корневой эндпоинт."""
    return {
        "message": "PR Reviewer Assignment Service",
        "version": "1.0.0",
        "status": "running",
    }
