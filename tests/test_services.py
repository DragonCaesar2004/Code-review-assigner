"""
Unit тесты для бизнес-логики (сервисов).

Best Practices:
- Тестируем изолированно сервисный слой
- Используем реальную БД сессию (in-memory SQLite)
- Проверяем граничные случаи и edge cases
- Тестируем все бизнес-правила из ТЗ
"""

import pytest
from sqlalchemy.orm import Session

from src.services.exceptions import (
    TeamExistsException,
    PRExistsException,
    PRMergedException,
    NotAssignedException,
    NoCandidateException,
    NotFoundException,
)
from src.services import team_service, user_service, pull_request_service
from src.schemas.team import TeamSchema, TeamMemberSchema


class TestTeamService:
    """Unit тесты для TeamService"""

    def test_create_team_with_members(self, db_session: Session):
        """Создание команды с участниками"""
        team_data = TeamSchema(
            team_name="test_team",
            members=[
                TeamMemberSchema(user_id="t1", username="User1", is_active=True),
                TeamMemberSchema(user_id="t2", username="User2", is_active=False),
            ],
        )

        result = team_service.create_team_with_members(db_session, team_data)

        assert result.team.team_name == "test_team"
        assert len(result.team.members) == 2

    def test_create_duplicate_team_raises_exception(self, db_session: Session):
        """Попытка создать дублирующуюся команду вызывает исключение"""
        team_data = TeamSchema(
            team_name="dup_team",
            members=[TeamMemberSchema(user_id="d1", username="D1", is_active=True)],
        )

        team_service.create_team_with_members(db_session, team_data)

        with pytest.raises(TeamExistsException) as exc_info:
            team_service.create_team_with_members(db_session, team_data)

        assert exc_info.value.code.value == "TEAM_EXISTS"

    def test_get_nonexistent_team_raises_exception(self, db_session: Session):
        """Получение несуществующей команды вызывает исключение"""
        with pytest.raises(NotFoundException) as exc_info:
            team_service.get_team_with_members(db_session, "nonexistent")

        assert exc_info.value.code.value == "NOT_FOUND"


class TestUserService:
    """Unit тесты для UserService"""

    def test_set_user_active_status(self, db_session: Session):
        """Изменение статуса активности пользователя"""
        # Сначала создаём пользователя через команду
        team_data = TeamSchema(
            team_name="user_test_team",
            members=[TeamMemberSchema(user_id="ut1", username="UT1", is_active=True)],
        )
        team_service.create_team_with_members(db_session, team_data)

        # Меняем статус
        result = user_service.set_user_active_status(db_session, "ut1", False)

        assert result.user.user_id == "ut1"
        assert result.user.is_active is False

    def test_set_nonexistent_user_active_raises_exception(self, db_session: Session):
        """Изменение статуса несуществующего пользователя вызывает исключение"""
        with pytest.raises(NotFoundException) as exc_info:
            user_service.set_user_active_status(db_session, "nonexistent", False)

        assert exc_info.value.code.value == "NOT_FOUND"


