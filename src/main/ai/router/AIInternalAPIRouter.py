from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from src.main.ai.di.dependencies import get_category_recommendation_service, get_file_duplicate_check_service
from src.main.ai.models.CategoryRecommendation import CategoryRecommendationResultRequest, CategoryRecommendationStatusResponse
from src.main.ai.service.CategoryRecommendationService import CategoryRecommendationService
from src.main.ai.models.FileDuplicateCheck import FileDuplicateCheckStatusResponse, FileDuplicateCheckEmbeddingsRequest, FileDuplicateCheckRequest, FileDuplicateCheckResponse, FileDuplicateCheckResultRequest
from src.main.ai.service.FileDuplicateCheckService import FileDuplicateCheckService


router = APIRouter(
    prefix="/ai-proxy",
    tags=["AI", "Internal"]
)


@router.post("/category-recommendation-results", response_model=dict)
async def update_category_recommendation_result(
    request: CategoryRecommendationResultRequest,
    service: CategoryRecommendationService = Depends(get_category_recommendation_service)
):
    result = service.update_recommendation_result(request.request_id, request)
    
    if not result:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "detail": "요청을 찾을 수 없습니다. 존재하지 않는 ID입니다."
            }
        )
        
    return {"success": True}


@router.post("/file-duplicate-checks", response_model=FileDuplicateCheckResponse)
async def create_file_duplicate_check(
    request: FileDuplicateCheckRequest,
    service: FileDuplicateCheckService = Depends(get_file_duplicate_check_service)
):
    result = service.create_duplicate_check_request(request)
    return result


@router.post("/file-duplicate-check-embeddings", response_model=dict)
async def update_file_duplicate_check_result(
    request: FileDuplicateCheckResultRequest,
    service: FileDuplicateCheckService = Depends(get_file_duplicate_check_service)
):
    result = service.update_duplicate_check_result(request.request_id, request.is_duplicated)
    
    if not result:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "status": 404,
                "message": "요청을 찾을 수 없습니다.",
                "detail": "존재하지 않는 ID입니다."
            }
        )
    
    # 요청 정보 조회
    check = service.repository.get_duplicate_check_by_id(request.request_id)
    
    return {
        "request_id": request.request_id,
        "file_id": check["file_id"],
        "is_completed": check["is_completed"],
        "is_duplicated": check["is_duplicated"]
    }
