from datetime import datetime, timezone
from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.user import User
    from src.models.pull_request import PullRequest


class PRReviewer(Base):
    """Модель связи между PR и ревьювером (многие-ко-многим)."""

    __tablename__ = "pr_reviewers"

    # ID PR (часть составного первичного ключа)
    pull_request_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("pull_requests.pull_request_id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    )

    # ID ревьювера (часть составного первичного ключа)
    reviewer_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("users.user_id", ondelete="RESTRICT"),
        nullable=False,
        primary_key=True,
    )

    # Дата назначения ревьювера
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(timezone.utc), nullable=False
    )

    # Связь: PR к которому назначен ревьювер
    pull_request: Mapped["PullRequest"] = relationship(
        "PullRequest", back_populates="reviewer_assignments"
    )

    # Связь: ревьювер
    reviewer: Mapped["User"] = relationship("User", back_populates="review_assignments")
