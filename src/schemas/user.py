from pydantic import BaseModel, ConfigDict


class UserSchema(BaseModel):
    """Пользователь (согласно компоненту User в OpenAPI)"""

    model_config = ConfigDict(from_attributes=True)

    user_id: str
    username: str
    team_name: str
    is_active: bool


class UserSetActiveSchema(BaseModel):
    """Запрос на изменение статуса активности пользователя (POST /users/setIsActive)"""

    user_id: str
    is_active: bool


class UserResponse(BaseModel):
    """Ответ при изменении статуса пользователя"""

    user: UserSchema
