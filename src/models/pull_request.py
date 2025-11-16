from datetime import datetime, timezone
from sqlalchemy import String, ForeignKey, Enum as SQLEnum, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional, TYPE_CHECKING
import enum

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.user import User
    from src.models.pr_reviewer import PRReviewer


class PRStatus(str, enum.Enum):
    OPEN = "OPEN"
    MERGED = "MERGED"


class PullRequest(Base):
    __tablename__ = "pull_requests"

    # Первичный ключ согласно API спецификации
    pull_request_id: Mapped[str] = mapped_column(
        String(255), primary_key=True, index=True
    )

    # Название PR (pull_request_name в API)
    pull_request_name: Mapped[str] = mapped_column(String(500), nullable=False)

    # Автор PR
    author_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("users.user_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    # Статус PR: OPEN или MERGED
    status: Mapped[PRStatus] = mapped_column(
        SQLEnum(PRStatus, native_enum=False),
        default=PRStatus.OPEN,
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(timezone.utc), nullable=False
    )

    merged_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    author: Mapped["User"] = relationship(
        "User", back_populates="authored_pull_requests", foreign_keys=[author_id]
    )

    reviewer_assignments: Mapped[List["PRReviewer"]] = relationship(
        "PRReviewer",
        back_populates="pull_request",
    )
