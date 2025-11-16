from typing import List
from pydantic import BaseModel, ConfigDict


class TeamMemberSchema(BaseModel):
    """Участник команды (согласно компоненту TeamMember в OpenAPI)"""

    model_config = ConfigDict(from_attributes=True)

    user_id: str
    username: str
    is_active: bool


class TeamSchema(BaseModel):
    """Команда с участниками (согласно компоненту Team в OpenAPI)"""

    model_config = ConfigDict(from_attributes=True)

    team_name: str
    members: List[TeamMemberSchema]


class TeamResponse(BaseModel):
    """Ответ при создании команды (POST /team/add)"""

    team: TeamSchema
