"""
API эндпоинты для получения статистики
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.database import get_db
from src.services.stats_service import StatsService
from src.schemas.stats import (
    StatsResponse,
    UserAssignmentStats,
    PRReviewerStats,
    OverallStats
)


router = APIRouter(prefix="/stats", tags=["Statistics"])


@router.get(
    "/reviewers",
    response_model=List[UserAssignmentStats],
    summary="Статистика назначений по ревьюверам"
)
async def get_reviewer_statistics(
    db: AsyncSession = Depends(get_db)
) -> List[UserAssignmentStats]:
    """
    Получить статистику назначений по каждому ревьюверу
    (количество PR, на которые был назначен каждый пользователь).
    """
    service = StatsService(db)
    return await service.get_user_assignment_stats()


@router.get(
    "/pull-requests",
    response_model=List[PRReviewerStats],
    summary="Статистика ревьюверов по PR"
)
async def get_pr_statistics(
    db: AsyncSession = Depends(get_db)
) -> List[PRReviewerStats]:
    """
    Получить статистику ревьюверов по каждому PR
    (сколько ревьюверов назначено на каждый PR).
    """
    service = StatsService(db)
    return await service.get_pr_reviewer_stats()


@router.get(
    "/overall",
    response_model=OverallStats,
    summary="Общая статистика системы"
)
async def get_overall_statistics(
    db: AsyncSession = Depends(get_db)
) -> OverallStats:
    """
    Получить общую статистику системы
    (количество команд, пользователей, PR, назначений).
    """
    service = StatsService(db)
    return await service.get_overall_stats()


@router.get(
    "",
    response_model=StatsResponse,
    summary="Получить полную статистику"
)
async def get_full_statistics(
    db: AsyncSession = Depends(get_db)
) -> StatsResponse:
    """
    Получить комбинированную статистику: по ревьюверам, по PR и общую.
    """
    service = StatsService(db)
    return await service.get_combined_stats()
