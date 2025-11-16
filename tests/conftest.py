"""
Pytest fixtures для E2E/интеграционного тестирования API.

Best Practices:
- Использует in-memory SQLite для быстрых тестов
- Каждый тест получает чистую сессию БД (автоматический rollback)
- TestClient с переопределением зависимости get_db
- Фикстуры для создания тестовых данных (команды, пользователи, PR)
"""

import os
from typing import Generator, Dict
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Устанавливаем DATABASE_URL для тестов перед импортом приложения
# Используем file::memory:?cache=shared чтобы все соединения использовали одну БД
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from src.main import app
from src.models.base import Base
from src.models.database import get_db, engine as app_engine

# Импортируем все модели, чтобы они были зарегистрированы в Base.metadata
from src.models.team import Team
from src.models.user import User
from src.models.pull_request import PullRequest
from src.models.pr_reviewer import PRReviewer


# ВАЖНО: Используем StaticPool для in-memory SQLite
# Это гарантирует, что все соединения используют одну и ту же базу данных в памяти
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # Критично для in-memory SQLite!
    echo=False,  # Отключаем SQL логирование для чистоты вывода
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создаём таблицы один раз для всего тестового модуля
Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """
    Фикстура сессии БД для каждого теста.

    Best Practice:
    - scope="function" - каждый тест получает свежую БД
    - Использует транзакцию для изоляции (быстрее чем drop/create)
    - Rollback после теста восстанавливает чистое состояние
    """
    # Создаём connection для управления транзакцией
    connection = engine.connect()
    transaction = connection.begin()

    # Создаём сессию, привязанную к этой connection
    session = TestingSessionLocal(bind=connection)

    try:
        yield session
    finally:
        session.close()
        # Откат транзакции - все изменения аннулируются
        transaction.rollback()
        connection.close()


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """
    TestClient с переопределением зависимости get_db на тестовую сессию.

    Best Practice:
    - Переопределяем только get_db, остальная логика приложения работает как в проде
    - Очищаем overrides после теста
    """

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# Фикстуры для создания тестовых данных (Arrange phase для E2E)


@pytest.fixture()
def sample_team(client: TestClient) -> Dict:
    """
    Создаёт тестовую команду 'backend' с 3 участниками.

    Returns:
        Словарь с данными созданной команды
    """
    team_data = {
        "team_name": "backend",
        "members": [
            {"user_id": "u1", "username": "Alice", "is_active": True},
            {"user_id": "u2", "username": "Bob", "is_active": True},
            {"user_id": "u3", "username": "Charlie", "is_active": True},
        ],
    }
    response = client.post("/team/add", json=team_data)
    assert response.status_code == 201
    return response.json()


@pytest.fixture()
def sample_team_large(client: TestClient) -> Dict:
    """
    Создаёт большую команду 'payments' с 5 участниками для сложных сценариев.
    """
    team_data = {
        "team_name": "payments",
        "members": [
            {"user_id": "p1", "username": "Author", "is_active": True},
            {"user_id": "p2", "username": "Reviewer1", "is_active": True},
            {"user_id": "p3", "username": "Reviewer2", "is_active": True},
            {"user_id": "p4", "username": "Reviewer3", "is_active": True},
            {"user_id": "p5", "username": "Reviewer4", "is_active": True},
        ],
    }
    response = client.post("/team/add", json=team_data)
    assert response.status_code == 201
    return response.json()


@pytest.fixture()
def sample_pr(client: TestClient, sample_team: Dict) -> Dict:
    """
    Создаёт тестовый PR от пользователя u1 (из sample_team).
    Автоматически назначает ревьюверов.

    Returns:
        Словарь с данными созданного PR
    """
    pr_data = {
        "pull_request_id": "pr-test-1",
        "pull_request_name": "Add feature X",
        "author_id": "u1",
    }
    response = client.post("/pullRequest/create", json=pr_data)
    assert response.status_code == 201
    return response.json()
