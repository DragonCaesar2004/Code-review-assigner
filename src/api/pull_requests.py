"""
API endpoints для работы с Pull Request'ами
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from src.models.database import get_db
from src.schemas.pull_request import (
    PullRequestCreateSchema,
    PullRequestMergeSchema,
    PullRequestReassignSchema,
    PullRequestResponse,
    PullRequestReassignResponse,
)
from src.services import pull_request_service

router = APIRouter(prefix="/pullRequest", tags=["PullRequests"])


@router.post(
    "/create", response_model=PullRequestResponse, status_code=status.HTTP_201_CREATED
)
def create_pull_request(data: PullRequestCreateSchema, db: Session = Depends(get_db)):
    """
    Создать PR и автоматически назначить до 2 ревьюверов из команды автора

    - **201**: PR создан
    - **404**: Автор/команда не найдены (NOT_FOUND)
    - **409**: PR уже существует (PR_EXISTS)
    """
    return pull_request_service.create_pr_with_reviewers(
        db, data.pull_request_id, data.pull_request_name, data.author_id
    )


@router.post(
    "/merge", response_model=PullRequestResponse, status_code=status.HTTP_200_OK
)
def merge_pull_request(data: PullRequestMergeSchema, db: Session = Depends(get_db)):
    """
    Пометить PR как MERGED (идемпотентная операция)

    - **200**: PR в состоянии MERGED
    - **404**: PR не найден (NOT_FOUND)
    """
    return pull_request_service.merge_pr(db, data.pull_request_id)


@router.post(
    "/reassign",
    response_model=PullRequestReassignResponse,
    status_code=status.HTTP_200_OK,
)
def reassign_reviewer(data: PullRequestReassignSchema, db: Session = Depends(get_db)):
    """
    Переназначить конкретного ревьювера на другого из его команды

    - **200**: Переназначение выполнено
    - **404**: PR или пользователь не найден (NOT_FOUND)
    - **409**: Нарушение доменных правил переназначения:
      - PR_MERGED: Нельзя менять после MERGED
      - NOT_ASSIGNED: Пользователь не был назначен ревьювером
      - NO_CANDIDATE: Нет доступных кандидатов
    """
    return pull_request_service.reassign_reviewer(
        db, data.pull_request_id, data.old_user_id
    )
