from typing import List
from pydantic import BaseModel
from .pull_request import PullRequestShortSchema


class UserReviewsResponse(BaseModel):
    """Ответ на запрос списка PR для ревью (GET /users/getReview)"""

    user_id: str
    pull_requests: List[PullRequestShortSchema]
