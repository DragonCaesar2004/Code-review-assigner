"""
CRUD операции для назначения ревьюверов (PRReviewer)
Специализированный класс без наследования от BaseCRUD из-за композитного ключа
"""

from typing import List, Optional
from datetime import datetime, UTC
from sqlalchemy.orm import Session
from src.models.pr_reviewer import PRReviewer


class PRReviewerCRUD:
    """CRUD операции для назначения ревьюверов на Pull Request'ы"""

    def assign_reviewer(
        self, db: Session, pull_request_id: str, reviewer_id: str
    ) -> PRReviewer:
        """
        Назначить ревьювера на PR

        Args:
            db: Сессия БД
            pull_request_id: ID Pull Request
            reviewer_id: ID ревьювера

        Returns:
            Созданный объект PRReviewer
        """
        db_assignment = PRReviewer(
            pull_request_id=pull_request_id,
            reviewer_id=reviewer_id,
            assigned_at=datetime.now(UTC),
        )
        db.add(db_assignment)
        db.commit()
        db.refresh(db_assignment)
        return db_assignment

    def remove_reviewer(
        self, db: Session, pull_request_id: str, reviewer_id: str
    ) -> bool:
        """
        Удалить назначение ревьювера с PR

        Args:
            db: Сессия БД
            pull_request_id: ID Pull Request
            reviewer_id: ID ревьювера

        Returns:
            True если удалено, False если не найдено
        """
        assignment = (
            db.query(PRReviewer)
            .filter(
                PRReviewer.pull_request_id == pull_request_id,
                PRReviewer.reviewer_id == reviewer_id,
            )
            .first()
        )

        if assignment:
            db.delete(assignment)
            db.commit()
            return True
        return False

    def get_reviewers(self, db: Session, pull_request_id: str) -> List[PRReviewer]:
        """
        Получить всех ревьюверов для конкретного PR

        Args:
            db: Сессия БД
            pull_request_id: ID Pull Request

        Returns:
            Список объектов PRReviewer
        """
        return (
            db.query(PRReviewer)
            .filter(PRReviewer.pull_request_id == pull_request_id)
            .all()
        )

    def get_reviewer_ids(self, db: Session, pull_request_id: str) -> List[str]:
        """
        Получить список ID ревьюверов для конкретного PR

        Args:
            db: Сессия БД
            pull_request_id: ID Pull Request

        Returns:
            Список ID ревьюверов (строки)
        """
        reviewers = self.get_reviewers(db, pull_request_id)
        return [r.reviewer_id for r in reviewers]

    def is_assigned(self, db: Session, pull_request_id: str, reviewer_id: str) -> bool:
        """
        Проверить, назначен ли пользователь ревьювером на этот PR

        Args:
            db: Сессия БД
            pull_request_id: ID Pull Request
            reviewer_id: ID ревьювера

        Returns:
            True если назначен, иначе False
        """
        return (
            db.query(PRReviewer)
            .filter(
                PRReviewer.pull_request_id == pull_request_id,
                PRReviewer.reviewer_id == reviewer_id,
            )
            .first()
        ) is not None

    def get_pr_count_by_reviewer(self, db: Session, reviewer_id: str) -> int:
        """
        Получить количество PR назначенных на конкретного ревьювера

        Args:
            db: Сессия БД
            reviewer_id: ID ревьювера

        Returns:
            Количество назначенных PR
        """
        return (
            db.query(PRReviewer).filter(PRReviewer.reviewer_id == reviewer_id).count()
        )


# Singleton экземпляр для использования в приложении
pr_reviewer_crud = PRReviewerCRUD()
