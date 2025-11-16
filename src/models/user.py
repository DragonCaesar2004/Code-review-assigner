from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, TYPE_CHECKING

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.team import Team
    from src.models.pull_request import PullRequest
    from src.models.pr_reviewer import PRReviewer


class User(Base):

    __tablename__ = "users"

    # Первичный ключ согласно API спецификации
    user_id: Mapped[str] = mapped_column(String(255), primary_key=True, index=True)

    username: Mapped[str] = mapped_column(String(255), nullable=False)

    team_name: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("teams.team_name", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    team: Mapped["Team"] = relationship("Team", back_populates="members")

    # Связь: pull requests созданные этим пользователем
    authored_pull_requests: Mapped[List["PullRequest"]] = relationship(
        "PullRequest", back_populates="author", foreign_keys="PullRequest.author_id"
    )

    review_assignments: Mapped[List["PRReviewer"]] = relationship(
        "PRReviewer", back_populates="reviewer"
    )