class TestPullRequestService:
    """Unit тесты для PullRequestService"""

    def test_create_pr_with_no_available_reviewers(self, db_session: Session):
        """
        Создание PR когда нет доступных ревьюверов.
        Граничный случай: команда из 1 человека (только автор)
        """
        # Создаём команду с 1 участником
        team_data = TeamSchema(
            team_name="solo_team",
            members=[
                TeamMemberSchema(user_id="solo1", username="Solo", is_active=True)
            ],
        )
        team_service.create_team_with_members(db_session, team_data)

        # Создаём PR
        result = pull_request_service.create_pr_with_reviewers(
            db_session, "pr-solo", "Solo PR", "solo1"
        )

        # Должно создаться без ревьюверов (0 reviewers OK согласно ТЗ)
        assert result.pr.pull_request_id == "pr-solo"
        assert len(result.pr.assigned_reviewers) == 0

    def test_create_pr_assigns_max_2_reviewers(self, db_session: Session):
        """
        Проверка что назначается максимум 2 ревьювера даже если в команде больше.
        """
        # Создаём команду с 5 участниками
        team_data = TeamSchema(
            team_name="big_team",
            members=[
                TeamMemberSchema(user_id=f"big{i}", username=f"Big{i}", is_active=True)
                for i in range(1, 6)
            ],
        )
        team_service.create_team_with_members(db_session, team_data)

        # Создаём PR от big1
        result = pull_request_service.create_pr_with_reviewers(
            db_session, "pr-big", "Big PR", "big1"
        )

        # Должно быть максимум 2 ревьювера
        assert len(result.pr.assigned_reviewers) <= 2
        # Автор не должен быть ревьювером
        assert "big1" not in result.pr.assigned_reviewers

    def test_merge_pr_idempotence(self, db_session: Session):
        """Проверка идемпотентности merge операции"""
        # Подготовка: создаём команду и PR
        team_data = TeamSchema(
            team_name="merge_team",
            members=[
                TeamMemberSchema(user_id="m1", username="M1", is_active=True),
                TeamMemberSchema(user_id="m2", username="M2", is_active=True),
            ],
        )
        team_service.create_team_with_members(db_session, team_data)

        pull_request_service.create_pr_with_reviewers(
            db_session, "pr-merge-test", "Merge Test", "m1"
        )

        # Первый merge
        result1 = pull_request_service.merge_pr(db_session, "pr-merge-test")
        assert result1.pr.status.value == "MERGED"
        merged_at_1 = result1.pr.mergedAt

        # Второй merge (идемпотентность)
        result2 = pull_request_service.merge_pr(db_session, "pr-merge-test")
        assert result2.pr.status.value == "MERGED"
        merged_at_2 = result2.pr.mergedAt

        # mergedAt должен остаться прежним
        assert merged_at_1 == merged_at_2

    def test_reassign_after_merge_raises_exception(self, db_session: Session):
        """Переназначение после merge должно вызывать исключение"""
        # Подготовка
        team_data = TeamSchema(
            team_name="reassign_team",
            members=[
                TeamMemberSchema(user_id="r1", username="R1", is_active=True),
                TeamMemberSchema(user_id="r2", username="R2", is_active=True),
                TeamMemberSchema(user_id="r3", username="R3", is_active=True),
            ],
        )
        team_service.create_team_with_members(db_session, team_data)

        pr_result = pull_request_service.create_pr_with_reviewers(
            db_session, "pr-reassign-test", "Test", "r1"
        )

        # Мерджим
        pull_request_service.merge_pr(db_session, "pr-reassign-test")

        # Пытаемся переназначить
        if pr_result.pr.assigned_reviewers:
            with pytest.raises(PRMergedException) as exc_info:
                pull_request_service.reassign_reviewer(
                    db_session, "pr-reassign-test", pr_result.pr.assigned_reviewers[0]
                )

            assert exc_info.value.code.value == "PR_MERGED"

    def test_reassign_not_assigned_reviewer_raises_exception(self, db_session: Session):
        """Переназначение пользователя, который не назначен, вызывает исключение"""
        # Подготовка
        team_data = TeamSchema(
            team_name="not_assigned_team",
            members=[
                TeamMemberSchema(user_id="na1", username="NA1", is_active=True),
                TeamMemberSchema(user_id="na2", username="NA2", is_active=True),
                TeamMemberSchema(user_id="na3", username="NA3", is_active=True),
            ],
        )
        team_service.create_team_with_members(db_session, team_data)

        pull_request_service.create_pr_with_reviewers(
            db_session, "pr-not-assigned", "Test", "na1"
        )

        # Пытаемся переназначить na1 (автор, точно не назначен ревьювером)
        with pytest.raises(NotAssignedException) as exc_info:
            pull_request_service.reassign_reviewer(db_session, "pr-not-assigned", "na1")

        assert exc_info.value.code.value == "NOT_ASSIGNED"
