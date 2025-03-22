from pydantic import BaseModel, Field
import uuid
from typing import Optional


class CategoryRecommendationRequest(BaseModel):
    title: str


class CategoryRecommendationResponse(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))


class CategoryRecommendationStatusResponse(BaseModel):
    request_id: str
    is_completed: bool
    predicted_category: Optional[str] = None


class CategoryRecommendationResultRequest(BaseModel):
    request_id: str
    predicted_category: str 