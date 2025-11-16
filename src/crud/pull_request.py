"""
CRUD операции для Pull Request'ов
"""

from typing import List, Optional
from datetime import datetime, UTC
from sqlalchemy.orm import Session
from src.crud.base import BaseCRUD
from src.models.pull_request import PullRequest, PRStatus
from src.models.pr_reviewer import PRReviewer
from src.schemas.pull_request import PullRequestCreateSchema, PullRequestSchema


class PullRequestCRUD(
    BaseCRUD[PullRequest, PullRequestCreateSchema, PullRequestSchema]
):
    """CRUD операции для Pull Request'ов"""

    def __init__(self):
        super().__init__(model=PullRequest, pk_field="pull_request_id")

    def get_by_id(self, db: Session, pull_request_id: str) -> Optional[PullRequest]:
        """
        Получить PR по ID

        Args:
            db: Сессия БД
            pull_request_id: ID Pull Request

        Returns:
            Объект PullRequest или None
        """
        return self.get(db, pull_request_id)

    def create_pr(
        self, db: Session, pull_request_id: str, pull_request_name: str, author_id: str
    ) -> PullRequest:
        """
        Создать новый Pull Request

        Args:
            db: Сессия БД
            pull_request_id: ID Pull Request
            pull_request_name: Название Pull Request
            author_id: ID автора

        Returns:
            Созданный объект PullRequest
        """
        db_pr = PullRequest(
            pull_request_id=pull_request_id,
            pull_request_name=pull_request_name,
            author_id=author_id,
            status=PRStatus.OPEN,
            created_at=datetime.now(UTC),
        )
        db.add(db_pr)
        db.commit()
        db.refresh(db_pr)
        return db_pr

    def merge_pr(self, db: Session, pull_request_id: str) -> Optional[PullRequest]:
        """
        Установить статус PR в MERGED (идемпотентная операция)

        Args:
            db: Сессия БД
            pull_request_id: ID Pull Request

        Returns:
            Обновленный объект PullRequest или None если не найден
        """
        db_pr = self.get_by_id(db, pull_request_id)
        if db_pr:
            # Идемпотентность: если уже MERGED, просто возвращаем
            if db_pr.status != PRStatus.MERGED:
                db_pr.status = PRStatus.MERGED
                db_pr.merged_at = datetime.now(UTC)
                db.commit()
                db.refresh(db_pr)
        return db_pr

    def get_prs_by_reviewer(self, db: Session, reviewer_id: str) -> List[PullRequest]:
        """
        Получить все PR где пользователь назначен ревьювером

        Args:
            db: Сессия БД
            reviewer_id: ID ревьювера

        Returns:
            Список объектов PullRequest
        """
        return (
            db.query(PullRequest)
            .join(PRReviewer, PullRequest.pull_request_id == PRReviewer.pull_request_id)
            .filter(PRReviewer.reviewer_id == reviewer_id)
            .all()
        )

    def get_prs_by_author(self, db: Session, author_id: str) -> List[PullRequest]:
        """
        Получить все PR конкретного автора

        Args:
            db: Сессия БД
            author_id: ID автора

        Returns:
            Список объектов PullRequest
        """
        return db.query(PullRequest).filter(PullRequest.author_id == author_id).all()


# Singleton экземпляр для использования в приложении
pull_request_crud = PullRequestCRUD()
