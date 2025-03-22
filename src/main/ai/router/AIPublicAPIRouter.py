from fastapi import APIRouter, Depends, HTTPException, status
import uuid

from src.main.auth.dependencies import get_current_user
from src.main.ai.di.dependencies import get_category_recommendation_service, get_file_duplicate_check_service
from src.main.ai.models.CategoryRecommendation import CategoryRecommendationRequest, CategoryRecommendationResponse, CategoryRecommendationStatusResponse
from src.main.ai.service.CategoryRecommendationService import CategoryRecommendationService
from src.main.ai.models.FileDuplicateCheck import FileDuplicateCheckStatusResponse, FileDuplicateCheckRequest, FileDuplicateCheckResponse
from src.main.ai.service.FileDuplicateCheckService import FileDuplicateCheckService


router = APIRouter(
    prefix="/ai",
    tags=["AI", "Public"]
)


@router.post("/category-recommendations", response_model=CategoryRecommendationResponse)
async def create_category_recommendation_request(
    request: CategoryRecommendationRequest,
    user_id: uuid.UUID = Depends(get_current_user),
    service: CategoryRecommendationService = Depends(get_category_recommendation_service)
):
    """
    자료 제목에 따른 추천 카테고리 요청
    """
    return service.create_recommendation_request(request, user_id)


@router.get("/category-recommendations/{request_id}", response_model=CategoryRecommendationStatusResponse)
async def get_category_recommendation_status(
    request_id: str,
    user_id: uuid.UUID = Depends(get_current_user),
    service: CategoryRecommendationService = Depends(get_category_recommendation_service)
):
    """
    자료 제목에 따른 추천 카테고리 조회
    """
    result = service.get_recommendation_status(request_id, user_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="요청을 찾을 수 없습니다. 존재하지 않는 ID입니다."
        )
        
    return result


@router.post("/file-duplicate-checks", response_model=FileDuplicateCheckResponse)
async def create_file_duplicate_check_request(
    request: FileDuplicateCheckRequest,
    service: FileDuplicateCheckService = Depends(get_file_duplicate_check_service)
):
    """
    업로드한 파일의 중복 검사 시작 요청
    """
    try:
        return service.create_duplicate_check_request(request)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="잘못된 요청입니다. 명세에 맞지 않은 요청입니다."
        )


@router.get("/file-duplicate-checks", response_model=FileDuplicateCheckStatusResponse)
async def get_file_duplicate_check_status(
    file_id: str,
    user_id: uuid.UUID = Depends(get_current_user),
    service: FileDuplicateCheckService = Depends(get_file_duplicate_check_service)
):
    """
    업로드한 파일의 중복 검사 결과 조회
    """
    result = service.get_duplicate_check_status(file_id, str(user_id))
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="요청을 찾을 수 없습니다. 존재하지 않는 ID입니다."
        )
        
    return result
