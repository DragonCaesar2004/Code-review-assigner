from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator
import os


DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise RuntimeError("DATABASE_URL is not set")

# Для разных драйверов SQLAlchemy принимает разные параметры при создании engine.
# Если используется SQLite — используем совместимые параметры. Для in-memory SQLite
# необходимо явно указать StaticPool, чтобы одна и та же память была доступна
# между подключениями (полезно в тестах с shared in-memory DB).
url = make_url(DATABASE_URL)
if url.drivername and url.drivername.startswith("sqlite"):
    if ":memory:" in DATABASE_URL:
        engine = create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    else:
        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # Для production БД (Postgres и др.) используем настройки пула
    engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=10, max_overflow=20)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Зависимость для получения сессии БД."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
