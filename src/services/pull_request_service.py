"""
Сервис для работы с Pull Request'ами
"""

from typing import List
from sqlalchemy.orm import Session
from src.crud import pull_request_crud, user_crud, pr_reviewer_crud
from src.models.pull_request import PRStatus
from src.schemas.pull_request import (
    PullRequestSchema,
    PullRequestShortSchema,
    PullRequestResponse,
    PullRequestReassignResponse,
)
from src.schemas.review import UserReviewsResponse
from src.services.exceptions import (
    PRExistsException,
    NotFoundException,
    PRMergedException,
    NotAssignedException,
)
from src.services.reviewer_assignment_service import reviewer_assignment_service


class PullRequestService:
    """Бизнес-логика для Pull Request'ов"""

    def create_pr_with_reviewers(
        self, db: Session, pull_request_id: str, pull_request_name: str, author_id: str
    ) -> PullRequestResponse:
        """
        Создать PR и автоматически назначить до 2 ревьюверов

        Бизнес-правила:
        - PR с таким ID не должен существовать
        - Автор должен существовать
        - Автоматически назначить до 2 ревьюверов из команды автора
        - Статус OPEN, created_at = now()

        Args:
            db: Сессия БД
            pull_request_id: ID Pull Request
            pull_request_name: Название Pull Request
            author_id: ID автора

        Returns:
            PullRequestResponse с созданным PR

        Raises:
            PRExistsException: Если PR уже существует
            NotFoundException: Если автор не найден
        """
        # Проверка: PR не должен существовать
        if pull_request_crud.exists(db, pull_request_id):
            raise PRExistsException(pull_request_id)

        # Проверка: автор должен существовать
        author = user_crud.get_by_id(db, author_id)
        if not author:
            raise NotFoundException("Author", author_id)

        # Создаем PR
        db_pr = pull_request_crud.create_pr(
            db, pull_request_id, pull_request_name, author_id
        )

        # Выбираем ревьюверов из команды автора
        reviewer_ids = reviewer_assignment_service.select_reviewers(
            db, team_name=author.team_name, author_id=author_id, max_count=2
        )

        # Назначаем ревьюверов
        reviewer_assignment_service.assign_reviewers_to_pr(
            db, pull_request_id, reviewer_ids
        )

        # Перезагружаем PR с ревьюверами
        db.refresh(db_pr)

        # Формируем ответ с assigned_reviewers
        pr_schema = self._build_pr_schema(db, db_pr)
        return PullRequestResponse(pr=pr_schema)

    def merge_pr(self, db: Session, pull_request_id: str) -> PullRequestResponse:
        """
        Установить статус PR в MERGED (идемпотентная операция)

        Бизнес-правила:
        - PR должен существовать
        - Операция идемпотентная (повторный вызов не ошибка)
        - Устанавливаем status=MERGED, merged_at=now()

        Args:
            db: Сессия БД
            pull_request_id: ID Pull Request

        Returns:
            PullRequestResponse с обновленным PR

        Raises:
            NotFoundException: Если PR не найден
        """
        db_pr = pull_request_crud.merge_pr(db, pull_request_id)

        if not db_pr:
            raise NotFoundException("Pull Request", pull_request_id)

        # Формируем ответ с assigned_reviewers
        pr_schema = self._build_pr_schema(db, db_pr)
        return PullRequestResponse(pr=pr_schema)

    def reassign_reviewer(
        self, db: Session, pull_request_id: str, old_reviewer_id: str
    ) -> PullRequestReassignResponse:
        """
        Переназначить ревьювера на другого из его команды

        Бизнес-правила:
        - PR должен существовать
        - PR не должен быть в статусе MERGED
        - old_reviewer_id должен быть назначен на этот PR
        - Должны быть доступные кандидаты для замены
        - Замена ищется из команды заменяемого ревьювера

        Args:
            db: Сессия БД
            pull_request_id: ID Pull Request
            old_reviewer_id: ID ревьювера для замены

        Returns:
            PullRequestReassignResponse с обновленным PR и replaced_by

        Raises:
            NotFoundException: Если PR не найден
            PRMergedException: Если PR уже merged
            NotAssignedException: Если old_reviewer_id не назначен на этот PR
            NoCandidateException: Если нет доступных кандидатов
        """
        # Проверка: PR должен существовать
        db_pr = pull_request_crud.get_by_id(db, pull_request_id)
        if not db_pr:
            raise NotFoundException("Pull Request", pull_request_id)

        # Проверка: PR не должен быть MERGED
        if db_pr.status == PRStatus.MERGED:
            raise PRMergedException(pull_request_id)

        # Проверка: old_reviewer_id назначен на этот PR
        if not pr_reviewer_crud.is_assigned(db, pull_request_id, old_reviewer_id):
            raise NotAssignedException(old_reviewer_id, pull_request_id)

        # Находим замену из команды заменяемого ревьювера
        new_reviewer_id = reviewer_assignment_service.find_replacement_reviewer(
            db, old_reviewer_id, db_pr
        )

        # Выполняем переназначение
        reviewer_assignment_service.reassign_reviewer(
            db, pull_request_id, old_reviewer_id, new_reviewer_id
        )

        # Перезагружаем PR
        db.refresh(db_pr)

        # Формируем ответ
        pr_schema = self._build_pr_schema(db, db_pr)
        return PullRequestReassignResponse(pr=pr_schema, replaced_by=new_reviewer_id)

    def get_user_reviews(self, db: Session, user_id: str) -> UserReviewsResponse:
        """
        Получить список PR где пользователь назначен ревьювером

        Args:
            db: Сессия БД
            user_id: ID пользователя

        Returns:
            UserReviewsResponse со списком PR
        """
        # Получаем PR где user - ревьювер
        prs = pull_request_crud.get_prs_by_reviewer(db, user_id)

        # Преобразуем в PullRequestShort
        pr_shorts = [PullRequestShortSchema.model_validate(pr) for pr in prs]

        return UserReviewsResponse(user_id=user_id, pull_requests=pr_shorts)

    def _build_pr_schema(self, db: Session, db_pr) -> PullRequestSchema:
        """
        Построить PullRequestSchema с assigned_reviewers

        Args:
            db: Сессия БД
            db_pr: Объект PullRequest из БД

        Returns:
            PullRequestSchema с заполненным assigned_reviewers
        """
        # Получаем ID ревьюверов
        reviewer_ids = pr_reviewer_crud.get_reviewer_ids(db, db_pr.pull_request_id)

        # Создаем схему
        pr_dict = {
            "pull_request_id": db_pr.pull_request_id,
            "pull_request_name": db_pr.pull_request_name,
            "author_id": db_pr.author_id,
            "status": db_pr.status,
            "assigned_reviewers": reviewer_ids,
            "createdAt": db_pr.created_at,
            "mergedAt": db_pr.merged_at,
        }

        return PullRequestSchema(**pr_dict)


# Singleton экземпляр для использования в приложении
pull_request_service = PullRequestService()
