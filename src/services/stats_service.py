"""
Сервис для получения статистики по назначениям ревьюверов
"""
from typing import List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.models.pr_reviewer import PRReviewer
from src.models.pull_request import PullRequest
from src.models.user import User
from src.models.team import Team
from src.schemas.stats import (
    UserAssignmentStats,
    PRReviewerStats,
    OverallStats,
    StatsResponse
)


class StatsService:
    """Сервис для работы со статистикой."""
    
    def __init__(self, db: AsyncSession):
        """
        Инициализация сервиса статистики.
        
        Args:
            db: Асинхронная сессия БД
        """
        self.db = db
    
    async def get_user_assignment_stats(self) -> List[UserAssignmentStats]:
        """
        Получить статистику назначений по всем пользователям.
        
        Returns:
            Список статистики по пользователям
        """
        # Получаем всех пользователей с их назначениями
        query = (
            select(
                User.user_id,
                User.username,
                func.count(PRReviewer.pull_request_id).label('total_assignments'),
                func.count(
                    func.nullif(
                        func.cast(PullRequest.status == 'OPEN', func.Integer()),
                        0
                    )
                ).label('active_assignments'),
                func.count(
                    func.nullif(
                        func.cast(PullRequest.status == 'MERGED', func.Integer()),
                        0
                    )
                ).label('completed_assignments')
            )
            .outerjoin(PRReviewer, User.user_id == PRReviewer.reviewer_id)
            .outerjoin(PullRequest, PRReviewer.pull_request_id == PullRequest.pull_request_id)
            .group_by(User.user_id, User.username)
            .order_by(func.count(PRReviewer.pull_request_id).desc())
        )
        
        result = await self.db.execute(query)
        rows = result.all()
        
        return [
            UserAssignmentStats(
                user_id=row.user_id,
                username=row.username,
                total_assignments=row.total_assignments or 0,
                active_assignments=row.active_assignments or 0,
                completed_assignments=row.completed_assignments or 0
            )
            for row in rows
        ]
    
    async def get_pr_reviewer_stats(self) -> List[PRReviewerStats]:
        """
        Получить статистику ревьюверов по всем PR.
        
        Returns:
            Список статистики по PR
        """
        # Получаем все PR с загруженными ревьюверами
        query = (
            select(PullRequest)
            .options(joinedload(PullRequest.reviewers))
            .order_by(PullRequest.created_at.desc())
        )
        
        result = await self.db.execute(query)
        prs = result.unique().scalars().all()
        
        return [
            PRReviewerStats(
                pull_request_id=pr.pull_request_id,
                pull_request_name=pr.pull_request_name,
                author_id=pr.author_id,
                status=pr.status,
                reviewer_count=len(pr.reviewers),
                reviewers=[reviewer.reviewer_id for reviewer in pr.reviewers]
            )
            for pr in prs
        ]
    
    async def get_overall_stats(self) -> OverallStats:
        """
        Получить общую статистику системы.
        
        Returns:
            Общая статистика
        """
        # Подсчитываем команды
        teams_query = select(func.count(Team.team_name))
        total_teams = await self.db.scalar(teams_query) or 0
        
        # Подсчитываем пользователей
        users_query = select(func.count(User.user_id))
        total_users = await self.db.scalar(users_query) or 0
        
        active_users_query = select(func.count(User.user_id)).where(User.is_active == True)
        active_users = await self.db.scalar(active_users_query) or 0
        
        # Подсчитываем PR
        prs_query = select(func.count(PullRequest.pull_request_id))
        total_prs = await self.db.scalar(prs_query) or 0
        
        open_prs_query = select(func.count(PullRequest.pull_request_id)).where(
            PullRequest.status == 'OPEN'
        )
        open_prs = await self.db.scalar(open_prs_query) or 0
        
        merged_prs_query = select(func.count(PullRequest.pull_request_id)).where(
            PullRequest.status == 'MERGED'
        )
        merged_prs = await self.db.scalar(merged_prs_query) or 0
        
        # Подсчитываем назначения
        assignments_query = select(func.count(PRReviewer.id))
        total_assignments = await self.db.scalar(assignments_query) or 0
        
        return OverallStats(
            total_teams=total_teams,
            total_users=total_users,
            active_users=active_users,
            total_prs=total_prs,
            open_prs=open_prs,
            merged_prs=merged_prs,
            total_assignments=total_assignments
        )
    
    async def get_combined_stats(self) -> StatsResponse:
        """
        Получить полную статистику (комбинированную).
        
        Returns:
            Полный ответ со всеми видами статистики
        """
        user_stats = await self.get_user_assignment_stats()
        pr_stats = await self.get_pr_reviewer_stats()
        overall = await self.get_overall_stats()
        
        return StatsResponse(
            user_stats=user_stats,
            pr_stats=pr_stats,
            overall=overall
        )
