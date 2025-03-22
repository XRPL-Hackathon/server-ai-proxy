from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from src.main.ai.di.dependencies import get_category_recommendation_service, get_file_duplicate_check_service
from src.main.ai.models.CategoryRecommendation import CategoryRecommendationResultRequest, CategoryRecommendationStatusResponse
from src.main.ai.service.CategoryRecommendationService import CategoryRecommendationService
from src.main.ai.models.FileDuplicateCheck import FileDuplicateCheckStatusResponse, FileDuplicateCheckEmbeddingsRequest
from src.main.ai.service.FileDuplicateCheckService import FileDuplicateCheckService


router = APIRouter(
    prefix="/ai-proxy",
    tags=["AI", "Internal"]
)


@router.post("/category-recommendation-results/{request_id}", response_model=CategoryRecommendationStatusResponse)
async def update_category_recommendation_result(
    request_id: str,
    request: CategoryRecommendationResultRequest,
    service: CategoryRecommendationService = Depends(get_category_recommendation_service)
):
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


@router.post("/file-duplicate-check-embeddings", response_model=FileDuplicateCheckStatusResponse)
async def update_file_duplicate_check_result(
    request: FileDuplicateCheckEmbeddingsRequest,
    service: FileDuplicateCheckService = Depends(get_file_duplicate_check_service)
):
    """
    업로드한 파일의 중복 검사 결과 업데이트
    """
    result = service.update_duplicate_check_result(request.request_id, request)
    
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
