"""
Сервис для назначения ревьюверов на Pull Request'ы
Содержит основную бизнес-логику выбора ревьюверов
"""

import random
from typing import List
from sqlalchemy.orm import Session
from src.crud import user_crud, pr_reviewer_crud
from src.models.pull_request import PullRequest
from src.services.exceptions import NoCandidateException


class ReviewerAssignmentService:
    """Бизнес-логика назначения ревьюверов"""

    def select_reviewers(
        self, db: Session, team_name: str, author_id: str, max_count: int = 2
    ) -> List[str]:
        """
        Выбрать до 2 случайных активных ревьюверов из команды автора

        Бизнес-правила:
        - Только активные участники (is_active=True)
        - Исключая автора PR
        - Случайный выбор
        - До 2 ревьюверов максимум
        - Если недостаточно кандидатов, назначаем сколько есть (0/1)

        Args:
            db: Сессия БД
            team_name: Имя команды
            author_id: ID автора (исключается из выбора)
            max_count: Максимальное количество ревьюверов (по умолчанию 2)

        Returns:
            Список ID выбранных ревьюверов (может быть пустым)
        """
        # Получаем активных участников команды, исключая автора
        candidates = user_crud.get_active_team_members(
            db, team_name=team_name, exclude_user_id=author_id
        )

        # Если нет кандидатов - возвращаем пустой список (не ошибка!)
        if not candidates:
            return []

        # Выбираем случайных ревьюверов (до max_count)
        selected_count = min(len(candidates), max_count)
        selected_reviewers = random.sample(candidates, selected_count)

        return [reviewer.user_id for reviewer in selected_reviewers]

    def assign_reviewers_to_pr(
        self, db: Session, pull_request_id: str, reviewer_ids: List[str]
    ) -> None:
        """
        Назначить список ревьюверов на PR

        Args:
            db: Сессия БД
            pull_request_id: ID Pull Request
            reviewer_ids: Список ID ревьюверов для назначения
        """
        for reviewer_id in reviewer_ids:
            pr_reviewer_crud.assign_reviewer(db, pull_request_id, reviewer_id)

    def find_replacement_reviewer(
        self, db: Session, old_reviewer_id: str, pr: PullRequest
    ) -> str:
        """
        Найти замену ревьюверу из его команды

        Бизнес-правила:
        - Замена ищется из команды ЗАМЕНЯЕМОГО ревьювера (не автора!)
        - Исключаем: автора PR, текущих ревьюверов (включая заменяемого), неактивных
        - Случайный выбор из доступных кандидатов

        Args:
            db: Сессия БД
            old_reviewer_id: ID ревьювера для замены
            pr: Объект PullRequest

        Returns:
            ID нового ревьювера

        Raises:
            NoCandidateException: Если нет доступных кандидатов
        """
        # Получаем команду заменяемого ревьювера
        old_reviewer = user_crud.get_by_id(db, old_reviewer_id)
        if not old_reviewer:
            raise NoCandidateException(f"Reviewer '{old_reviewer_id}' not found")

        # Получаем текущих ревьюверов PR
        current_reviewer_ids = pr_reviewer_crud.get_reviewer_ids(db, pr.pull_request_id)

        # Получаем активных участников команды заменяемого ревьювера
        candidates = user_crud.get_active_team_members(
            db, team_name=old_reviewer.team_name
        )

        # Фильтруем кандидатов: исключаем автора и текущих ревьюверов
        exclude_ids = set([pr.author_id] + current_reviewer_ids)
        available_candidates = [c for c in candidates if c.user_id not in exclude_ids]

        # Если нет доступных кандидатов - исключение
        if not available_candidates:
            raise NoCandidateException(
                f"No active replacement candidates in team '{old_reviewer.team_name}'"
            )

        # Случайный выбор
        new_reviewer = random.choice(available_candidates)
        return new_reviewer.user_id

    def reassign_reviewer(
        self,
        db: Session,
        pull_request_id: str,
        old_reviewer_id: str,
        new_reviewer_id: str,
    ) -> None:
        """
        Заменить ревьювера на PR

        Args:
            db: Сессия БД
            pull_request_id: ID Pull Request
            old_reviewer_id: ID старого ревьювера
            new_reviewer_id: ID нового ревьювера
        """
        # Удаляем старого ревьювера
        pr_reviewer_crud.remove_reviewer(db, pull_request_id, old_reviewer_id)

        # Назначаем нового ревьювера
        pr_reviewer_crud.assign_reviewer(db, pull_request_id, new_reviewer_id)


# Singleton экземпляр для использования в приложении
reviewer_assignment_service = ReviewerAssignmentService()
