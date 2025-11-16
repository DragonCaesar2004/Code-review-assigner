"""
API endpoints для работы с командами (Teams)
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from src.models.database import get_db
from src.schemas.team import TeamSchema, TeamResponse
from src.services import team_service

router = APIRouter(prefix="/team", tags=["Teams"])


@router.post("/add", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
def create_team(team_data: TeamSchema, db: Session = Depends(get_db)):
    """
    Создать команду с участниками (создаёт/обновляет пользователей)

    - **201**: Команда создана
    - **400**: Команда уже существует (TEAM_EXISTS)
    """
    return team_service.create_team_with_members(db, team_data)


@router.get("/get", response_model=TeamSchema, status_code=status.HTTP_200_OK)
def get_team(team_name: str, db: Session = Depends(get_db)):
    """
    Получить команду с участниками

    - **200**: Объект команды
    - **404**: Команда не найдена (NOT_FOUND)
    """
    return team_service.get_team_with_members(db, team_name)
