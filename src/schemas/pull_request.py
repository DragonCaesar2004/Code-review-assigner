from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from enum import Enum


class PRStatus(str, Enum):
    """Статус Pull Request"""

    OPEN = "OPEN"
    MERGED = "MERGED"


class PullRequestCreateSchema(BaseModel):
    """Запрос на создание PR (POST /pullRequest/create)"""

    pull_request_id: str
    pull_request_name: str
    author_id: str


class PullRequestSchema(BaseModel):
    """Полная информация о PR (согласно компоненту PullRequest в OpenAPI)"""

    model_config = ConfigDict(from_attributes=True)

    pull_request_id: str
    pull_request_name: str
    author_id: str
    status: PRStatus
    assigned_reviewers: List[str] = Field(
        description="user_id назначенных ревьюверов (0..2)"
    )
    createdAt: Optional[datetime] = None
    mergedAt: Optional[datetime] = None


class PullRequestShortSchema(BaseModel):
    """Краткая информация о PR (согласно компоненту PullRequestShort в OpenAPI)"""

    model_config = ConfigDict(from_attributes=True)

    pull_request_id: str
    pull_request_name: str
    author_id: str
    status: PRStatus


class PullRequestMergeSchema(BaseModel):
    """Запрос на merge PR (POST /pullRequest/merge)"""

    pull_request_id: str


class PullRequestReassignSchema(BaseModel):
    """Запрос на переназначение ревьювера (POST /pullRequest/reassign)"""

    model_config = ConfigDict(populate_by_name=True)

    pull_request_id: str
    old_user_id: str


class PullRequestResponse(BaseModel):
    """Ответ при создании/изменении PR"""

    pr: PullRequestSchema


class PullRequestReassignResponse(BaseModel):
    """Ответ при переназначении ревьювера (POST /pullRequest/reassign)"""

    pr: PullRequestSchema
    replaced_by: str = Field(description="user_id нового ревьювера")
