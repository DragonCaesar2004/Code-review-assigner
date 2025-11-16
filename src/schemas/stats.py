"""
Pydantic схемы для статистики
"""
from typing import Dict, List
from pydantic import BaseModel, ConfigDict, Field


class UserAssignmentStats(BaseModel):
    """Статистика назначений по пользователю."""
    model_config = ConfigDict(from_attributes=True)
    
    user_id: str = Field(description="ID пользователя")
    username: str = Field(description="Имя пользователя")
    total_assignments: int = Field(description="Общее количество назначений")
    active_assignments: int = Field(description="Количество активных (OPEN) PR")
    completed_assignments: int = Field(description="Количество завершённых (MERGED) PR")


class PRReviewerStats(BaseModel):
    """Статистика ревьюверов по PR."""
    model_config = ConfigDict(from_attributes=True)
    
    pull_request_id: str = Field(description="ID Pull Request")
    pull_request_name: str = Field(description="Название PR")
    author_id: str = Field(description="ID автора")
    status: str = Field(description="Статус PR (OPEN/MERGED)")
    reviewer_count: int = Field(description="Количество назначенных ревьюверов")
    reviewers: List[str] = Field(description="Список ID ревьюверов")


class OverallStats(BaseModel):
    """Общая статистика системы."""
    
    total_teams: int = Field(description="Всего команд")
    total_users: int = Field(description="Всего пользователей")
    active_users: int = Field(description="Активных пользователей")
    total_prs: int = Field(description="Всего PR")
    open_prs: int = Field(description="Открытых PR")
    merged_prs: int = Field(description="Смерженных PR")
    total_assignments: int = Field(description="Всего назначений ревьюверов")


class StatsResponse(BaseModel):
    """Полный ответ со статистикой."""
    
    user_stats: List[UserAssignmentStats] = Field(
        description="Статистика по пользователям"
    )
    pr_stats: List[PRReviewerStats] = Field(
        description="Статистика по PR"
    )
    overall: OverallStats = Field(
        description="Общая статистика"
    )
