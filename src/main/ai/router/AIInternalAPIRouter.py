from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from src.main.ai.di.dependencies import get_category_recommendation_service
from src.main.ai.models.CategoryRecommendation import CategoryRecommendationResultRequest, CategoryRecommendationStatusResponse
from src.main.ai.service.CategoryRecommendationService import CategoryRecommendationService


router = APIRouter(
    prefix="/ai-proxy",
    tags=["AI", "Internal"]
)


@router.post("/category-recommendations-results/{request_id}", response_model=CategoryRecommendationStatusResponse)
async def update_category_recommendation_result(
    request_id: str,
    request: CategoryRecommendationResultRequest,
    service: CategoryRecommendationService = Depends(get_category_recommendation_service)
):
    """
    (내부용) 자료 제목에 따른 추천 카테고리 조회 결과 저장
    """
    result = service.update_recommendation_result(request_id, request)
    
    if not result:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "status": 404,
                "message": "요청을 찾을 수 없습니다.",
                "detail": "존재하지 않는 ID입니다."
            }
        )
        
    return result
