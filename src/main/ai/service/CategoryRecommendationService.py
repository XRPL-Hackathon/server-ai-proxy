from typing import Optional
import uuid
from bson import ObjectId

from src.main.ai.data.CategoryRecommendationRepository import CategoryRecommendationRepository
from src.main.ai.data.CategoryRecommendationQueue import CategoryRecommendationQueue
from src.main.ai.models.CategoryRecommendation import (
    CategoryRecommendationRequest,
    CategoryRecommendationResponse,
    CategoryRecommendationStatusResponse,
    CategoryRecommendationResultRequest
)


class CategoryRecommendationService:
    def __init__(self, repository: CategoryRecommendationRepository, queue: CategoryRecommendationQueue):
        self.repository = repository
        self.queue = queue

    def create_recommendation_request(self, request: CategoryRecommendationRequest, user_id: uuid.UUID) -> CategoryRecommendationResponse:
        # MongoDB에 저장 - ObjectId 자동 생성
        document = self.repository.create_recommendation_request(
            title=request.title,
            user_id=str(user_id)
        )
        
        # request_id는 MongoDB의 _id를 문자열로 변환
        request_id = str(document["_id"])
        
        # 메시지 발행
        self.queue.send_message(
            request_id=request_id,
            title=request.title,
            user_id=str(user_id)
        )
        
        return CategoryRecommendationResponse(request_id=request_id)

    def get_recommendation_status(self, request_id: str, user_id: uuid.UUID) -> Optional[CategoryRecommendationStatusResponse]:
        result = self.repository.get_recommendation_by_id(request_id, str(user_id))
        
        if not result:
            return None
            
        return CategoryRecommendationStatusResponse(
            request_id=str(result["_id"]),
            is_completed=result["is_completed"],
            predicted_category=result.get("predicted_category")
        )

    def update_recommendation_result(self, request_id: str, result: CategoryRecommendationResultRequest) -> Optional[CategoryRecommendationStatusResponse]:
        updated = self.repository.update_recommendation_result(
            request_id=request_id,
            predicted_category=result.predicted_category
        )
        
        if not updated:
            return None
            
        return CategoryRecommendationStatusResponse(
            request_id=str(updated["_id"]),
            is_completed=updated["is_completed"],
            predicted_category=updated.get("predicted_category")
        ) 